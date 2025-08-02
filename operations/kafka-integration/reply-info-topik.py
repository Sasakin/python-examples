import os
from dotenv import load_dotenv
from confluent_kafka import Consumer, Producer

# Загружаем переменные из .env
load_dotenv()

# Конфигурация удалённого Kafka сервера
REMOTE_BOOTSTRAP_SERVERS = os.getenv('REMOTE_BOOTSTRAP_SERVERS')
SASL_USERNAME = os.getenv('SASL_USERNAME')
SASL_PASSWORD = os.getenv('SASL_PASSWORD')

# Конфигурация локального Kafka сервера
LOCAL_BOOTSTRAP_SERVERS = os.getenv('LOCAL_BOOTSTRAP_SERVERS')
REMOTE_TOPIC = 'stack_cn-t_rabbitmq.neutron.info'
LOCAL_TOPIC = 'stack_cn-t_rabbitmq.neutron.info'

# Конфигурация удалённого потребителя
consumer_conf = {
    'bootstrap.servers': REMOTE_BOOTSTRAP_SERVERS,
    'group.id': 'mirror-group',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanisms': 'SCRAM-SHA-512',
    'sasl.username': SASL_USERNAME,
    'sasl.password': SASL_PASSWORD,
    'auto.offset.reset': 'latest'
}

# Конфигурация локального производителя
producer_conf = {
    'bootstrap.servers': LOCAL_BOOTSTRAP_SERVERS
}

# Инициализация потребителя
consumer = Consumer(consumer_conf)
consumer.subscribe([REMOTE_TOPIC])

# Инициализация производителя
producer = Producer(producer_conf)

# Функция для обработки результата отправки сообщения
def delivery_report(err, msg):
    if err:
        print(f'Ошибка при отправке: {err}')
    else:
        print(f'Сообщение успешно отправлено в {msg.topic()} [{msg.partition()}]')

print("Запуск потребителя...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)  # Ждём сообщение 1 секунду

        if msg is None:
            continue  # Таймаут — продолжаем ожидание

        if msg.error():
            print(f"Ошибка при получении сообщения: {msg.error()}")
            continue

        print(f"Получено сообщение: {msg.value()}")

        # Отправляем сообщение в локальный топик
        producer.produce(
            LOCAL_TOPIC,
            key=msg.key(),
            value=msg.value(),
            callback=delivery_report
        )

        # Обрабатываем очередь доставки
        producer.poll(0)

except KeyboardInterrupt:
    print("Остановка потребителя...")

finally:
    # Ожидаем отправки всех оставшихся сообщений
    producer.flush(timeout=10)
    consumer.close()
    producer.close()