import paho.mqtt.client as mqtt
import json
import time
from langchain.chat_models.openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
import docx2txt
import requests
from datahandler import DataHandler 


# Variables globales
broker_address = "mqtt.eclipseprojects.io"
topic = "Spirulina_Edge"
api_key = ""
temperature = 0.6

class Subscriber:
    def __init__(self, data_handler, llm_model):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.data_handler = data_handler
        self.llm_model = llm_model
        self.processing_message = False 
        

    def start(self):
        self.client.connect(broker_address)
        self.client.loop_start()
   

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
         if not self.processing_message:
            
                self.processing_message = True 
                data = json.loads(msg.payload.decode())
                # Convert the Python dictionary to a JSON object
                json_data = json.loads(data)
                print("Received data:", json_data)
             
            
                # Get weather data using latitude and longitude from the message
                latitude = 37.108796
                longitude = 10.25208
                weather_data = self.get_weather_data(latitude, longitude)
                if weather_data:
                    print("Les données météorologiques pour Bio ALgues Mahdia,Tunis:")
                    print(f"Temperature at 2m: {weather_data['hourly']['temperature_2m'][0]}°C")
                    print(f"Precipitation: {weather_data['hourly']['precipitation'][0]} mm")
                else:
                    print("Unable to fetch weather data.")
                
            
                self.data_handler.execute(json_data)
            
          
            
            

    def get_weather_data(self, latitude, longitude):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the response status code is not 200
            weather_data = response.json()  # Parse the JSON response
            return weather_data
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

class MyLLM(ChatOpenAI):
    def __init__(self):
        super().__init__(api_key=api_key, temperature=temperature)

    def execute(self, recommendations):
        response_data = {
            "recommendations": recommendations,
            
        }
        return response_data

# Exemple d'utilisation
if __name__ == "__main__":
   
    data_handler_instance = DataHandler()
    llm_model_instance = MyLLM()
    subscriber = Subscriber(data_handler=data_handler_instance, llm_model=llm_model_instance)
    subscriber.client.on_connect = subscriber.on_connect
    subscriber.client.on_message = subscriber.on_message
    subscriber.start()
    
   
    
    try:
        # Garder le subscriber en cours d'exécution pendant 2 heures (7200 secondes)
        time.sleep(7200)
    except KeyboardInterrupt:
        # Arrêter le subscriber si interrompu par le clavier
     subscriber.stop()
 
     
