from flask import Flask, request, jsonify
import json
from main import process_user_input
app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_message():
    try:
        data = request.get_json()
        print(f"Body recebido: {data}")
        if data.get("payload", {}).get("from", "") == "553791332517@c.us" and "Bot:" not in data.get("payload", {}).get("body", ""):
            process_user_input(data.get("payload", {}).get("body", ""));
        return jsonify({"message": "Mensagem recebida com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return jsonify({"error": "Erro ao processar a mensagem."}), 400
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5500)