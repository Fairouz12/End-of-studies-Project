from flask import Flask, render_template, url_for, jsonify, request

import json
from flask import session
from flask import redirect
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/get_chatbot')
def get_chatbot():
    return render_template('TTBOT.html')

@app.route('/')
def home():
    # Get the URL for the chatbot application image
    chatbot_app_image = url_for('static', filename='chatbot_app.png')
    # Get the URL for the logo image
    logo_image = url_for('static', filename='telecom1.png')
    return render_template('home.html', chatbot_app_image=chatbot_app_image, logo_image=logo_image)

@app.route("/TTBOT")
def ttbot():
    # Get the URL for the chatbot icon image
    chatbot_icone = url_for('static', filename='chaticon.png')

    return render_template("TTBOT.html", chatbot_icone=chatbot_icone)


# Cette fonction crée une route pour l'API Flask à l'URL "/get"
@app.route("/get")
# Cette fonction récupère la réponse du bot
def get_bot_response():
    
    userText = str(request.args.get('msg'))
    
    if not userText:
        data = json.dumps({"sender": "Rasa", "message": "/greet"})
    else:
        data = json.dumps({"sender": "Rasa", "message": userText})

    # Ajoute des en-têtes de requête
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # Envoie une requête POST à l'URL spécifiée pour obtenir la réponse du bot
    response = requests.post('http://localhost:5005/webhooks/rest/webhook', data=data, headers=headers)
    # Convertit la réponse JSON en dictionnaire Python
    response = response.json()
    # Initialise une liste pour stocker les messages du bot
    messages = []
    # Initialise une chaîne vide pour stocker le code HTML des boutons
    button_html = ""
    # Boucle à travers chaque réponse du bot
    for r in response:
        # Récupère le texte de la réponse
        text = r['text']
        # Récupère les entités (s'il y en a) de la réponse
        entities = r.get('entities', {})
        # Si des entités sont présentes, les remplace par leur valeur dans le texte de la réponse
        if entities:
            for entity, value in entities.items():
                text = text.replace(f"[{entity}]", value)
        # Récupère les boutons (s'il y en a) de la réponse
        buttons = r.get('buttons', [])
        # Boucle à travers chaque bouton
        for button in buttons:
            # Récupère le titre du bouton
            buttonTitle = button['title']
            # Récupère le payload du bouton et le remplace par des valeurs spécifiques
            buttonPayload = button['payload'].replace('{{"forfait":"50Mo"}}', '{"forfait":"50Mo"}')
            buttonPayload = buttonPayload.replace('{{"forfait_ehdia":"200Mo"}}', '{"forfait_ehdia":"200Mo"}')
            buttonPayload = buttonPayload.replace('{{"type_request":"statut"}}', '{"type_request":"statut"}')
            # Ajoute le bouton au code HTML
            button_html += f'<button class="btn btn-primary" data-payload=\'{buttonPayload}\'>{buttonTitle}</button>'
        # Si des boutons sont présents, les ajoute au code HTML
        if button_html:
            button_html = f'<div id="button-container">{button_html}</div>'
        # Ajoute le texte de la réponse à la liste de messages
        messages.append(text)
    # Joint tous les messages en une chaîne avec des séparateurs spécifiques et ajoute le code HTML des boutons à la fin
    bot_responses = '|||'.join(messages) + '|||' + button_html
    # Retourne la réponse finale
    return bot_responses



if __name__ == "__main__":
	app.run(debug = True)