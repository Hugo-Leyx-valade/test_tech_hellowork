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


def test_update(line):
    url = 'https://lesjeudis.com/jobs?page={page_number}&limit=20'
    r = requests.get(url.format(page_number=0))
    soup = BeautifulSoup(r.text, 'html.parser')
    tableau = soup.find(class_="Jobs_jobsList__sRyvQ")
    offre = tableau.find('div', class_=pattern)
    lien = "https://lesjeudis.com/"+offre.find('a', class_=pattern_link)['href'] #lien de l'offre
    titre = offre.find('a', class_=pattern_title).text
    premier_obj = json.loads(line)
    if premier_obj['link'] == lien:
        return True
    else:
        return False


with open("offres.jsonl", "r", encoding="utf-8") as f: #pour supprimmer le texte précédent
    line = f.readline()
    if line!= "" and test_update(line):
        print("Le fichier est à jour.")
        exit(0)
    else:
        print("Le fichier n'est pas à jour, récupération des nouvelles offres d'emploi...")
        f.close()
        with open("offres.jsonl", "w", encoding="utf-8") as f:
            pass
        with open("infos.jsonl", "w", encoding="utf-8") as f: #pour supprimmer le texte précédent
            pass
        nombre_offres = 0 
        nombre_entreprises = set()
        repartition_type_contrat = {}
        print("Récupération des offres d'emploi...")
        for i in range(0, 5):
            url = 'https://lesjeudis.com/jobs?page={page_number}&limit=20'
            r = requests.get(url.format(page_number=i))
            soup = BeautifulSoup(r.text, 'html.parser')
            tableau = soup.find(class_="Jobs_jobsList__sRyvQ")
            offres = tableau.find_all('div', class_=pattern)
            if offres:
                for offre in offres:
                    nombre_offres += 1
                    obj = {}
                    lien = "https://lesjeudis.com/"+offre.find('a', class_=pattern_link)['href'] #lien de l'offre
                    titre = offre.find('a', class_=pattern_title).text
                    company=(offre.find('span', {'data-testid': pattern_company}).text if offre.find('span', {'data-testid': pattern_company}) else offre.find('a', {'data-testid' : pattern_company_bis}).text),
                    nombre_entreprises.add(company)
                    location= offre.find('div', {'data-testid' : pattern_location}).text if offre.find('div', {'data-testid' : pattern_location}) else 'N/A',
                    date= offre.find('div', {'data-testid' : pattern_date}).text if offre.find('div', {'data-testid' : pattern_date}) else 'N/A',
                    status= offre.find('div', {'data-testid' : pattern_status}).text if offre.find('div', {'data-testid' : pattern_status}) else 'N/A',
                    status = str(status)
                    if status not in repartition_type_contrat:
                        repartition_type_contrat[status] = 1
                    else:
                        repartition_type_contrat[status] += 1
                    obj = { #data récupérées depuis la page de recherche 
                        'title': titre,
                        'company': company,
                        'location': location,
                        'date': date,
                        'status': status,
                        'link': lien,
                    }
                    r2 = requests.get(lien)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    description = soup2.find('div', {'data-testid' : pattern_description}) # data récupérées depuis la page de l'offre
                    obj['description'] = description.text if description else 'N/A'
                    with open("offres.jsonl", "a", encoding="utf-8") as f:
                        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            else:
                print("Section 'Projet' non trouvée.")

        with open("infos.jsonl", "a", encoding="utf-8") as f2:
            infos = {
                'nombre_offres': nombre_offres,
                'nombre_entreprises': len(nombre_entreprises),
                'repartition_type_contrat': repartition_type_contrat
            }
            json.dump(infos, f2, ensure_ascii=False, indent=4)
        print(f"Nous avons trouvé {nombre_offres} offres d'emploi. Dont {len(nombre_entreprises)} entreprises différentes. Répartition des types de contrat : {repartition_type_contrat}")


