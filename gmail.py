import os.path
import base64
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constantes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
SENDER_EMAIL = "bolivarartur77@gmail.com"


def authenticate():
    """Autentica e retorna o serviço Gmail."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def create_message(sender, to, subject, message_text):
    """Cria uma mensagem de e-mail."""
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_email(receiver_email, subject, message_text):
    """Envia uma mensagem de e-mail."""
    service = authenticate()
    if not service:
        print("Falha na autenticação.")
        return None

    message = create_message(
        SENDER_EMAIL, receiver_email, subject, message_text
    )
    try:
        message = (
            service.users().messages().send(userId="me", body=message).execute()
        )
        print(f'Mensagem enviada com ID: {message["id"]}')
        return message
    except HttpError as error:
        print(f"Ocorreu um erro ao enviar: {error}")
        return None


def get_email_body(msg):
    """
    Obtém o corpo de um e-mail do Gmail, preferindo texto plano e, se não disponível, HTML (removendo tags).

    Args:
        msg (dict): Dicionário representando o e-mail do Gmail (contém a chave 'id').

    Returns:
        str: O corpo do e-mail como string, ou string vazia em caso de erro ou se nenhum formato de texto for encontrado.
    """
    service = authenticate()
    if not service:
        print("Falha na autenticação.")
        return ""
    try:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )
        payload = msg["payload"]
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode()
                    return body  # Retorna imediatamente se encontrar text/plain

        # Se não encontrou text/plain, tenta pegar HTML e remover as tags
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/html":
                    html_body = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode()
                    soup = BeautifulSoup(html_body, "html.parser")
                    body = soup.get_text(separator="\n", strip=True)
                    return body
        elif payload.get("mimeType") == "text/html":
            html_body = base64.urlsafe_b64decode(
                payload["body"]["data"]
            ).decode()
            soup = BeautifulSoup(html_body, "html.parser")
            body = soup.get_text(separator="\n", strip=True)
            return body
        elif payload.get("mimeType") == "text/plain":
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
            return body.strip()

        return body  # Retorna string vazia se não encontrar nenhum formato de texto

    except HttpError as error:
        print(f"Erro ao obter o corpo do e-mail: {error}")
        return ""


def read_emails(max_results=10, unread_only=False, keywords=None):
    """Lê e-mails do Gmail, com opções de filtro."""
    service = authenticate()
    if not service:
        print("Falha na autenticação.")
        return []
    try:
        query = "is:unread" if unread_only else ""
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results, q=query)
            .execute()
        )
        messages = results.get("messages", [])

        email_list = []
        if messages:
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )
                payload = msg["payload"]
                headers = payload["headers"]
                sender = next(
                    (
                        header["value"]
                        for header in headers
                        if header["name"] == "From"
                    ),
                    None,
                )
                subject = next(
                    (
                        header["value"]
                        for header in headers
                        if header["name"] == "Subject"
                    ),
                    None,
                )
                body = get_email_body(message)

                if not subject:
                    subject = ""
                if not body:
                    body = ""
                if keywords:
                    if any(
                        keyword.lower() in subject.lower()
                        or keyword.lower() in body.lower()
                        for keyword in keywords
                    ):
                        email_list.append(
                            {"sender": sender, "subject": subject, "body": body}
                        )
                else:
                    email_list.append(
                        {"sender": sender, "subject": subject, "body": body}
                    )
        return email_list

    except HttpError as error:
        print(f"Ocorreu um erro ao ler e-mails: {error}")
        return []


def main():
    """Função principal para demonstrar as funcionalidades."""

    # Exemplo de leitura de e-mails não lidos com filtro por palavra-chave
    # unread_emails = read_emails(max_results=5, unread_only=False, keywords=["fiap"])
    # if unread_emails:
    #     print("E-mails não lidos (filtrados):")
    #     for email in unread_emails:
    #         print(f"De: {email['sender']}")
    #         print(f"Assunto: {email['subject']}")
    #         print(f"Corpo: {email['body']}")
    #         print("-" * 20)
    # else:
    #     print("Nenhum e-mail não lido encontrado com esses termos.")

    # Exemplo de leitura de e-mails (sem filtro por palavra-chave)
    emails = read_emails(max_results=10)
    print("Todos os e-mails recentes (sem filtros):")
    if emails:
        for email in emails:
            print(f"De: {email['sender']}")
            print(f"Assunto: {email['subject']}")
            print(f"Corpo: {email['body']}")
            print("-" * 20)
    else:
        print("Nenhum e-mail encontrado.")

    # Exemplo de envio de e-mail
    # receiver_email = "bolivarartur77yt@gmail.com"
    # subject = "Teste de envio de e-mail"
    # message_text = "Este é um teste de envio de e-mail usando a API do Gmail."
    # send_email(receiver_email, subject, message_text)


if __name__ == "__main__":
    main()