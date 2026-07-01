from dotenv import load_dotenv
load_dotenv()

import boto3, os, time
from scraper import scrape
from database import salvar

sqs = boto3.client('sqs',
    region_name='us-east-2',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET']
)
QUEUE_URL = os.environ['SQS_QUEUE_URL']

def processar(mensagem, receipt_handle):
    try:
        dados = scrape(mensagem)  # passa o body completo (JSON ou URL)
        salvar(dados)
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
        print(f'✓ Processado: {dados["url"][:80]}')
    except Exception as e:
        print(f'✗ Erro: {e}')

while True:
    resp = sqs.receive_message(QueueUrl=QUEUE_URL, WaitTimeSeconds=20, MaxNumberOfMessages=1)
    msgs = resp.get('Messages', [])
    for msg in msgs:
        processar(msg['Body'], msg['ReceiptHandle'])
    if not msgs:
        time.sleep(1)