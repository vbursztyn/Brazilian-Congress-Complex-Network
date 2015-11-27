import requests
import pickle
import xml.etree.ElementTree as ET
import pandas as pd

# TODO: fix encoding


def load_votations(cached = True):

    if cached == True:
        with open('data.pck', 'rb') as fp:
            return pickle.load(fp)

    # if not cached

    votations = pd.DataFrame.from_csv('voted_projects.csv', sep=';').values.tolist()
    votations = [map(str, votation) for votation in votations]

    amends = []
    parties_votings = []
    congressmen_votings = []
    congressmen = {}

    collected_projects = []
    for pType, pId, pYear in votations:

        if [pType, pId, pYear] in collected_projects:
            continue
        else:
            print 'collecting', pType, pId, pYear
            collected_projects.append([pType, pId, pYear])

        url = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/' + \
                'ObterVotacaoProposicao?tipo=%s&numero=%s&ano=%s' % (pType, pId, pYear)
        page = requests.get(url)
        xml = page.content
        tree = ET.fromstring(xml)

        for xml_data in tree[3]:

            amend = {}
            party_voting = {}
            congressman_voting = {}

            # collenct amend info
            amend['date'] = xml_data.attrib['Data']
            if amend['date'].split('/')[-1] != '2015':
                continue
            amend['desc'] = xml_data.attrib['ObjVotacao'] + '--' \
                            + xml_data.attrib['Resumo']

            try:
                # collects congressmen voting and personal info
                for congressman in xml_data[1]:
                    congressman_voting[ congressman.attrib['Nome'] ] = \
                    congressman.attrib['Voto'].replace(' ','')

                    if congressman.attrib['Nome'] not in congressmen.keys():
                        congressmen[ congressman.attrib['Nome'] ] = \
                        [ congressman.attrib['Partido'].replace(' ',''),
                         congressman.attrib['UF'] ]

                # collects party orientation
                for party in xml_data[0]:
                        party_voting[ party.attrib['Sigla'] ] = \
                        party.attrib['orientacao'].replace(' ','')

            except Exception, e:
                print 'ERROR: ', str(e)

            amends.append( amend )
            congressmen_votings.append( congressman_voting )
            parties_votings.append( party_voting )

    df_amends = pd.DataFrame(amends)
    df_parties_votings = pd.DataFrame(parties_votings)
    df_congressmen_votings = pd.DataFrame(congressmen_votings)
    df_congressmen = pd.DataFrame(
        zip(congressmen.keys(), zip(*congressmen.values())[0], zip(*congressmen.values())[1]),
        columns = ['congressman', 'party', 'state'] ).set_index('congressman')

    with open('data.pck', 'wb') as fp:
        pickle.dump( (df_amends, df_parties_votings, df_congressmen_votings, df_congressmen), fp )

    return (df_amends, df_parties_votings, df_congressmen_votings, df_congressmen)


(amends, parties_votings, congressmen_votings, congressmen) = load_votations(cached = True)
