#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle, os.path

# from py2neo import ServiceRoot

# from py2neo.packages.httpstream import http
# http.socket_timeout = 9999

from graph_tool.all import *


class Neo4jPersistence():

	def __init__(self):
		neo4jUri = 'http://localhost:7474/'
		self.graph = ServiceRoot(neo4jUri).graph

	def createCoVotingNetwork(self):
		query = 'MATCH (c1:Congressmen)-[r1:VOTES]->(v1:Votings)<-[r2:VOTES]-(c2:Congressmen)\
				 WHERE r1.position = r2.position AND c1.name <> c2.name\
				 WITH c1, c2 AS other, COUNT(v1) AS intersection\
				 MATCH (c1:Congressmen)-[r3:VOTES]->(v2:Votings)\
				 WITH other, c1 AS original, intersection, COUNT(v2) AS count_original\
				 MATCH (other:Congressmen)-[r4:VOTES]->(v3:Votings)\
				 RETURN original, other, toFloat(intersection) / toFloat(count_original + COUNT(v3)) AS jac\
				 ORDER BY jac DESC'
		
		records = []
		for record in self.graph.cypher.execute(query):
			original_str = '%s (%s-%s)' %(record['original']['name'], \
										  record['original']['party'],\
										  record['original']['state'])
			other_str = '%s (%s-%s)' %(record['other']['name'], \
									   record['other']['party'],\
									   record['other']['state'])
			weight = record['jac']
			records.append([original_str, other_str, weight])

		if len(records):
			pickle.dump(records, open('covoting_net.p','wb'))
			

	def createCoDonatorsNetwork(self):
		query = 'MATCH (c:Congressmen)-[:VOTES]->(v:Votings) RETURN DISTINCT c.cId, c.name AS name'
		elected_only = list()
		for record in self.graph.cypher.execute(query):
			elected_only.append(record['c.cId'])
		
		print len(elected_only)

		records = []
		for cId1 in elected_only:
			print records

			for cId2 in elected_only:
				if cId2 == cId1:
					continue

				query = "MATCH (c1:Congressmen {cId : '%s'})<-[r1:DONATES]-(d1:Donators)\
						 -[r2:DONATES]->(c2:Congressmen {cId : '%s'})\
						 WITH c1, c2 AS other, COUNT(d1) AS intersection\
						 MATCH (c1:Congressmen)<-[r3:DONATES]-(d2:Donators)\
						 WITH other, c1 AS original, intersection, COUNT(d2) AS count_original\
						 MATCH (other:Congressmen)<-[r4:DONATES]-(d3:Donators)\
						 RETURN original, other, toFloat(intersection) / toFloat(count_original + COUNT(d3))\
						 AS jac" %(cId1, cId2)

				for record in self.graph.cypher.execute(query):
					original_str = '%s (%s-%s)' %(record['original']['name'], \
												  record['original']['party'],\
												  record['original']['state'])
					other_str = '%s (%s-%s)' %(record['other']['name'], \
											   record['other']['party'],\
											   record['other']['state'])
					weight = record['jac']
					records.append([original_str, other_str, weight])

		if len(records):
				pickle.dump(records, open('codonators_net.p','wb'))


if not os.path.exists('codonators_net.p') and not os.path.exists('covoting_net.p'):
	n4jp = Neo4jPersistence()
	n4jp.createCoVotingNetwork()
	n4jp.createCoDonatorsNetwork()


g = Graph()
congressmen_to_GT = dict()
GT_to_congressmen = dict()

for PICKLE_FILE in [ 'covoting_net.p', 'codonators_net.p' ]:
	print '****************'
	print '* %s' %PICKLE_FILE
	print '****************'

	with open('codonators_net.p') as f_codonators:
		for record in pickle.load(f_codonators):
			# print record

			c1 = record[0]
			if c1 not in congressmen_to_GT:
				v = g.add_vertex()
				GT_id = g.vertex_index[v]
				congressmen_to_GT[c1] = GT_id
				GT_to_congressmen[GT_id] = c1

			c2 = record[1]
			if c2 not in congressmen_to_GT:
				v = g.add_vertex()
				GT_id = g.vertex_index[v]
				congressmen_to_GT[c2] = GT_id
				GT_to_congressmen[GT_id] = c2

			g.add_edge(congressmen_to_GT[c1], congressmen_to_GT[c2], record[2])

		vertices_count = g.num_vertices()
		print 'Number of vertices: %s' %vertices_count
		edges_count = g.num_edges()
		print 'Number of edges: %s' %edges_count

		density = float(edges_count)
		if not g.is_directed():
			density += float(edges_count)
		density = density / float( vertices_count * (vertices_count - 1) )
		print 'Density is: %s' %density

		vertex_deg_hist = vertex_hist(g, 'total')
		vertex_deg_values = vertex_deg_hist[1]
		print 'Maximum degree is: %s' %max(vertex_deg_values)
		print 'Minimum degree is: %s' %min(vertex_deg_values)
		print 'Average degree is: %s' %vertex_average(g, 'total')[0]

		components = label_components(g)[1]
		components_count = len(components)
		print 'Number of components: %s' %components_count
		max_component = max(components) / float(vertices_count)
		print 'Maximum component is: %s' %(max_component * 100.00)

		glob_clustering = global_clustering(g)[0]
		print 'Global clustering is: %s' %glob_clustering

		loc_clustering = local_clustering(g, undirected=(not g.is_directed())).get_array()
		print 'Average local clustering is: %s' %( sum(loc_clustering) / len(loc_clustering) )

		distance_hist = distance_histogram(g)
		average_dist = 0.0
		total_count = 0.0
		for count, value in zip(distance_hist[0], distance_hist[1]):
			average_dist += count * value
			total_count += count
		print 'Average distance is: %s' %(average_dist / total_count)

		diameter = pseudo_diameter(g)
		print 'Pseudo diameter is: %s' %(diameter[0])


# def get_sorted(values_array, normalization_factor=None):
# 	values_dict = dict()
# 	for i,value in enumerate(values_array):
# 		if not normalization_factor:
# 			values_dict[i] = value
# 		else:
# 			values_dict[i] = value / float(normalization_factor)
# 	return sorted(values_dict.items(), key=lambda x: x[1], reverse=True)


# betweennesses = betweenness(g)
# sorted_betweennesses = get_sorted(betweennesses[0].get_array())
# top_betweennesses = ','.join(('%s:%.5f') %(GT_to_congressmen[ t[0] ],t[1]) for t in sorted_betweennesses[:50])
# print top_betweennesses
