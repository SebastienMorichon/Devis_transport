import requests
from bs4 import BeautifulSoup

def get_cnr_index():
    url = "https://www.cnr.fr/espaces/2/indicateurs/26"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Trouver l'élément avec l'ID "lastValue"
        value_element = soup.find("p", id="lastValue")
        
        if value_element:
            # Extraire le texte de la balise <b>
            cnr_value = value_element.find("b").text.strip()
            cnr_value = cnr_value.replace(",", ".")  # Convertir en format numérique
            return float(cnr_value)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur de récupération de l'indice CNR : {e}")
        return None 
