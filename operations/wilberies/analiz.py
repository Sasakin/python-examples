import pandas as pd

# Загрузка данных из CSV файла
# Предположим, что файл имеет колонки: 'название', 'категория', 'спрос'
data = pd.read_csv('wildberries_data.csv')

# Проверяем, какие данные загружены
print(data.head())

# Суммируем спрос по категориям
category_demand = data.groupby('категория')['спрос'].sum().reset_index()

# Находим категорию с наибольшим спросом
max_demand_category = category_demand.loc[category_demand['спрос'].idxmax()]

# Выводим результат
print(f"Категория с наибольшим спросом: {max_demand_category['категория']} (Спрос: {max_demand_category['спрос']})")