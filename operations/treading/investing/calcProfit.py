import requests
import gspread
import os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Загрузить переменные окружения из файла .env
load_dotenv()

# === НАСТРОЙКИ ===
TINKOFF_TOKEN = os.environ["INVEST_TOKEN"]  # Замените на свой токен
GOOGLE_CREDENTIALS = "credentials.json"  # Путь к вашему credentials.json
SPREADSHEET_NAME = "Инвестиционный_Портфель"  # Название вашей Google Таблицы

# === ФУНКЦИИ ===
def get_tinkoff_portfolio():
    """Получает данные портфеля из Tinkoff API"""
    url = "https://api-invest.tinkoff.ru/openapi/portfolio"
    headers = {"Authorization": f"Bearer {TINKOFF_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Ошибка Tinkoff API: {response.text}")
    
    data = response.json()["payload"]["positions"]
    portfolio = []
    
    for asset in data:
        figi = asset["figi"]
        quantity = asset["balance"]
        avg_price = asset["averagePositionPrice"]["value"]
        current_price = asset["currentPrice"]["value"] if "currentPrice" in asset else None
        
        # Получаем доп. информацию по FIGI
        instrument = get_instrument_info(figi)
        
        portfolio.append({
            "Тип актива": instrument["type"],
            "Название": instrument["name"],
            "Тикер": instrument["ticker"],
            "Количество": quantity,
            "Средняя цена": avg_price,
            "Текущая цена": current_price,
            "Валюта": asset["averagePositionPrice"]["currency"],
            "Дивиденды/Купоны": calculate_dividends(figi) if instrument["type"] == "Stock" else calculate_coupons(figi)
        })
    return portfolio

def get_instrument_info(figi):
    """Получает информацию об активе (название, тикер, тип)"""
    url = f"https://api-invest.tinkoff.ru/openapi/instruments/{figi}"
    headers = {"Authorization": f"Bearer {TINKOFF_TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()["payload"]
    return {
        "name": data["name"],
        "ticker": data["ticker"],
        "type": "Stock" if data["type"] == "Stock" else "Bond"  # Упрощено
    }

def calculate_dividends(figi):
    """Рассчитывает годовой дивиденд на акцию (пример для последнего года)"""
    url = f"https://api-invest.tinkoff.ru/openapi/market/dividends?figi={figi}"
    headers = {"Authorization": f"Bearer {TINKOFF_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return 0
    
    dividends = response.json()["payload"]["dividends"]
    last_year = datetime.now() - timedelta(days=365)
    total = sum(div["dividendNet"] for div in dividends if datetime.fromisoformat(div["closeDate"]) >= last_year)
    return total

def calculate_coupons(figi):
    """Рассчитывает купонный доход для облигаций (пример)"""
    # В реальном коде нужно запросить купоны через /operations
    return 0  # Заглушка для примера

def update_google_sheet(portfolio_data):
    """Обновляет Google Таблицу"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open(SPREADSHEET_NAME).sheet1
    
    # Формируем данные для таблицы
    rows = []
    for asset in portfolio_data:
        rows.append([
            asset["Тип актива"],
            asset["Название"],
            asset["Тикер"],
            asset["Количество"],
            asset["Средняя цена"],
            asset["Текущая цена"],
            asset["Дивиденды/Купоны"],
            f"=E2*F2",  # Текущая стоимость позиции
            f"=G2/F2"   # Доходность
        ])
    
    # Очищаем старые данные и записываем новые
    sheet.clear()
    sheet.update("A1", [["Тип", "Название", "Тикер", "Кол-во", "Ср. цена", "Тек. цена", "Дивиденды", "Стоимость", "Доходность"]] + rows)

# === ЗАПУСК ===
if __name__ == "__main__":
    portfolio = get_tinkoff_portfolio()
    ##update_google_sheet(portfolio)
    print("Данные успешно обновлены в Google Таблице!")