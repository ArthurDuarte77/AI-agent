from flask import Flask, request, jsonify
import json
from main import process_user_input
app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_message():
    try:
        data = request.get_json()
        if data.get("payload", {}).get("fromMe", "") == True and "Resposta:" not in data.get("payload", {}).get("body", "") and data.get("payload", {}).get("hasMedia", "") == False and data.get("payload", {}).get("to", "") == "553791332517@c.us":
            print("Entrou no bot: ")
            process_user_input(data.get("payload", {}).get("body", ""), False);
            
        if data.get("payload", {}).get("fromMe", "") == True and "Resposta:" not in data.get("payload", {}).get("body", "") and data.get("payload", {}).get("hasMedia", "") == True and data.get("payload", {}).get("to", "") == "553791332517@c.us" and  data.get("payload", {}).get("type", "") == "ptt":
            print("Entrou no bot: ")
            process_user_input(data.get("payload", {}).get("media", "").get("url", ""), True);
            
        return jsonify({"message": "Mensagem recebida com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return jsonify({"error": f"Erro ao processar mensagem: {e}"}), 400