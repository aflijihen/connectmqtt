import paho.mqtt.client as mqtt
import json
from openai import OpenAI  # Assurez-vous d'avoir correctement importé OpenAI

# Variables globales
broker_address = "mqtt.eclipseprojects.io"
topic = "Spirulina"

class Publisher:
    def __init__(self, llm):
        self.llm = OpenAI(api_key='')
        
    def generate_recommendation(self, data):
        recommendations = {}
        # Temperature
        if data['temperature'] >= 34:
            recommendations['TEMPERATURE'] = 'K'  # Température supérieure à 34°C
        elif data['temperature'] < 4:
            recommendations['TEMPERATURE'] = 'L'  # Température inférieure à 4°C

        # pH
        if data['Ph_value'] > 10.5:
            recommendations['PH'] = 'E'  # pH supérieur à 10,5
        elif data['Ph_value'] > 10.2:
            recommendations['PH'] = 'D'  # pH supérieur à 10,2
        elif data['Ph_value'] < 9:
            recommendations['PH'] = 'C'  # pH inférieur à 9

        # Niveau d'eau
        if data['brightness'] > 4:
            recommendations['LUMINOSITE'] = 'I'  # Niveau d'eau supérieur à 4cm
        elif data['brightness'] > 3:
            recommendations['LUMINOSITE'] = 'H'  # Niveau d'eau entre 3cm et 4cm
        elif data['brightness'] > 2:
            recommendations['LUMINOSITE'] = 'G'  # Niveau d'eau entre 2cm et 3cm
        elif data['brightness'] <= 2:
            recommendations['LUMINOSITE'] = 'F'  # Niveau d'eau inférieur ou égal à 2cm

        # Conductivité 

        if data['conductivity']< 15:
              recommendations['conductivity'] = 'A'
        elif data['conductivity']> 35:
            recommendations['conductivity'] = 'B'

        # Luminosité
        if data['brightness'] > 10:
            recommendations['LUMINOSITE'] = 'J'  # Luminosité dépasse 10cm

        # Construire la chaîne user_input
        user_input = (f"Utiliser les valeurs actuelles : temperature: {data['temperature']}°C - Ph : {data['Ph_value']} - Niveau_deau : {data['water_level']} - Conductivité : {data['conductivity']} - Luminosité : {data['brightness']}, donner des recommandations spécifiques à chaque mesure: ")
        
        # Définir le prompt avec les actions et descriptions
        system_prompt = f"""
        Assurez-vous que toutes les réponses sont sous forme JSON : 
        envoyer seulement code 

      {user_input}
        """

        # Générer la réponse en utilisant le prompt
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return recommendations

    def publish_recommendations(self, recommendations):
        # Extraire uniquement les codes de recommandation du dictionnaire
        extracted_codes = set(recommendations.values())

        # Convertir les codes extraits en un dictionnaire pour la structure JSON
        extracted_recommendations = {"RECOMMANDATIONS": list(extracted_codes)}

        # Connecter au broker MQTT
        client = mqtt.Client()
        client.connect(broker_address)
        

        # Convertir les recommandations extraites en JSON et publier au topic
        message = json.dumps(extracted_recommendations)
        client.publish(topic, message)
        print("Published recommendations:", extracted_recommendations)






