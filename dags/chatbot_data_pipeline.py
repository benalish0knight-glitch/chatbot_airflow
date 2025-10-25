from __future__ import annotations
import os
import pendulum

from airflow.decorators import dag, task

from airflow.models.variable import Variable

# Importa as funções do seu projeto
from scripts.chatbot_script import extract_and_process_data
from modules.messaging_service import send_message_to_group

# Configurações da DAG
DAG_ID = os.getenv("DAG_ID")
SCHEDULE = os.getenv("SCHEDULE") # Executa de segunda a sexta-feira às 8:00 AM
CONN_ID = os.getenv("CONN_ID")

@dag(
    dag_id=DAG_ID,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=SCHEDULE,
    catchup=False,
    tags=["chatbot", "data_pipeline", "messaging"],
    doc_md=__doc__,
)
def chatbot_data_pipeline_dag():
    """
    DAG do Airflow para orquestrar a extração, processamento de dados do chatbot
    e o envio de um relatório para um grupo de mensageria.
    """

    @task(task_id="extract_and_process_data_task")
    def process_data():
        """
        Executa a lógica de extração e processamento de dados do chatbot.
        Retorna o conteúdo da mensagem formatada.
        """
        message_content = extract_and_process_data()
        return message_content

    @task(task_id="send_message_to_group_task")
    def send_report(message_content: str):
        """
        Envia o relatório processado para o grupo de mensageria.
        
        Requer a variável do Airflow 'messaging_group_id' configurada.
        Requer a conexão do Airflow 'messaging_conn_id' configurada.
        """
        # Obtém o ID do grupo de mensageria das Variáveis do Airflow
        group_id = Variable.get("messaging_group_id", default_var=None)
        
        if not group_id:
            raise ValueError("A Variável do Airflow 'messaging_group_id' não está configurada.")
        
        send_message_to_group(
            message_content=message_content,
            conn_id=CONN_ID,
            group_id=group_id
        )

    # Define a ordem de execução das tarefas
    message_data = process_data()
    send_report(message_data)

chatbot_data_pipeline_dag()