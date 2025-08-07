import os
import json
import uuid
from confluent_kafka import Producer

# Опционально: загрузка из .env (удалите, если не используете)
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

# === Получаем cloudId и resourceGroupName из переменных окружения ===
CLOUD_ID = os.getenv("CLOUD_ID")
RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")

# Проверка обязательных переменных
if not CLOUD_ID:
    raise EnvironmentError("Переменная окружения CLOUD_ID не установлена.")
if not RESOURCE_GROUP_NAME:
    raise EnvironmentError("Переменная окружения RESOURCE_GROUP_NAME не установлена.")

# === Данные CloudEvent (без изменений) ===
NEW_DATA = {
    "id": str(uuid.uuid4()),
    "source": "urn:event:from:sn_rt-t",
    "type": "operationRequest",
    "specversion": "1.0"
}

NEW_EXTENSIONS = {
    "resourceid": str(uuid.uuid4()),
    "messagetype": "REQUEST",
    "domaintypesource": "RESOURCE_TYPE",
    "domaintypetarget": "RESOURCE_TYPE",
    "resourceservice": "RESOURCE_TYPE",
    "correlationid": "92f719f0-32ee-4908-9465-c1fbb0c75944",
    "operationtype": "CREATE",
    "resourcetype": "SUBNET",
    "responseto": "vpc_rt-t.response",
    "xiamctx": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "xiamtkn": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
}

# Обновленные данные ресурса
NEW_DATA_PAYLOAD = {
    "name": "tech-subnet-rt-3",
    "description": "technical subnet",
    "availabilityZone": "zone1",
    "cloudId": CLOUD_ID,  # ← из переменной окружения
    "resourceCategory": "SERVICE",
    "resourceGroupName": RESOURCE_GROUP_NAME,  # ← из переменной окружения
    "vpcName": "lps-dummy",
    "specification": {
        "ipConfigurationBlocks": [
            {
                "cidr": "192.169.1.0/24",
                "ipVersion": 4,
                "dnsServers": [
                    {
                        "ipAddress": "8.8.8.8",
                        "serverName": "cloudx-dns"
                    },
                    {
                        "ipAddress": "8.8.4.4",
                        "serverName": "cloudx-dns2"
                    }
                ],
                "enableDhcp": True,
                "allocationPools": [
                    {
                        "start": "192.169.1.10",
                        "end": "192.169.1.100"
                    }
                ],
                "gatewayIp": "192.169.1.1",
                "vrf": "prod-vrf"
            }
        ],
        "mtu": 1500,
        "networkType": "vlan",
        "physicalNetworkName": "provider",
        "segmentationId": 109,
        "subnetRole": "service"
    }
}

# Формируем заголовки Kafka в формате ce_*
headers = []
for key, value in NEW_DATA.items():
    headers.append((f"ce_{key}", str(value).encode('utf-8')))

for key, value in NEW_EXTENSIONS.items():
    headers.append((f"ce_{key}", str(value).encode('utf-8')))

# Настройки отправки
TOPIC = "sn_rt-t.request"
RESOURCE_KEY = NEW_EXTENSIONS["resourceid"].encode('utf-8')

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