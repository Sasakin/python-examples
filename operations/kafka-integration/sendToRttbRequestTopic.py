from confluent_kafka import Producer
import json

# Конфигурация Kafka
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'cloudevent-producer'
}

# Инициализируем Producer
producer = Producer(conf)

# Callback для доставки
def delivery_report(err, msg):
    if err:
        print(f'Ошибка доставки сообщения: {err}')
    else:
        print(f'Сообщение успешно отправлено в {msg.topic()} [{msg.partition()}]')

# CloudEvent Attributes
attributes = {
    "id": "1ce9a758-3388-4fc3-9b99-d8312072cb00",
    "source": "urn:event:from:sn_rt-t",
    "type": "operationRequest",
    "specversion": "1.0"
}

# CloudEvent Extensions
extensions = {
    "cloudid": "d55e02c0-6533-49c2-8f01-d77d7068b51c",
    "containername": "vpcName",
    "correlationid": "350159af-e377-4996-914e-8db41be9db5b",
    "iamcontext": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "operationtype": "createResource",
    "resourcegroupname": "baseRGName",
    "resourceid": "417bbaa3-deb2-48a2-af98-cf87e2ba0eb9",
    "resourcetype": "Route",
    "responsetoq": "sn_rt-t.response",
    "xiamctx": "{\"tid\":\"c08ec7d4-90c7-40d1-ad66-e5d04f4c297a\",\"rid\":\"7cec41db-1eca-4fb6-9114-9f93770fd43d\",\"uid\":\"0cb5c597-e858-4b5e-9c0d-cae1cb9ca8f0\",\"sid\":\"4c367b48-b727-49f2-a996-5c1ae454d881\",\"aid\":\"681cb42d-b321-4cf8-94f2-f021d8fb2f40\",\"ak\":\"0b4543cb-340f-406f-8f75-456e9dfc291a\",\"ln\":\"en\",\"scope\":\"read write\",\"exp\":1783070753,\"iat\":1751534753,\"email\":\"user@example.com\",\"azcs\":[{},{}]}",
    "xiamtkn": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiJjMDhlYzdkNC05MGM3LTQwZDEtYWQ2Ni1lNWQwNGY0YzI5N2EiLCJyaWQiOiI3Y2VjNDFkYi0xZWNhLTRmYjYtOTExNC05ZjkzNzcwZmQ0M2QiLCJ1aWQiOiIwY2I1YzU5Ny1lODU4LTRiNWUtOWMwZC1jYWUxY2I5Y2E4ZjAiLCJzaWQiOiI0YzM2N2I0OC1iNzI3LTQ5ZjItYTk5Ni01YzFhZTQ1NGQ4ODEiLCJhaWQiOiI2ODFjYjQyZC1iMzIxLTRjZjgtOTRmMi1mMDIxZDhmYjJmNDAiLCJhayI6IjBiNDU0M2NiLTM0MGYtNDA2Zi04Zjc1LTQ1NmU5ZGZjMjkxYSIsImxuIjoiZW4iLCJzY29wZSI6InJlYWQgd3JpdGUiLCJleHAiOjE3ODMwNzA3NTMsImlhdCI6MTc1MTUzNDc1MywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiYXpjcyI6W3sicm9sZXMiOlsicm9sZTEiLCJyb2xlMiJdfSx7InJvbGVzIjpbInJvbGUzIl19XX0.i64HqCVK0kfgjajk8GIpc0vo4ZJZZ02ZzS1pqleGRwM",
    "xsessioncontext": "eyJ0ZW5hbnRJZCI6ImMwOGVjN2Q0LTkwYzctNDBkMS1hZDY2LWU1ZDA0ZjRjMjk3YSIsInVzZXJJZCI6IjBjYjVjNTk3LWU4NTgtNGI1ZS05YzBkLWNhZTFjYjljYThmMCIsInVzZXJOYW1lIjoiZW4ifQ=="
}

# Тело сообщения — только Data
data = {
    "name": "route-CxResourceName[value=tech-subnet-rt-33]",
    "displayName": "route-displayName",
    "description": "technical subnet",
    "routeTableId": "dc3f780f-ecf5-4a48-a55a-13b62d9bc8d9",
    "resourceCategory": "SERVICE",
    "specification": {
        "destinationPrefix": "192.169.1.0/24",
        "nextHopAddress": "10.0.0.6",
        "priority": 0
    },
    "routeRole": "STATIC"
}

# Формируем заголовки Kafka в формате ce_*
headers = []
for key, value in attributes.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

for key, value in extensions.items():
    headers.append((f"ce_{key}", value.encode('utf-8')))

# Топик, куда отправлять
topic = "rttb_rt-t.request"

# Преобразуем Data в JSON
message_value = json.dumps(data).encode('utf-8')

# Отправляем сообщение
producer.produce(topic, key="4137bbaa3-deb2-48a2-af98-cf87e2ba0eb9", value=message_value, headers=headers, callback=delivery_report)

# Ждём завершения отправки
producer.poll(0)
producer.flush(timeout=10)
print("Готово.")