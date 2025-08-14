import requests
from bs4 import BeautifulSoup
import re

page_number = 0
url = 'https://lesjeudis.com/jobs?page={page_number}&limit=50'

print("Récupération des offres d'emploi...")
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
print(soup)
dico = {}
# Récupérer la section avec l'id "Projet"
section_projet = soup.find(id="projets")
pattern = re.compile(r'^https://github.com/Hugo-Leyx-valade/')
patern2 = re.compile(r'^\.\/.*\.html$')
if section_projet:
    liens = soup.find_all('a', href=pattern)
    print("Liens GitHub trouvés :")
    for lien in liens:
        print(lien['href'])
        dico[lien['href']] = (lien.find_parent(class_ = "glide__slide").find('a', href=patern2)['href'])
    print(dico)
else:
    print("Section 'Projet' non trouvée.")


"""https://github.com/Hugo-Leyx-valade/"""