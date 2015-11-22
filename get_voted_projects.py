import requests
import untangle
import pandas as pd


table = []
year = '2015'
tipos = ['PEC', 'PL', 'PLP', 'MPV']

for tipo in tipos:

    url = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/' + \
            'ListarProposicoesVotadasEmPlenario?ano=2015&tipo=%s' % tipo

    page = requests.get(url)
    xml = page.content

    doc = untangle.parse(xml)


    for project in doc.proposicoes.proposicao:
        table.append([ project.codProposicao.cdata,
                      project.nomeProposicao.cdata.split()[0],
                      project.nomeProposicao.cdata.split()[1].split('/')[0],
                      project.nomeProposicao.cdata.split('/')[1],
                      project.dataVotacao.cdata ])

df = pd.DataFrame(table, columns = ['pCode', 'pType', 'pId', 'pYear', 'votingDate'])

with open('voted_projects.csv', 'w') as fp:
  fp.write( df[['pType', 'pId', 'pYear']].to_csv(sep=';') )
