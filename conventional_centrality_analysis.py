import graph_tool.all as gt
import pandas as pd
import os
import pickle

(amends, parties_votings, congressmen_votings, congressmen) =  pd.read_pickle('data.pck')

# merge add cabecas column

df = pd.merge(pd.read_csv('cabecas.csv', sep=';').reset_index(), congressmen_votings.transpose().reset_index(), 
               left_on='TSE' ,right_on='index', how='right')

# build network

g = gt.Graph()

name_to_vertex = {}
vertex_to_name = {}
diap = []
edges = {}

# add vertices

data = df3.values.tolist()

for line in data:
    name = line[4]
    diap.append(line[3])
    name_to_vertex[name] = g.add_vertex()
    vertex_to_name[name_to_vertex[name]] = name
      
# add edges

weight_map = g.new_edge_property('double')

for idx1 in range(len(data)):
    for idx2 in range(idx1+1, len(data)):
        dep1, dep2 = data[idx1], data[idx2]
        e = g.add_edge(name_to_vertex[dep1[4]], name_to_vertex[dep2[4]])

        # calculates similarity
        try:
            common_votes = sum([ dep1[idx] == dep2[idx] for idx in range(5, len(data[1])) ])

            weight_map[e] = 1. * common_votes / len(dep1[5:])
            edges[(dep1[4],dep2[4])] = [weight_map[e], dep1, dep2] # adds for debuging

        except Exception, e:
            print str(e)


# conventional centrality analysis

# degree 
degree = g.degree_property_map('total', weight = weight_map)

# vertice betweeness
betweeness = gt.betweenness(g, weight = weight_map)

# closeness
closeness = gt.closeness(g, weight = weight_map)

# Katz
katz = gt.katz(g, weight = weight_map)

# Pagerank
pagerank = gt.pagerank(g, weight = weight_map)


metrics = ['name', 'diap', 'betweenness', 'closeness', 'degree', 'katz', 'pagerank']
df = pd.DataFrame(zip(vertex_to_name.values(), diap, degree.a.tolist(), betweeness[0].a.tolist(), closeness.a.tolist(), katz.a.tolist(), 
                      pagerank.a.tolist()), columns = metrics)

df.sort('Pagerank', ascending=True)[:30]
