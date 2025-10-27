from __future__ import annotations

import pendulum
import os

from airflow.decorators import dag, task
# from airflow.providers.telegram.operators.telegram import TelegramOperator
from airflow.providers.telegram.operators.telegram import TelegramOperator
from dotenv import load_dotenv
# from airflow.providers.telegram.hooks.telegram import TelegramHook
# from airflow.operators.python import PythonOperator
# Variáveis de configuração (podem ser as mesmas do DAG principal)

load_dotenv()
TELEGRAM_CONN_ID = os.getenv("CONNECTION_ID")
CHAT_ID = os.getenv("HOST")

@dag(
    dag_id="telegram_chatbot_health_check",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 * * *",  # Executa diariamente às 09:00 UTC
    catchup=False,
    tags=["chatbot", "health_check", "monitoring"],
    default_args={
        "owner": "airflow",
        "retries": 3,
        "retry_delay": pendulum.duration(minutes=5),
    }
)
def telegram_chatbot_health_check_dag():
    """
    DAG para realizar verificações de saúde e monitoramento do serviço
    do chatbot do Telegram.
    """

    @task(retries=0)  # Não queremos que esta task tente novamente, se falhar, a notificação deve ser imediata
    def check_bot_service_status():
        """
        Verifica se o serviço do chatbot está ativo.
        Na vida real, faria uma chamada de API para o servidor do bot
        ou verificaria o status do processo.
        """
        import random
        # Simula uma verificação de status
        is_up = random.choice([True, True, True, False]) # 75% de chance de estar UP
        
        if not is_up:
            raise Exception("O serviço do Chatbot parece estar OFFLINE ou com erro de conexão.")
        
        return "Serviço do Chatbot está UP e respondendo."

    @task
    def check_telegram_api_connectivity():
        """
        Verifica a conectividade básica com a API do Telegram.
        Pode usar o método getMe da API do Telegram.
        """
        # Em um cenário real, você faria uma chamada HTTP para a API do Telegram
        # Exemplo: requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        return "Conexão com a API do Telegram bem-sucedida."

    send_success_notification = TelegramOperator(
        task_id="notify_health_check_success",
        telegram_conn_id=TELEGRAM_CONN_ID,
        chat_id=CHAT_ID,
        text="✅ *Verificação de Saúde do Chatbot Concluída*:\n"
             "{{ task_instance.xcom_pull(task_ids='check_bot_service_status') }}\n"
             "{{ task_instance.xcom_pull(task_ids='check_telegram_api_connectivity') }}",
        # parse_mode="Markdown",
        trigger_rule="all_success"
    )

    # Definição do fluxo
    status_check = check_bot_service_status()
    api_check = check_telegram_api_connectivity()

    [status_check, api_check] >> send_success_notification

# Instanciação da DAG
telegram_chatbot_health_check_dag()