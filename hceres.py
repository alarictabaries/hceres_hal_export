import requests
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import WriteOnlyCell
from openpyxl.utils.dataframe import dataframe_to_rows


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
            'publicationDateY_i,' \
            'defenseDate_tdate'

    req = requests.get(
        'http://api.archives-ouvertes.fr/search/?q=' + field + ':' + str(idHal) + '&fl=' + flags + '&start=' + str(
            increment) + '&fq=publicationDateY_i:[2016 TO *]')

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

hceres_art = []
hceres_book = []
hceres_conf = []
hceres_hdr = []

for article in articles:

    article["authfullName_s"] = ""

    if "serie_s" in article:
        if "issue_s" in article:
            article["volFull_s"] = article["serie_s"][0] + " " + article["issue_s"]
        else:
            article["volFull_s"] = article["serie_s"][0]

    if "journalTitle_s" not in article:
        article["journalTitle_s"] = ""

    if 'openAccess_bool' in article:
        if article['openAccess_bool'] == "true" or article['openAccess_bool'] == True:
            article["openAccess_bool_s"] = "O"
        else:
            article["openAccess_bool_s"] = "N"
    else:
        article["openAccess_bool_s"] = "N"

    if 'conferenceStartDate_tdate' in article:
        tmp_start = article["conferenceStartDate_tdate"][0:9].split("-")
        if 'conferenceEndDate_tdate' in article:
            tmp_end = article["conferenceEndDate_tdate"][0:9].split("-")
            article["conferenceDate_s"] = tmp_start[2] + "-" + tmp_start[1] + "-" + tmp_start[0] + ", " + tmp_end[2] + "-" + tmp_end[1] + "-" + tmp_end[0]
        else:
            article["conferenceDate_s"] = tmp_start[2] + "-" + tmp_start[1] + "-" + tmp_start[0]
    else:
        if 'conferenceEndDate_tdate' in article:
            article["conferenceDate_s"] = tmp_end[2] + "-" + tmp_end[1] + "-" + tmp_end[0]

    if "defenseDate_tdate" in article:
        article["defenseDate_tdate_s"] = article["defenseDate_tdate"][0:9]

    article["title_s"] = article["title_s"][0]

    for i in range(len(article["authFirstName_s"])):
        article["authfullName_s"] += article["authLastName_s"][i].upper() + " " + article["authFirstName_s"][i] + ", "

    article["authfullName_s"] = article["authfullName_s"][:-2]

    print(article["authfullName_s"])

    # colloque et posters
    if article["docType_s"] == "COMM" or article["docType_s"] == "POSTER":
        hceres_conf.append(article)

    # art
    if article["docType_s"] == "ART":
        hceres_art.append(article)
    # ouvrages, chapitres d'ouvrages et directions d'ouvrages
    if article["docType_s"] == "COUV" or article["docType_s"] == "DOUV" or article["docType_s"] == "OUV":
        hceres_book.append(article)


art_df = pd.DataFrame(hceres_art)
art_df = art_df.sort_values(by=['publicationDateY_i'])

book_df = pd.DataFrame(hceres_book)
book_df = book_df.sort_values(by=['publicationDateY_i'])

conf_df = pd.DataFrame(hceres_conf)
conf_df = conf_df.sort_values(by=['publicationDateY_i'])

writer = pd.ExcelWriter("output.xlsx", engine='openpyxl')
art_df[['authfullName_s','title_s','journalTitle_s','volFull_s', 'page_s', 'publicationDateY_i', 'doiId_s', 'openAccess_bool_s']].to_excel(writer, 'ART', index=False)
book_df[['authfullName_s','title_s','journalTitle_s','volFull_s', 'page_s', 'publicationDateY_i', 'isbn_s', 'openAccess_bool_s']].to_excel(writer, 'OUV', index=False)
conf_df[['authfullName_s','title_s','journalTitle_s','volFull_s', 'page_s', 'publicationDateY_i', 'doiId_s', 'conferenceTitle_s', 'conferenceDate_s', 'openAccess_bool_s']].to_excel(writer, 'CONF', index=False)
writer.save()