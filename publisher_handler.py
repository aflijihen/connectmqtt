


import paho.mqtt.client as mqtt
import json
from openai import OpenAI
import os  



api_key = os.getenv("OPENAI_API_KEY", "")


broker_address = "mqtt.eclipseprojects.io"
topic = "Spirulina"


class Publisher:
    def __init__(self):
       
        self.llm = OpenAI(api_key=api_key)

    def generate_recommendation(self, data):
       

        # Construct user input string summarizing sensor data
        user_input = """ Utiliser les valeurs actuelles :temperature: {data['temperature']}°C - Ph : {data['Ph_value']} - Niveau_deau : {data['water_level']} - Conductivité : {data['conductivity']} - Luminosité : {data['brightness']}, donner des recommandations spécifiques à chaque mesure: ")"""



        # Define system prompt with action-description table and instructions for recommendation generation
        system_prompt = """
        Assurez-vous que toutes les réponses sont sous forme JSON :
        en utilisant le Tableau d'action de document la PARTIE 2 seleument le code qui specifique a chaque recommendation 
      
        """

        # Generate response using the prompt and LLM
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        recommendations = response.choices[0].message.content.upper()  # Convert to uppercase for easier matching

        # Extract only the recommended action codes (letters)
        extracted_codes = set(char for char in recommendations if char in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"))

        # Convert recommendations to a dictionary for JSON
        recommendations_dict = {"recommendations": list(extracted_codes)}

        return recommendations_dict

    def publish_recommendations(self, recommendations):
        # Connect to MQTT broker
        client = mqtt.Client()
        try:
            client.connect(broker_address)
        except ConnectionRefusedError:
            print("Error connecting to MQTT broker:", broker_address)
            return

        # Convert recommendations to JSON and publish to topic
        message = json.dumps(recommendations)
        client.publish(topic, message)
        print("Published recommendations:", recommendations)




