# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union
from rasa_sdk.events import SlotSet
import json
import re
import asyncio



from typing import Text, List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from time import sleep


        
class GetForfait(Action):
    # Regular expression pattern to match forfait values
    forfait_pattern = re.compile(r'(?<!\d)(50|100|200|350|440|1|1,1|2,2|2,5|6|10|25|55|500|700)\s*(Go|GO|Mo|MO|go|mo)?(?!\d)')
    # List of valid units
    units = ["Go", "GO", "Mo", "MO", "go", "mo"]

    def __init__(self):
        self.forfait_regex = re.compile(self.forfait_pattern)

    def name(self) -> Text:
        return "get_forfait"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the entities from the latest user message
        forfait_entities = tracker.latest_message["entities"]
        forfait = None
        forfait_unit = None

        # Find the first matching entity using the forfait_regex pattern
        match = next((self.forfait_regex.search(entity["value"]) for entity in forfait_entities if entity["entity"] == "forfait"), None)
        if match:
            # Extract the forfait value and unit from the match
            forfait = match.group(1)
            forfait_unit = match.group(2)

        # If unit is not found, try to determine it from the message by checking for valid units
        if not forfait_unit:
            forfait_unit = next((word for word in tracker.latest_message['text'].split() if word in self.units), None)

        if forfait and forfait_unit:
            # Set the forfait and forfait_unit slots
            return [SlotSet("forfait", forfait), SlotSet("forfait_unit", forfait_unit)]
        else:
            # No valid forfait and forfait_unit found, return empty list
            return []



        
class GetCodeAcces(Action):
    def name(self) -> Text:
        return "get_code_acces"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the value of the "forfait" slot
        forfait = tracker.get_slot("forfait")
        code_acces = None
        
        # Read-only dictionary of access codes for each forfait type
        codes_acces = {
            "50": "*140*1*1#",
            "200": "*140*2*1#",
            "440": "*140*4*1#",
            "1.1": "*140*3*1#",
            "1,1": "*140*3*1#",
            "2.2": "*140*7*1*1#",
            "2,2": "*140*7*1*1#",
            "6": "*140*7*2*1#",
            "10": "*140*5*1#",
            "25": "*140*6*1#",
            "55": "*140*7*3*1#"
        }
        
        # Check if the forfait is in the codes_acces dictionary
        if forfait in codes_acces:
            # Get the access code for the forfait
            code_acces = codes_acces.get(forfait)
        else:
            # If the forfait is not available, send a message and set code_acces to None
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("code_acces", None)]
        
        # Set the value of the "code_acces" slot
        return [SlotSet("code_acces", code_acces)]


from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class GetRenouvel(Action):
    def name(self) -> Text:
        return "get_renouvel"

    # Dictionary mapping forfait types to renewal options
    FORFAIT_RENOUV_OPTIONS = {
        "50": "manuellement",
        "100": "manuellement",
        "350": "manuellement",
        "1": "manuellement",
        "2.5": "manuellement",
        "2,5": "manuellement",
        "200": "automatiquement",
        "440": "automatiquement",
        "500": "automatiquement",
        "700": "automatiquement",
        "1.1": "automatiquement",
        "1,1": "automatiquement",
        "2.2": "automatiquement",
        "2,2": "automatiquement",
        "6": "automatiquement",
        "10": "automatiquement",
        "25": "automatiquement",
        "55": "automatiquement"
    }

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the value of the "forfait" slot
        forfait = tracker.get_slot("forfait")
        # Get the corresponding renewal option from the FORFAIT_RENOUV_OPTIONS dictionary
        renouv = self.FORFAIT_RENOUV_OPTIONS.get(forfait)

        if renouv is None:
            # If the renewal option is not available, send a message and set renouv to None
            dispatcher.utter_message("Désolé, je ne comprends pas quel forfait vous voulez.")
            return [SlotSet("renouv", None)]
        else:
            # If the renewal option is available, get the value of the "forfait_unit" slot
            forfait_unit = tracker.get_slot("forfait_unit")
            # Send a message with the renewal option for the specified forfait and forfait_unit
            dispatcher.utter_message(f"Le renouvellement du forfait {forfait} {forfait_unit} se fait {renouv}.")
            # Set the value of the "renouv" slot
            return [SlotSet("renouv", renouv)]


class GetPrice(Action):
    def name(self) -> Text:
        return "get_price"
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Définir les prix des différents types de forfaits dans un dictionnaire
        prices = {
            "50": {"price": "0,250", "price_remise": "0,238"},
            "200": {"price": "0,9", "price_remise": "0,855"},
            "440": {"price": "2", "price_remise": "1,9"},
            "1.1": {"price": "4,5", "price_remise": "4,275"},
            "1,1": {"price": "4,5", "price_remise": "4,275"},
            "2.2": {"price": "8", "price_remise": "7,6"},
            "2,2": {"price": "8", "price_remise": "7,6"},
            "6": {"price": "15", "price_remise": "14,25"},
            "10": {"price": "20", "price_remise": "19"},
            "25": {"price": "25", "price_remise": "23,75"},
            "55": {"price": "55", "price_remise": "52,25"}
            
        }
        
        price_hadra1 = {
            "100" : {"price_hadra" : "0,8"},
            "350" : {"price_hadra" : "2"},
            "1" : {"price_hadra" : "5"},
            "2.5":{"price_hadra" : "9,5"}

        }
        price_facebook = {
            "500" : {"pricef" : "2,5"},
            "700" : {"pricef" : "3,5"}
        }
        
        # Récupérer la valeur du slot "forfait"
        forfait = tracker.get_slot("forfait")
        forfait_unit = tracker.get_slot("forfait_unit")
        duree =  tracker.get_slot("duree")
        # Vérifier si le type de forfait existe dans le dictionnaire de prix
        if forfait in prices :
            # Si oui, récupérer le prix correspondant
            price = prices[forfait]["price"]
            price_remise = prices[forfait]["price_remise"]
            dispatcher.utter_message(" Le forfait internet mobile de {} {} coûte normalement {} DT, mais nous avons une offre spéciale pour vous!".format(forfait,forfait_unit , price))
            dispatcher.utter_message("En activant ce forfait via l'application MY TT, vous bénéficierez d'une remise de 5% soit {} DT seulement.".format(price_remise))
            return [SlotSet("forfait_unit", forfait_unit),SlotSet("price", price), SlotSet("price_remise", price_remise)]
            # Afficher uniquement le prix si le forfait est différent de ceux mentionnés ci-dessus
        elif forfait in price_hadra1 :
            price_hadra = price_hadra1[forfait]["price_hadra"]
            dispatcher.utter_message("Le forfait HADRA NET comprenant {} d'appels et {} {} de données mobiles est vendu seulement à {}DT.".format(duree, forfait,forfait_unit,  price_hadra))
            return [SlotSet("duree", duree), SlotSet("forfait_unit", forfait_unit),SlotSet("price_hadra", price_hadra)]
        elif forfait in price_facebook : 
            pricef = price_facebook[forfait]["pricef"]
            dispatcher.utter_message("Le forfait facebook de {} {} est proposé à un prix abordable de {} DT.".format(forfait,forfait_unit , pricef))
            return [SlotSet("forfait_unit", forfait_unit),SlotSet("pricef", pricef)]
        else:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return []
        

class GetTemps(Action):
    def name(self) -> Text:
        return "get_temps"
        
    # Dictionnaire qui mappe les types de forfaits avec leurs durées de validité
    FORFAIT_TIMES = {
        "50": "2 heures",
        "100": "jusqu'à minuit",
        "200": "24 heures",
        "350": "7 jours",
        "1": "30 jours",
        "2.5": "30 jours",
        "440": "7 jours",
        "500": "7 jours",
        "700": "30 jours",
        "1.1": "30 jours",
        "1,1": "30 jours",
        "2.2": "30 jours",
        "2,2": "30 jours",
        "6": "30 jours",
        "10": "30 jours",
        "25": "30 jours",
        "55": "30 jours"
    }

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Récupérer la valeur du slot "forfait"
        forfait = tracker.get_slot("forfait")
        # Récupérer la valeur du slot "forfait_ehdia"
        forfait_ehdia = tracker.get_slot("forfait_ehdia")
        temps = None

        if forfait:
            # Obtenir la durée de validité correspondante dans FORFAIT_TIMES pour le forfait
            temps = self.FORFAIT_TIMES.get(forfait)
        elif forfait_ehdia:
            # Obtenir la durée de validité correspondante dans FORFAIT_TIMES pour le forfait_ehdia
            temps = self.FORFAIT_TIMES.get(forfait_ehdia)

        if temps:
            # Envoyer un message avec la durée de validité du forfait
            dispatcher.utter_message(f"Le temps de validité du forfait est : {temps}")
        else:
            # Envoyer un message indiquant que le forfait demandé n'a pas été compris
            dispatcher.utter_message("Je n'ai pas compris quel forfait vous avez demandé.")
        
        # Mettre à jour la valeur du slot "temps"
        return [SlotSet("temps", temps)]


############################# Forfait Facebook ###################
class GetCodef(Action):
    def name(self) -> Text:
        return "get_code_f"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        forfait = tracker.get_slot("forfait")
        if forfait == "500":
            code_f = "*182*1*1#"
        elif forfait == "700":
            code_f = "*182*2*1#"
        else:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("code_f", None)]
        return [SlotSet("code_f", code_f)]



class GetCodeHadra(Action):
    def name(self) -> Text:
        return "get_code_hadra"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        forfait = tracker.get_slot("forfait")
        codes_hadra = {"100": "*140*7*4*3*Numéro*1*1#","350": "*140*7*4*3*Numéro*2*1#", "1": "*140*7*4*3*Numéro*3*1#", "2.5": "*140*7*4*3*Numéro*4*1#", "2,5": "*140*7*4*3*Numéro*4*1#"}
        code_hadra = codes_hadra.get(forfait)
        if not code_hadra:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("code_hadra", None)]
        return [SlotSet("code_hadra", code_hadra)]


class GetDuree(Action):
    def name(self) -> Text:
        return "get_duree"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        forfait = tracker.get_slot("forfait")
        durees = {"100": "10 minutes", "350": "15 minutes", "1": "15 minutes", "2,5": "20 minutes"}
        duree = durees.get(forfait)
        if not duree:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("duree", None)]
        return [SlotSet("duree", duree)]



################################################ Forfait EHDIA NET ########
class GetForfaitEhdia(Action):
    forfait_pattern_ehdia = re.compile(r'(?<!\d)(200|440|1,1|2,2|6|10|25)\s*(Go|GO|Mo|MO|go|mo)?(?!\d)')
    units = ["Go", "GO", "Mo", "MO", "go", "mo"]

    def __init__(self):
        self.forfait_regex_ehdia = re.compile(self.forfait_pattern_ehdia)

    def name(self) -> Text:
        return "get_forfait_ehdia"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        forfait_entities = tracker.latest_message["entities"]
        forfait_ehdia = None
        forfait_unite = None
        # Find the first matching entity
        match = next((self.forfait_regex_ehdia.search(entity["value"]) for entity in forfait_entities if entity["entity"] == "forfait_ehdia"), None)
        if match:
            forfait_ehdia = match.group(1)
            forfait_unite = match.group(2)

        # If unit is not found, try to determine it from the message
        if not forfait_unite:
            forfait_unite = next((word for word in tracker.latest_message['text'].split() if word in self.units), None)

        if forfait_ehdia and forfait_unite:
            return [SlotSet("forfait_ehdia", forfait_ehdia), SlotSet("forfait_unite", forfait_unite)]
        else:
            return []

class GetCodeEhdia(Action):
    def name(self) -> Text:
        return "get_code_ehdia"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        code_ehdia_dict = {
            "200": "140*7*4*1*Numéro_de_destinataire*1*1#",
            "440": "140*7*4*1*Numéro_de_destinataire*2*1#",
            "1,1": "140*7*4*1*Numéro_de_destinataire*3*1#",
            "2,2": "140*7*4*1*Numéro_de_destinataire*4*1#",
            "6": "140*7*4*1*Numéro_de_destinataire*5*1#",
            "10": "140*7*4*1*Numéro_de_destinataire*6*1#",
            "25": "140*7*4*1*Numéro_de_destinataire*7*1#"
        }
        
        forfait_ehdia = tracker.get_slot("forfait_ehdia")
        
        if forfait_ehdia in code_ehdia_dict:
            code_ehdia = code_ehdia_dict[forfait_ehdia]
            return [SlotSet("code_ehdia", code_ehdia)]
        else:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("code_ehdia", None)]


class GetPriceEhdia(Action):
    def name(self) -> Text:
        return "get_price_ehdia"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        forfait_prix = {
            "200": "0,9",
            "440": "2",
            "1,1": "4,5",
            "2,2": "8",
            "6": "15",
            "10": "20",
            "25": "30"
        }
        
        forfait_ehdia = tracker.get_slot("forfait_ehdia")
        if forfait_ehdia in forfait_prix:
            price_ehdia = forfait_prix[forfait_ehdia]
            return [SlotSet("price_ehdia", price_ehdia)]
        else:
            dispatcher.utter_message("Le forfait que vous avez demandé n'est pas disponible")
            return [SlotSet("price_ehdia", None)]


################################################## Récuperation des informations de carte SIM de la base de données ##########################
import mysql.connector
import random
import string

###### Dans la suite de code on a utiliser MySQLWorkbench pour la base de données ############


#La fonction de la classe ActionGetNumeroAppel est d'obtenir le numéro de téléphone entré par l'utilisateur, de vérifier sa validité, de générer un code de vérification unique et de l'associer au numéro de téléphone dans une base de données. 

class ActionGetNumeroAppel(Action):
    def name(self) -> Text:
        return "action_get_numero_appel"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Récupérer le numéro de téléphone entré par l'utilisateur
        numero_appel = tracker.latest_message['text']
        # If not, ask the user for the phone number
        if not numero_appel:
            dispatcher.utter_message(text="Pour des raisons de sécurité, j'ai besoin de vous envoyer un code de vérification. Pourriez-vous me donner votre numéro de téléphone pour que je puisse vous l'envoyer et confirmer votre identité ?")
            return []

        # Vérifier que le numéro de téléphone entré par l'utilisateur est valide
        if not numero_appel.isdigit() or len(numero_appel) != 8:
            dispatcher.utter_message(text="Le numéro de téléphone doit être composé de 8 chiffres.")
            return []

        # Connexion à la base de données
        cnx = mysql.connector.connect(user='root', password='Fayrouz@123', host='localhost', database='database', port='3306')
        cursor = cnx.cursor()

        # Exécution de la requête pour récupérer les informations du client en fonction du numéro de téléphone entré par l'utilisateur
        query = "SELECT auth_code FROM donnees_clients WHERE NUMERO_APPEL = '{}'".format(numero_appel)
        cursor.execute(query)

        # Récupération des résultats de la requête
        results = cursor.fetchall()
        # Vérifier si le numéro de téléphone entré par l'utilisateur est présent dans la base de données
        if not results:
            dispatcher.utter_message(text="Le numéro de téléphone n'est pas valide.")
            return []
        # Générer un nouveau code de vérification s'il n'y a pas déjà un code pour ce numéro de téléphone
        if not results:
            
            # Générer un code de vérification unique
            while True:
                letters = 'abcdefghijklmnopqrstuvwxyz'
                digits = '0123456789'
                rand_string = ''
                for i in range(3) : 
                    while True : 
                        k= random.choice(digits)
                        if k not in rand_string : break
                    # select at least one letter and one digit
                    rand_string += k
                    while True : 
                        l = random.choice(letters)
                        if l not in rand_string : break
                    rand_string += l
                # Générer un code de vérification aléatoire et unique
                #auth_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                auth_code = rand_string

                # Vérifier que le code est unique
                query = "SELECT COUNT(*) FROM donnees_clients WHERE auth_code = '{}'".format(auth_code)
                cursor.execute(query)
                count = cursor.fetchone()[0]
                if count == 0:
                    break

            # Insérer le nouveau code de vérification dans la base de données
            query = "UPDATE donnees_clients SET auth_code = '{}' WHERE NUMERO_APPEL = '{}'".format(auth_code, numero_appel)
            cursor.execute(query)
            cnx.commit()
            
        else:
            # Générer un nouveau code de vérification unique
            while True:
                letters = 'abcdefghijklmnopqrstuvwxyz'
                digits = '0123456789'
                rand_string = ''
                for i in range(3) : 
                    while True : 
                        k= random.choice(digits)
                        if k not in rand_string : break
                    # select at least one letter and one digit
                    rand_string += k
                    while True : 
                        l = random.choice(letters)
                        if l not in rand_string : break
                    rand_string += l
                # Générer un code de vérification aléatoire et unique
                #auth_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                auth_code = rand_string
                # Vérifier que le code est unique
                query = "SELECT COUNT(*) FROM donnees_clients WHERE auth_code = '{}'".format(auth_code)
                cursor.execute(query)
                count = cursor.fetchone()[0]
                if count == 0:
                    break

            # Insérer le nouveau code de vérification dans la base de données
            query = "UPDATE donnees_clients SET auth_code = '{}' WHERE NUMERO_APPEL = '{}'".format(auth_code, numero_appel)
            cursor.execute(query)
            cnx.commit()
            
    
        # Stocker le code de vérification dans une variable de suivi
        tracker.slots['auth_code'] = auth_code
        # Stocker le code de vérification dans une variable de suivi
        print(f'auth_code slot: {tracker.get_slot("auth_code")}')
        # Store the phone number in a slot
        tracker.slots['numero_appel'] = numero_appel
        print(f'numero_appel slot: {tracker.get_slot("numero_appel")}')
            # Ajout de la réponse à la conversation
        dispatcher.utter_message(text="Un code de vérification a été envoyé à votre téléphone. Veuillez saisir ce code")

        # Fermeture de la connexion à la base de données
        cursor.close()
        cnx.close()

        return [SlotSet('auth_code', auth_code),SlotSet('numero_appel', numero_appel)]


#La fonction de la classe ActionGetClientDetails est de récupérer le code de vérification entré par l'utilisateur, de vérifier sa validité et de vérifier si le code correspond au code de vérification stocké dans le suivi de la conversation.
class ActionGetClientDetails(Action):
    def name(self) -> Text:
        return "action_get_client_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Récupérer le code de vérification entré par l'utilisateur
        auth_code = tracker.latest_message.get('text')
        # Récupérer type_request entré par l'utilisateur
        type_request = tracker.get_slot('type_request')
        print(f'type_request: {type_request}')
            # Récupérer le numéro de téléphone stocké dans un slot
        numero_appel = tracker.get_slot("numero_appel")
        print(f'numero_appel: {numero_appel}')
            # If the phone number slot is empty, ask the user for the phone number
        if not numero_appel:
            dispatcher.utter_message(text="Pour des raisons de sécurité, j'ai besoin de vous envoyer un code de vérification. Pourriez-vous me donner votre numéro de téléphone pour que je puisse vous l'envoyer et confirmer votre identité ?")
            return []
        # Traitez le code de vérification ici
            # Vérifier que le code entré par l'utilisateur est bien de 6 chiffres
        if not auth_code.isalnum() or len(auth_code) != 6:
            dispatcher.utter_message(text="Le code de vérification doit être composé de 6 caractères.")
            return []
        # Vérifier si le message de l'utilisateur contient un code de vérification
        code_verification = re.search(r"[A-Za-z0-9]{6}", auth_code)
        print(f'code_verification: {code_verification}')
        if code_verification:
            code = code_verification.group(0)
            

            # Récupérer le code de vérification stocké dans la variable de suivi
            stored_auth_code = tracker.get_slot('auth_code')
            print(f'stored_auth_code: {stored_auth_code}')

            # Vérifier que le code entré par l'utilisateur correspond au code stocké
            if auth_code != stored_auth_code and auth_code.isalnum():
                print(f'Comparaison des codes : {stored_auth_code} vs {auth_code}')
                dispatcher.utter_message(text="Le code de vérification est incorrect.")
                time.sleep(1)
                dispatcher.utter_message(text="Veuillez resaisir le code de vérification ou fournir à nouveau votre numéro de téléphone pour obtenir un nouveau code.")
                return []
            else:
                dispatcher.utter_message(response="utter_info_carte")

        return [SlotSet('auth_code', auth_code), SlotSet('numero_appel', numero_appel), SlotSet('type_request', type_request)]
import time


#La classe ActionGetInfo a pour fonction de récupérer les informations demandées par l'utilisateur ,lorsqu'il entre le code de verification correctement, à partir d'une base de données, en fonction du type de demande et du code de vérification fournis.
class ActionGetInfo(Action):

    def name(self) -> Text:
        return "action_get_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        type_request = tracker.get_slot('type_request')
        print(f'type_request: {type_request}')
        # Récupérer le numéro de téléphone stocké dans un slot
        numero_appel = tracker.get_slot("numero_appel")
        print(f'numero_appel: {numero_appel}')
        # Récupérer le code de vérification stocké dans la variable de suivi
        auth_code  = tracker.get_slot('auth_code')
        print(f'stored_auth_code: {auth_code}')
        
        # Récupérer le dernier message de l'utilisateur
        latest_message = tracker.latest_message.get('intent', {}).get('name')
        print(f'latest_message: {latest_message}')
        
        # Vérifier si le dernier message de l'utilisateur est l'intent "statut"
        if latest_message == "statut_offre" and type_request == "statut":
            # Exécuter la requête pour récupérer le statut de l'offre
            query = "SELECT Statut_in , CREDIT_CLEARANCE_DATE , ACCOUNT_DISCONNECT_DATE FROM donnees_clients WHERE auth_code = '{}' ".format(auth_code)
            message = "Le statut de votre SIM est : "     
        elif latest_message == "demander_forfait_actuel" and type_request == "actuel":
            # Exécuter la requête pour récupérer le statut de l'offre par défaut
            query = "SELECT offre , Prix_minute FROM donnees_clients WHERE auth_code = '{}' ".format(auth_code)
            message = "Votre offre actuelle est : "
        elif latest_message == "consulter_solde"and type_request =="solde":
            query = "SELECT Solde FROM donnees_clients WHERE auth_code = '{}' ".format(auth_code)
            message = "Le montant actuel disponible dans votre compte est : "
        elif latest_message == "suivi_bonus" and type_request =="bonus":
            query = "SELECT Bonus FROM donnees_clients WHERE auth_code = '{}' ".format(auth_code)
            message = "Vous bénéficiez d'un bonus de :  "
        elif latest_message == "volume_data" and type_request =="volume":
            query = "SELECT Volume_DATA FROM donnees_clients WHERE auth_code = '{}' ".format(auth_code)
            message = "Le volume de données dont vous disposez est : "
        else : 
             # Si l'intention de l'utilisateur n'est pas claire, demander des clarifications
            dispatcher.utter_message(text="Je n'ai pas compris votre demande. Pouvez-vous reformuler s'il vous plaît ?")
            return []

        # Connexion à la base de données
        cnx = mysql.connector.connect(user='root', password='Fayrouz@123',
                                      host='localhost',
                                      database='database', port='3306')
        cursor = cnx.cursor()

        # Exécuter la requête pour récupérer les informations du client en fonction du code de vérification et du type de requête entrés par l'utilisateur
        cursor.execute(query)

        # Récupération des résultats de la requête
        results = cursor.fetchall()

        # Vérifier si le code de vérification est correct
        if not results:
            dispatcher.utter_message(text="Code de vérification incorrect.")
        else:
            # Traitement des résultats
            for result in results:
                # Ajout de la réponse à la conversation
                
                # Vérifier si le dernier message de l'utilisateur est l'intent "statut"
                if latest_message == "statut_offre" and type_request == "statut":
                    if result[0]== "Suspendu" : 
                        
                        dispatcher.utter_message(text=message + "{}".format(result[0]))
                        time.sleep(1)
                        dispatcher.utter_message(text="Votre ligne est expirée depuis le {}".format(result[1]) + " car la période de validité a pris fin.")
                        dispatcher.utter_message(text="Vous devez recharger votre ligne avant le {}".format(result[2]) + " ,sinon elle sera définitivement désactivée.")
                        
                    elif result[0]== "Actif" : 
                        dispatcher.utter_message(text=message + "{}".format(result[0]))
            
                elif latest_message == "demander_forfait_actuel" and type_request == "actuel":
                    dispatcher.utter_message(text=message + "{}".format(result[0]) )
                    dispatcher.utter_message ( text ="Le prix par minute de cette offre est de " + "{}".format(result[1]) + " DT")
                elif latest_message == "consulter_solde"and type_request =="solde":
            
                    dispatcher.utter_message(text=message + "{}".format(result[0]) + " DT")
                elif latest_message == "suivi_bonus" and type_request =="bonus":
           
                    dispatcher.utter_message(text=message + "{}".format(result[0]) + " DT")
                elif latest_message == "volume_data" and type_request =="volume":
            
                    dispatcher.utter_message(text=message + "{}".format(result[0]) + " Mo")
        # Fermeture de la connexion à la base de données
        cursor.close()
        cnx.close()

        return [SlotSet('auth_code', auth_code), SlotSet('numero_appel', numero_appel)]



from rasa_sdk.events import UserUttered, UserUtteranceReverted
#La classe ActionGreet a pour fonction d'accueillir l'utilisateur et de lui présenter l'assistant virtuel TTbot
class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text = "Bonjour et bienvenue chez Tunisie Télécom ! Je suis TTbot, votre assistant virtuel.") 
        message2 = "utter_info"
        # envoyer le deuxième message
        dispatcher.utter_message(response = message2)

        return [UserUtteranceReverted()]

#La classe ActionInfoCarte a pour fonction d'afficher des informations sur la carte de l'utilisateur
class ActionInfoCarte(Action):
    def name(self) -> Text:
        return "action_info_carte"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response="utter_info_carte")
        

        return []


#La classe ActionDefault a pour fonction de gérer les actions par défaut lorsqu'aucune autre action n'est appropriée. (elle active le fallback classifier qui se trouve dans la configuration de rasa)
class ActionDefault(Action):
    def name(self) -> Text:
        return "action_default"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Veuillez reformuler votre demande ou contacter notre service clientèle au 1298."
        # envoyer le deuxième message
        dispatcher.utter_message(message)

        return []
    




