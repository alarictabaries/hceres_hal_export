import requests
import csv

def find_publications(idHal, field, increment=0):
    articles = []
    # ex : https://hal.archives-ouvertes.fr/hal-02637923
    # issue_s => numéro (84)
    # page_s => pages (9-12)
    # serie_s => volume ? (2)

    flags = 'halId_s,' \
            'authFirstName_s,authLastName_s,' \
            'docType_s,doiId_s,' \
            'bookTitle_s,title_s,journalTitle_s,volume_s,serie_s,page_s,issue_s' \
            'openAccess_bool,' \
            'conferenceTitle_s,conferenceStartDate_tdate,conferenceEndDate_tdate,' \
            'isbn_s,' \
            'publicationDateY_i'

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


# pour lab IMSIC
articles = find_publications('527028', 'structId_i')

for article in articles:
    print(article)