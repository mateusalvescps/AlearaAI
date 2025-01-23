from pprint import pprint
import time
import googlemaps  # pip install googlemaps
import pandas as pd  # pip install pandas

def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0

API_KEY = 'AIzaSyCvXge_bQItaPfrmMOZxN-f8Qe3UjbS3Fo'
map_client = googlemaps.Client(API_KEY)

address = 'Campinas/SP'
geocode = map_client.geocode(address=address)
(lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))
print((lat, lng))

search_string = 'Comida Japonesa'
distance = miles_to_meters(2)
business_list = []

# Parâmetros ajustados
params = {
    "location": (lat, lng),
    "keyword": search_string,
    "radius": distance,
    "type": "restaurant",  # Tipo específico de lugar
    "min_price": 1,  # Faixa de preço mínima (1 a 4)
    "max_price": 4   # Faixa de preço máxima (1 a 4)
}

# Primeira chamada de busca
response = map_client.places_nearby(**params)
business_list.extend(response.get('results'))
next_page_token = response.get('next_page_token')

# Loop para resultados paginados
while next_page_token:
    time.sleep(5)
    params['page_token'] = next_page_token
    response = map_client.places_nearby(**params)
    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

# Exibir os resultados
pprint(business_list)