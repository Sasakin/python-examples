import os
import ssl
import socket
import urllib.request
from tinkoff.invest import CandleInterval, Client
from dotenv import load_dotenv
# Загрузить переменные окружения из файла .env
load_dotenv()

TOKEN = os.environ["INVEST_TOKEN"]

# URL для скачивания корневых сертификатов
CACERT_URL = "https://api-invest.tinkoff.ru"
host = "api-invest.tinkoff.ru"

# Путь для сохранения сертификата
CACERT_PATH = "cacert.pem"

def loadCert():
    # Скачиваем сертификат, если он еще не скачан
    if not os.path.exists(CACERT_PATH):
        print("Скачивание корневых сертификатов...")
        context = ssl.create_default_context()

        #     Установка параметра, чтобы контролировать проверку сертификата
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        port = 443

        # Установка соединения с веб-сайтом и получение сертификата
        certificate = ssl.get_server_certificate((host, port))
        with open(CACERT_PATH, "wb") as file:
            file.write(certificate.encode())
        print("Сертификаты успешно скачаны.")
        os.environ['SSL_CERT_FILE'] = os.path.abspath(CACERT_PATH)

# Устанавливаем переменную окружения SSL_CERT_FILE
#os.environ['SSL_CERT_FILE'] = os.path.abspath(CACERT_PATH)

def check_ssl_cert(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            print(f"Сертификат для {hostname}:")
            print(cert)

import certifi
import requests

def clientLogic():
    with Client(TOKEN) as client:
        print(client.orders)
        print(client.users.get_accounts())
        for candle in client.get_all_candles(
            figi="BBG004730N88",
            from_=now() - timedelta(days=365),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            ):
            print(candle)


def main():
    loadCert()
    clientLogic()

if __name__ == "__main__":
    main()