import requests

url = input('Введите URL сайта (например, https://.../): ')

# Настройка заголовков для имитации браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

# Получение содержимого страницы
response = requests.get(
        url,
        headers=headers,
        verify=False,
        timeout=10
    )

# Проверка успешности запроса
if response.status_code == 200:
    # Сохранение содержимого в файл
    with open('page.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("HTML-страница успешно скопирована!")
else:
    print(f"Ошибка при получении страницы: {response.status_code}")