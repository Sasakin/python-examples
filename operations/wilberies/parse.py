import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL страницы Wildberries (пример)
url = 'https://www.wildberries.ru/catalog/elektronika'  # Замените на нужную категорию

# Заголовки для имитации запроса от браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получаем страницу
response = requests.get(url, headers=headers)

# Проверяем успешность запроса
if response.status_code == 200:
    # Парсим HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем товары на странице
    products = soup.find_all('div', class_='product-card')

    # Список для хранения данных
    data = []

    for product in products:
        title = product.find('span', class_='goods-name').text.strip() if product.find('span', class_='goods-name') else 'Нет названия'
        category = 'Электроника'  # Замените на нужную категорию, если необходимо
        demand = product.find('span', class_='price').text.strip() if product.find('span', class_='price') else 'Нет данных'

        # Добавляем данные в список
        data.append({
            'название': title,
            'категория': category,
            'спрос': demand
        })

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в CSV файл
    df.to_csv('wildberries_data.csv', index=False, encoding='utf-8-sig')
    print("Данные успешно сохранены в wildberries_data.csv")
else:
    print(f"Ошибка при получении страницы: {response.status_code}")