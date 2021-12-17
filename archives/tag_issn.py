import requests
import csv

def find_publications(idHal, field, increment=0):
    articles = []
    flags = 'docid,halId_s,title_s,publicationDate_tdate,journalIssn_s'

    req = requests.get(
        'http://api.archives-ouvertes.fr/search/?q=' + field + ':' + str(idHal) + '&fl=' + flags + '&start=' + str(
            increment))

    if req.status_code == 200:
        data = req.json()
        if "response" in data.keys():
            data = data['response']
            count = data['numFound']

            for article in data['docs']:
                if 'fulltext_t' in article:
                    print(article['fulltext_t'])
                articles.append(article)
            if (count > 30) and (increment < (count)):
                increment += 30
                tmp_articles = find_publications(idHal, field, increment=increment)
                for tmp_article in tmp_articles:
                    articles.append(tmp_article)
                return articles
            else:
                return articles
        else:
            print('Error : wrong response from HAL API endpoint')
            return -1
    else:
        print('Error : can not reach HAL API endpoint')
        return articles


issns = []

with open('../data/shs_issn-list.csv', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    for row in csv_reader:
        issns.append(row['issn'])

articles = find_publications('527028', 'structId_i')

for article in articles:
    if int(article['publicationDate_tdate'][0:4]) >= 2017:
        if 'journalIssn_s' in article:
            if article['journalIssn_s'] in issns:
                print(article['publicationDate_tdate'][0:4] + ' ' + article['title_s'][0] + ' (' + article['journalIssn_s'] + ')')