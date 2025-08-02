from confluent_kafka import Producer
import json
import uuid

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

# Новые данные из сообщения
NEW_DATA = {
    "id": str(uuid.uuid4()),  # Генерируем новый уникальный ID
    "source": "urn:event:from:sn_rt-t",
    "type": "operationRequest",
    "specversion": "1.0"
}

NEW_EXTENSIONS = {
    "cloudid": "d55e02c0-6533-49c2-8f01-d77d7068b51c",
    "containername": "vpcName",
    "correlationid": "92f719f0-32ee-4908-9465-c1fbb0c75944", #str(uuid.uuid4()),  # Генерируем новый correlationid
    "iamcontext": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "operationtype": "createResource",  # Обновленное значение
    "resourcegroupname": "baseRGName",
    "resourceid": "417bbaa3-deb2-48a2-af98-cf87e2ba0eb9",
    "resourcetype": "Route",
    "responsetoq": "sn_rt-t.response",
    "xiamctx": "{\"tid\":\"c08ec7d4-90c7-40d1-ad66-e5d04f4c297a\",\"rid\":\"7cec41db-1eca-4fb6-9114-9f93770fd43d\",\"uid\":\"0cb5c597-e858-4b5e-9c0d-cae1cb9ca8f0\",\"sid\":\"4c367b48-b727-49f2-a996-5c1ae454d881\",\"aid\":\"681cb42d-b321-4cf8-94f2-f021d8fb2f40\",\"ak\":\"0b4543cb-340f-406f-8f75-456e9dfc291a\",\"ln\":\"en\",\"scope\":\"read write\",\"exp\":1783070753,\"iat\":1751534753,\"email\":\"user@example.com\",\"azcs\":[{},{}]}",
    "xiamtkn": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "xsessioncontext": "eyJ0ZW5hbnRJZCI6ImMwOGVjN2Q0LTkwYzctNDBkMS1hZDY2LWU1ZDA0ZjRjMjk3YSIsInVzZXJJZCI6IjBjYjVjNTk3LWU4NTgtNGI1ZS05YzBkLWNhZTFjYjljYThmMCIsInVzZXJOYW1lIjoiZW4ifQ=="
}

# Обновленные данные ресурса
NEW_DATA_PAYLOAD = {
    "name": "route-CxResourceName[value=tech-subnet-rt-33]",
    "displayName": "route-displayName",
    "description": "technical subnet",
    "routeTableId": "d7ddf734-f8f6-4e5a-869b-2cdaac890659",
    "resourceCategory": "SERVICE",
    "specification": {
        "destinationPrefix": "192.169.1.0/24",
        "nextHopAddress": "direct",  # Изменено значение
        "priority": 0
    },
    "routeRole": "DIRECT"  # Изменено значение
}

# Формируем заголовки Kafka в формате ce_*
headers = []
for key, value in NEW_DATA.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

for key, value in NEW_EXTENSIONS.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

# Настройки отправки
TOPIC = "rttb_rt-t.request"
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