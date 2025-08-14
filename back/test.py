import requests
from bs4 import BeautifulSoup
import re
import json

page_number = 0
pattern = re.compile(r'^BaseJobCard_container__')
pattern_title = re.compile(r'^BaseJobCard_jobTitle__')
pattern_company = re.compile(r'\bjob-card-company-name\b')
pattern_company_bis = re.compile(r'\bjob-card-company-name\b')
pattern_location = re.compile(r'^job-location-tag')
pattern_date = re.compile(r'job-date-tag')
pattern_description = re.compile(r'^html-renderer-job-main-body-text')
pattern_status = re.compile(r'^job-occupation-type-tag')
pattern_link = re.compile(r'^BaseJobCard_jobTitle__')

with open("offres.jsonl", "w", encoding="utf-8") as f: #pour supprimmer le texte précédent
    pass

for i in range(0, 5):
    url = 'https://lesjeudis.com/jobs?page={page_number}&limit=20'
    print("Récupération des offres d'emploi...")
    r = requests.get(url.format(page_number=i))
    soup = BeautifulSoup(r.text, 'html.parser')
    tableau = soup.find(class_="Jobs_jobsList__sRyvQ")
    offres = tableau.find_all('div', class_=pattern)
    if offres:
        for offre in offres:
            obj = {}
            lien = "https://lesjeudis.com/"+offre.find('a', class_=pattern_link)['href']
            obj[offre.find('a', class_=pattern_title).text] = {
                'company': (offre.find('span', {'data-testid': pattern_company}).text if offre.find('span', {'data-testid': pattern_company}) else offre.find('a', {'data-testid' : pattern_company_bis}).text),
                'location': offre.find('div', {'data-testid' : pattern_location}).text if offre.find('div', {'data-testid' : pattern_location}) else 'N/A',
                'date': offre.find('div', {'data-testid' : pattern_date}).text if offre.find('div', {'data-testid' : pattern_date}) else 'N/A',
                'status': offre.find('div', {'data-testid' : pattern_status}).text if offre.find('div', {'data-testid' : pattern_status}) else 'N/A',
                'link': lien,
            }
            r2 = requests.get(lien)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            description = soup2.find('div', {'data-testid' : pattern_description})
            obj[offre.find('a', class_=pattern_title).text]['description'] = description.text if description else 'N/A'
            with open("offres.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    else:
        print("Section 'Projet' non trouvée.")