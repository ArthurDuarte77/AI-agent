from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/bot', methods=['POST'])
def receive_message():
    """Endpoint que recebe as mensagens do webhook."""
    try:
        data = request.get_json()
        print(f"Body recebido: {data}")
        return jsonify({"message": "Mensagem recebida com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return jsonify({"error": "Erro ao processar a mensagem."}), 400
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5050)