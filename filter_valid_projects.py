#!/usr/bin/python
# -*- coding: utf-8 -*-


import pandas as pd

import untangle, urllib2, datetime


CONGRESS_URL = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicao?tipo=%s&numero=%s&ano=%s'

class ProjectFetcher():

	def __init__(self, pType, pId, year):
		self.pType = pType
		self.pId = pId
		self.year = year


	def getURL(self):
		return CONGRESS_URL % (self.pType, self.pId, self.year)


	def fetchContent(self):
		response = urllib2.urlopen(self.getURL())
		self.contentObj = untangle.parse(response.read())

		validProjects = list()
		for voting in self.contentObj.proposicao.Votacoes.Votacao:
			dateObj = datetime.datetime.strptime(voting['Data'], '%d/%m/%Y')
			if dateObj.year == 2015:
				validProjects.append(voting['ObjVotacao'])
			else:
				print 'Fitering out invalid (year < 2015): ' + voting['ObjVotacao']

		return validProjects


allProjects_df = pd.read_csv('voted_projects.csv', sep=';', encoding='utf-8')
uniqueProjects_df = pd.unique(allProjects_df[ ['pType', 'pId', 'pYear'] ].values)

filteredProjects_df = pd.DataFrame(columns=['pType', 'pId', 'year', 'subject'])
for project in uniqueProjects_df:
	pType, pId, year = project[0], project[1], project[2]
	fetcher = ProjectFetcher(pType, pId, year)
	validSubjects = fetcher.fetchContent()
	for subject in validSubjects:
		filteredProjects_df = filteredProjects_df.append({ 'pType': pType, 'pId': pId,
														'year': year, 'subject': subject },
														ignore_index=True)

filteredProjects_df.to_csv('filtered_projects.csv', sep=';', index=False, encoding='utf-8', float_format='%.0f')

