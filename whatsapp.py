import requests



def getMessagesUnread():
    response = requests.get("https://ecommerceflow.com.br/waha/api/default/chats?limit=5&offset=0")    
    response = response.json()
    messages_unread = []
    for chat in response:
        if chat.get("unreadCount", 0) > 0:
            name = chat.get("name", "")
            isGroup = chat.get("isReadOnly", None)
            messages = requests.get(f"https://ecommerceflow.com.br/waha/api/default/chats/{chat.get("id").get("_serialized", "")}/messages?limit={chat.get("unreadCount", 0)}&offset=0")
            messages = messages.json()
            for message in messages:    
                if message.get("hasMedia") == False:
                    id_to_send = message.get("from", "")
                    if len(message.get("_data", {}).get("id", {}).get("participant", {}).get("user", "")) > 1:
                        from_user = requests.get(f"https://ecommerceflow.com.br/waha/api/contacts?contactId={message.get("_data", {}).get("id", {}).get("participant", {}).get("user", "")}&session=default")
                        from_user = from_user.json().get("name", "")
                    else:
                        from_user = name
                    
                    if isGroup == False:
                        body = {
                            "id_to_send": id_to_send,
                            "isGroup": True,
                            "group": name,
                            "from":from_user,
                            "message": message.get("body", ""),
                        }
                    else:
                        body = {
                            "id_to_send": id_to_send,
                            "isGroup": False,
                            "from":from_user,
                            "message": message.get("body", ""),
                        }
                    messages_unread.append(body)
    return messages_unread


def send_messages(send_id, message):
    response = requests.post("https://ecommerceflow.com.br/waha/api/sendText", {
        "chatId": f"{send_id}",
        "text": f"{message}",
        "session": "default"
    })
    if response.status_code == 200:
        return "Mensagem enviada com sucesso"
    else:
        return "Erro ao enviar mensagem"



            
        
        
if __name__ == "__main__":
    # print(getMessagesUnread())
    print(send_messages("553791332517@c.us", "teste"))