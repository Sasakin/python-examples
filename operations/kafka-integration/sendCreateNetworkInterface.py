from confluent_kafka import Producer
import json
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

# Конфигурация Kafka
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'cloudevent-producer',
    'message.timeout.ms': 45000,
}

# Инициализируем Producer
producer = Producer(conf)

# Callback для доставки
def delivery_report(err, msg):
    if err:
        print(f'❌ Ошибка доставки сообщения: {err}')
    else:
        print(f'✅ Сообщение успешно отправлено в {msg.topic()} [{msg.partition()}]')

CLOUD_ID = os.getenv("CLOUD_ID")
RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")        

# Новые данные из сообщения
NEW_DATA = {
    "id": str(uuid.uuid4()),  # Генерируем новый уникальный ID
    "source": "urn:event:from:sn_rt-t",
    "type": "operationRequest",
    "specversion": "1.0"
}

NEW_EXTENSIONS = {
    "requestid": str(uuid.uuid4()),
    "messagetype": "REQUEST",
    "resourceservice": "RESOURCE_TYPE",
    "domaintypesource": "RESOURCE_TYPE",
    "domaintypetarget": "RESOURCE_TYPE",
    "correlationid": "92f719f0-32ee-4908-9465-c1fbb0c75944", #str(uuid.uuid4()),  # Генерируем новый correlationid
    "operationtype": "CREATE",  # Обновленное значение
    "resourceid": "417bbaa3-deb2-48a2-af98-cf87e2ba0eb9",
    "resourcetype": "NETWORK_INTERFACE",
    "responseto": "vpc_rt-t.response",
    "xiamctx": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "xiamtkn": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
}

# Обновленные данные ресурса
NEW_DATA_PAYLOAD = {
  "name": "test-Interface8",
  "displayName": "test-Interface1",
  "description": "test interface",
  "cloudId": CLOUD_ID,
  "resourceGroupName": RESOURCE_GROUP_NAME,
  "vpcName": "vpcName",
  "specification": {
     "subnet": {"id" : "9670fdd4-1b1e-442f-9ae3-744631400815"},
    "ipConfigurations": [],
    "securitySettings": {
      "enableSecurity": "false",
      #"securityGroups": [
      #  "f47ac10b-58cc-4372-a567-0e02b2c3d480"
      #],
      "allowedAddresses": [
        "10.0.0.6",
        "10.0.0.7",
        "10.0.0.8"
      ],
      "adminState": "adminState"
    }
  }
}


# Формируем заголовки Kafka в формате ce_*
headers = []
for key, value in NEW_DATA.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

for key, value in NEW_EXTENSIONS.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

# Настройки отправки
TOPIC = "sn_rt-t.request"
RESOURCE_KEY = NEW_EXTENSIONS["resourceid"].encode('utf-8')  # Используем resourceid как ключ

# Преобразуем Data в JSON
message_value = json.dumps(NEW_DATA_PAYLOAD, ensure_ascii=False).encode('utf-8')

# Отправляем сообщение
producer.produce(
    TOPIC,
    key=RESOURCE_KEY,
    value=message_value,
    headers=headers,
    callback=delivery_report
)

# Ждем завершения отправки
producer.poll(0)
producer.flush(timeout=10)
print("✅ Сообщение отправлено с обновленными данными")