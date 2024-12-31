from moexalgo import session, Market, Ticker, CandlePeriod

stocks = Market("stocks")
all_stocks = stocks.tickers()  # Вызоваем метод tickers() на экземпляре класса Market
print(all_stocks)

stocks = Market("stocks")
all_stocks = stocks.tickers()  # Вызоваем метод tickers() на экземпляре класса Market
print(all_stocks)

sber = Ticker('SBER')

trades = sber.trades()
print(sber)
print(trades)

# Пример обработки, если trades - это список строк
for trade in trades:
    # Предположим, что данные разделены запятыми
    parts = trade.split(',')
    print(f"Объем сделки: {parts[0]}, Цена: {parts[1]}, Направление: {parts[2]}")

