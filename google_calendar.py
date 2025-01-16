import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks"
]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def create_event(summary, description, start_time, end_time, location=""):
    """Cria um evento no Google Calendar."""
    creds = get_credentials()
    try:
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": end_time, "timeZone": "America/Sao_Paulo"},
            "location": location,
        }
        event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        return f"Evento criado com sucesso: {event.get('htmlLink')}"
    except HttpError as error:
        return f"Erro ao criar evento: {error}"


def create_task(title, notes="", due_date=None):
    """Cria uma tarefa no Google Tasks."""
    creds = get_credentials()
    try:
        service = build("tasks", "v1", credentials=creds)
        task = {"title": title, "notes": notes}
        # if due_date:
        #     task["due"] = due_date
        task = service.tasks().insert(tasklist="@default", body=task).execute()
        return f"Tarefa criada com sucesso: {task.get('id')}"
    except HttpError as error:
        return f"Erro ao criar tarefa: {error}"


def list_events(max_events=10):
    """Lista os próximos eventos do Google Calendar."""
    creds = get_credentials()
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_events,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "Nenhum evento futuro encontrado."

        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(
                f"Data: {start} | Evento: {event['summary']} | Descrição: {event.get('description', 'N/A')} | Local: {event.get('location', 'N/A')}"
            )
        return event_list
    except HttpError as error:
        return f"Ocorreu um erro: {error}"

def list_tasks(max_tasks=10):
    """Lista as próximas tarefas do Google Tasks."""
    creds = get_credentials()
    try:
      service = build("tasks", "v1", credentials=creds)
      results = service.tasks().list(tasklist="@default", maxResults=max_tasks).execute()
      tasks = results.get("items", [])

      if not tasks:
        return "Nenhuma tarefa encontrada."
      
      task_list = []
      for task in tasks:
        due_date = task.get("due", "N/A")
        task_list.append(
            f"Título: {task['title']} | Descrição: {task.get('notes','N/A')} | Data de Vencimento: {due_date}"
        )
      return task_list
    except HttpError as error:
      return f"Ocorreu um erro: {error}"

if __name__ == "__main__":
    # Exemplo de uso:
    # Cria um evento
    start_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
    end_time = (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat()
    print(
        create_event(
            "Reunião de Teste", "Reunião para testar a API", start_time, end_time, "Sala 1"
        )
    )

    # Cria uma tarefa
    # due_date = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
    # print(create_task("Comprar Leite", "Ir ao mercado comprar leite", due_date))

    # Lista os próximos eventos
    # print("\nPróximos eventos:")
    # print(list_events())
    
    # Lista as próximas tarefas
    # print("\nPróximas tarefas:")
    # print(list_tasks())