import boto3
from datetime import datetime, timedelta
import requests

# Configuração do webhook do Slack
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'  # Substitua pelo URL do seu webhook

def send_slack_notification(message):
    payload = {'text': message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"Erro ao enviar notificação para o Slack: {response.status_code}, {response.text}")

def check_aws_health():
    client = boto3.client('health', region_name='us-east-1')  # A AWS Health API é global, mas você precisa especificar uma região

    # Define o intervalo de tempo para buscar eventos recentes
    end_time = datetime.utcnow().isoformat() + 'Z'  # Adiciona 'Z' para indicar UTC
    start_time = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'  # Últimos 30 dias

    try:
        # Obtém eventos de saúde recentes
        response = client.describe_events(
            filter={
                'startTimes': [start_time],
                'endTimes': [end_time],
                'eventStatusCodes': ['open', 'upcoming', 'resolved']
            }
        )
        
        events = response.get('events', [])
        
        if not events:
            print("Nenhum evento recente encontrado.")
            return
        
        # Construa a mensagem para o Slack
        slack_message = "Eventos recentes na AWS Health:\n"
        
        for event in events:
            event_arn = event.get('arn')
            service = event.get('service')
            event_type = event.get('eventTypeCode')
            description = event.get('description', 'Sem descrição disponível')
            slack_message += (f"Evento ARN: {event_arn}\n"
                              f"Serviço: {service}\n"
                              f"Tipo de Evento: {event_type}\n"
                              f"Descrição: {description}\n"
                              "-" * 40 + "\n")
        
        # Envia a notificação para o Slack
        send_slack_notification(slack_message)
    
    except Exception as e:
        print(f"Erro ao consultar a AWS Health API: {e}")
        send_slack_notification(f"Erro ao consultar a AWS Health API: {e}")

if __name__ == "__main__":
    check_aws_health()
