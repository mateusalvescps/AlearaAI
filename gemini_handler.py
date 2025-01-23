import google.generativeai as genai
from PIL import Image
from typing import Dict, Optional, List
import googlemaps
import json
import time
import re
from pprint import pformat

class GeminiHandler:
    def __init__(self):
        self.api_key = "AIzaSyA-fkqtBJphYnJXdbKxV5UjXh2gky72IEc"
        genai.configure(api_key=self.api_key)
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.maps_api_key = 'AIzaSyCvXge_bQItaPfrmMOZxN-f8Qe3UjbS3Fo'
        self.map_client = googlemaps.Client(self.maps_api_key)
        
        self.system_instruction = """
        Você é Elara, uma IA amigável e especializada em recomendações gastronômicas. Sua função é ajudar os usuários a descobrir restaurantes e experiências culinárias, considerando suas preferências, localização e orçamento. Mantenha um tom amigável e use emojis para tornar a conversa mais envolvente.

        Extraia as seguintes informações da entrada do usuário:
        1. Preferência culinária (Ajude com exemplos)(resumida em poucas palavras, caso ele fale um prato específico, resuma em poucas palavras também)
        2. Localização do usuário (cidade e bairro, se possível. Se o usuário falar de algum bairro de onde ele não está reformule como você vai solicitar as informações abaixo... dizendo algo como: e você quer procurar algo no [bairro/cidade] ou está afim de ir mais longe? < algo assim)
        3. Distância desejada (identifique qual a preferência do usuário de acordo com oq ele falar e classifique  como "perto", "médio" ou "longe")
        4. Faixa de preço desejada (identifique qual a preferência do usuário de acordo com oq ele falar e classifique  como como "barato", "médio" ou "caro")

        Se alguma informação não for fornecida, indique como null.

        Mantenha o foco em gastronomia e redirecione gentilmente se o usuário desviar do assunto.
        Não faça perguntas juntas, pergunte 1 preferência por vez.

        Retorne as preferências do usuário em JSON da seguinte forma:
        
        {
            "preferencia_culinaria": null,
            "local_usuario": null,
            "distancia": null,
            "preco": null
        }
        
        Não inclua este JSON na resposta ao usuário, use-o apenas internamente.
        """
        
        self.chat_model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        self.vision_model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        self.chat = self.chat_model.start_chat(history=[])
        self.chat.send_message(self.system_instruction)

        self.user_preferences = {
            "preferencia_culinaria": None,
            "local_usuario": None,
            "distancia": None,
            "preco": None
        }
        self.user_coordinates = None

    def analyze_input(self, text: str, image_path: Optional[str] = None) -> List[str]:
        try:
            print("Analyzing input:", text)
            if image_path:
                image = Image.open(image_path)
                prompt = f"{self.system_instruction}\n\nAnalise esta imagem e identifique o tipo de comida mostrada. Use essa informação como preferência culinária do usuário ""preferencia_culinaria"". Se houver um texto do usuário, considere-o também: {text}"
                response = self.vision_model.generate_content([prompt, image])
            else:
                response = self.chat.send_message(text)
            
            if response.parts:
                response_text = response.parts[0].text
            else:
                response_text = "Desculpe, não consegui processar sua mensagem."
            
            extracted_info = self.extract_information(response_text)
            print("Extracted info:", extracted_info)
            self.update_user_preferences(extracted_info)
            print("Updated user preferences:", self.user_preferences)
            
            ai_response = self.remove_json_from_response(response_text)
            messages = [ai_response]
            
            if all(self.user_preferences.values()):
                recommendations = self.get_restaurant_recommendations()
                messages.append(recommendations)
            
            return messages
        except Exception as e:
            print(f"Error in analyze_input: {e}")
            return ["Desculpe, ocorreu um erro ao processar sua mensagem. Pode tentar novamente?"]

    def extract_information(self, text: str) -> Dict[str, str]:
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_info = json.loads(json_str)
                return {k: v for k, v in extracted_info.items() if v is not None}
            else:
                print("No JSON object found in the response")
                return {}
        except json.JSONDecodeError:
            print("Failed to parse JSON from response")
            return {}

    def remove_json_from_response(self, text: str) -> str:
        return re.sub(r'\{.*\}', '', text, flags=re.DOTALL).strip()

    def update_user_preferences(self, extracted_info: Dict[str, str]):
        print("Starting update_user_preferences with:", extracted_info)
        for key, value in extracted_info.items():
            if value is not None and value != "":
                if key == "preco":
                    if value.lower() in ["1", "barato"]:
                        self.user_preferences[key] = 1
                    elif value.lower() in ["2", "médio", "medio"]:
                        self.user_preferences[key] = 2
                    elif value.lower() in ["3", "4", "caro"]:
                        self.user_preferences[key] = 3
                elif key == "distancia":
                    if value.lower() == "perto":
                        self.user_preferences[key] = 1
                    elif value.lower() == "médio" or value.lower() == "medio":
                        self.user_preferences[key] = 3
                    elif value.lower() == "longe":
                        self.user_preferences[key] = 8
                    else:
                        print(f"Invalid distance value: {value}")
                else:
                    self.user_preferences[key] = value

        print("Final user preferences after update:", self.user_preferences)

    def get_missing_preference(self):
        for key, value in self.user_preferences.items():
            if value is None:
                return key
        return None

    def get_user_coordinates(self):
        local_usuario = self.user_preferences.get('local_usuario')
        if not local_usuario:
            print("User location not provided.")
            return

        print(f"Getting coordinates for: {local_usuario}")
        geocode = self.map_client.geocode(address=local_usuario)
        if not geocode:
            print("Não foi possível encontrar as coordenadas para o endereço fornecido.")
            return

        lat, lng = geocode[0]['geometry']['location']['lat'], geocode[0]['geometry']['location']['lng']
        self.user_coordinates = (lat, lng)
        print(f"User coordinates: {self.user_coordinates}")

    def miles_to_meters(self, miles):
        try:
            return miles * 1609.344
        except:
            return 0

    def buscar_restaurantes(self):
        print("Starting restaurant search...")
        print("User preferences:", self.user_preferences)

        self.get_user_coordinates()
        if not self.user_coordinates:
            print("User coordinates not available.")
            return []

        preferencia_culinaria = self.user_preferences.get('preferencia_culinaria', 'restaurante')
        distancia = self.user_preferences.get('distancia', 5)  # Default to 5km if not specified
        preco = self.user_preferences.get('preco', 2)

        print(f"Searching for {preferencia_culinaria} restaurants near {self.user_coordinates}")

        distancia_metros = int(self.miles_to_meters(distancia))
        print(f"Search radius: {distancia_metros} meters")

        params = {
            "location": self.user_coordinates,
            "keyword": preferencia_culinaria,
            "radius": distancia_metros,
            "type": "restaurant",
            "min_price": 1,
            "max_price": preco
        }
        print("Search parameters:", params)

        business_list = []
        response = self.map_client.places_nearby(**params)
        business_list.extend(response.get('results', []))
        print(f"Initial results: {len(business_list)} restaurants found")

        next_page_token = response.get('next_page_token')
        while next_page_token:
            print("Fetching next page of results...")
            time.sleep(2)
            params['page_token'] = next_page_token
            response = self.map_client.places_nearby(**params)
            new_results = response.get('results', [])
            business_list.extend(new_results)
            print(f"Added {len(new_results)} more restaurants")
            next_page_token = response.get('next_page_token')

        print(f"Total restaurants found: {len(business_list)}")
        return business_list

    def get_restaurant_recommendations(self):
        results = self.buscar_restaurantes()
        if results:
            unformatted_results = pformat(results)
            prompt = f"""
            Aqui está uma lista de restaurantes encontrados com base nas preferências do usuário:

            {unformatted_results}
            
            faça uma mensagem como encontrei algumas opções aqui

            Crie uma lista formatada com as 4 melhores opções, incluindo:
            - Nome do restaurante
            - Uma breve descrição e destaque do restaurante
            - Endereço
            - Avaliação (se disponível)
            - Faixa de preço (use símbolos de $ de 1 a 4 para representar)
            - Link do Google Maps use o formato: (
                lat-lng: é a latitude e longitude da preferencia do usuário (ex.: 47.5951518%2C-122.3316393)
                place_id: é o ['place_id'] apresentado para você (ex.:query_place_id=ChIJd223s1bPyJQRBHOolRUwQp4)
                https://www.google.com/maps/search/?api=1&query=lat-lng&query_place_id=place+id
                exemplo geral: https://www.google.com/maps/search/?api=1&query=47.5951518%2C-122.3316393&query_place_id=ChIJd223s1bPyJQRBHOolRUwQp4
                vá até [nome do restaurante] < e o link concatenado
                Nunca deixe o link visível, sempre concatene ao texto
                
                )

            Apresente as informações de forma amigável e envolvente, usando emojis quando apropriado e deixe fácil de entender! Siga sempre 1 modelo, em lista.
            
            Não coloque observações, este dado será apresentado para o usuário.
            Nunca repita opções já apresentadas, mesmo que tenha que apresentar um número menor que 4
            """
            response = self.chat_model.generate_content(prompt)
            return response.text
        else:
            return "Desculpe, não consegui encontrar restaurantes que atendam aos seus critérios. Poderia tentar com outras preferências?"