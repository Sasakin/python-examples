from moexalgo import session, Market, Ticker, CandlePeriod
from datetime import datetime, timedelta  # Добавьте эту строку в начало файла
import pandas as pd

stocks = Market("stocks")
all_stocks = stocks.tickers()  # Вызоваем метод tickers() на экземпляре класса Market
#print(all_stocks)

stocks = Market("stocks")
all_stocks = stocks.tickers()  # Вызоваем метод tickers() на экземпляре класса Market
#print(all_stocks)

sber = Ticker('SBER')

trades = sber.trades()
#print(sber)
#print(trades)

# Пример обработки, если trades - это список строк
#for trade in trades:
    # Предположим, что данные разделены запятыми
   ## parts = trade.split(',')
   ## print(f"Объем сделки: {parts[0]}, Цена: {parts[1]}, Направление: {parts[2]}")

from datetime import datetime, timedelta
import logging
import time
from typing import Optional, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("moex_data_fetcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("moex_data_fetcher")

def get_moex_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    max_retries: int = 1,
    retry_delay: int = 2
) -> Optional[pd.DataFrame]:
    """
    Получает исторические данные с Московской биржи через moexalgo с обработкой ошибок и повторными попытками
    
    Args:
        ticker: Тикер актива (например, 'SBER')
        period: Период данных ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
        interval: Интервал данных ('1d' - дневные, '1w' - недельные, '1m' - месячные)
        max_retries: Максимальное количество попыток при ошибке
        retry_delay: Задержка между попытками в секундах
    
    Returns:
        DataFrame с историческими данными или None при ошибке
    """
    logger.info(f"Запрос данных для {ticker} (период: {period}, интервал: {interval})")
    
    # Определение даты начала в зависимости от периода
    end_date = datetime.now()
    
    period_mapping = {
        "1d": 1,
        "5d": 5,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825
    }
    
    days = period_mapping.get(period, 365)  # По умолчанию 1 год
    start_date = end_date - timedelta(days=days)
    
    # Определение периода свечей для moexalgo
    if interval == "1d":
        candle_period = CandlePeriod.ONE_DAY
    elif interval == "1w":
        candle_period = CandlePeriod.ONE_WEEK
    else:  # По умолчанию дневные данные
        candle_period = CandlePeriod.ONE_MONTH
    
    logger.debug(f"Запрашиваем данные с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')} с периодом {candle_period}")
    
    # Попытки получения данных с повторными запросами при ошибке
    for attempt in range(max_retries):
        try:
            # Получение данных через moexalgo
            ticker_data = Ticker(ticker)
            
            # Используем метод candles как в примере
               # Используем метод candles как в примере
            candles = ticker_data.candles(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                period=candle_period
            )
            
            # Критически важное исправление:
            # Вместо [dict(candle) for candle in candles] используем прямое создание DataFrame
            column_names = ["begin", "end", "open", "high", "low", "close", "value", "volume"]
            df = pd.DataFrame(candles, columns=column_names)
            
            if df.empty:
                logger.warning(f"Для {ticker} не найдено данных за указанный период")
                return None
            
            # Проверяем минимальное количество записей
            if len(df) < 5:
                logger.warning(f"Недостаточно данных для {ticker}: всего {len(df)} записей")
                return None if attempt == max_retries - 1 else None
            
            # Преобразуем даты в правильный формат
            df['begin'] = pd.to_datetime(df['begin'])
            df['end'] = pd.to_datetime(df['end'])
            
            # Устанавливаем индекс
            df = df.set_index('begin')
            
            # Переименовываем колонки для совместимости с общим форматом
            df = df.rename(columns={
                'open': 'Open',
                'close': 'Close',
                'high': 'High',
                'low': 'Low',
                'volume': 'Volume'
            })
            
            # Выбираем только нужные колонки
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Проверка логической целостности данных
            if not validate_ohlc_data(df):
                logger.warning(f"Данные для {ticker} содержат логические ошибки в OHLC")
                return None if attempt == max_retries - 1 else None
            
            logger.info(f"✅ Успешно получены данные для {ticker}: {len(df)} записей")
            return df
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении данных для {ticker} (попытка {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ Не удалось получить данные для {ticker} после {max_retries} попыток")
                return None

def validate_ohlc_data(df: pd.DataFrame) -> bool:
    """
    Проверяет логическую целостность OHLC данных
    
    Args:
        df: DataFrame с OHLC данными
    
    Returns:
        True, если данные логически целостны, иначе False
    """
    # Проверка, что все цены положительные
    if (df['Open'] <= 0).any() or (df['High'] <= 0).any() or \
       (df['Low'] <= 0).any() or (df['Close'] <= 0).any():
        logger.debug("Обнаружены некорректные значения цен (<= 0)")
        return False
    
    # Проверка соотношения OHLC
    if not (df['High'] >= df['Low']).all():
        logger.debug("Нарушено условие: High >= Low")
        return False
    
    if not (df['High'] >= df['Open']).all():
        logger.debug("Нарушено условие: High >= Open")
        return False
    
    if not (df['High'] >= df['Close']).all():
        logger.debug("Нарушено условие: High >= Close")
        return False
    
    if not (df['Low'] <= df['Open']).all():
        logger.debug("Нарушено условие: Low <= Open")
        return False
    
    if not (df['Low'] <= df['Close']).all():
        logger.debug("Нарушено условие: Low <= Close")
        return False
    
    return True

def get_first_available_date(ticker: str) -> Optional[datetime]:
    """
    Получает дату первой доступной свечи для тикера
    
    Args:
        ticker: Тикер актива
    
    Returns:
        Дата первой доступной свечи или None при ошибке
    """
    try:
        # Используем очень раннюю дату для поиска первой свечи
        early_date = datetime(1990, 1, 1)
        ticker_data = Ticker(ticker)
        
        # ПРАВИЛЬНЫЙ ВЫЗОВ: используем start и end вместо date и till_date
        candles = ticker_data.candles(
            start=early_date.strftime("%Y-%m-%d"),
            end=datetime.now().strftime("%Y-%m-%d"),
            period=CandlePeriod.ONE_MONTH,
            use_dataframe=False
        )
        
        column_names = ["begin", "end", "open", "high", "low", "close", "value", "volume"]
        df = pd.DataFrame(candles, columns=column_names)
        
        if not df.empty:
            return pd.to_datetime(df.iloc[0]['begin'])
        
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка при получении первой даты для {ticker}: {str(e)}")
        return None
    
def get_available_tickers() -> pd.DataFrame:
    """
    Получает список всех доступных тикеров с Московской биржи
    
    Returns:
        DataFrame со списком тикеров
    """
    try:
        logger.info("Получение списка всех тикеров с Московской биржи...")
        stocks = Market("stocks")
        tickers = stocks.tickers() 
        
        # Преобразуем в DataFrame
        df = pd.DataFrame(tickers)
        
        # Добавляем информацию о первой доступной дате для каждого тикера
        #df['first_date'] = None
        #for i, ticker in enumerate(df['SECID']):
        #    first_date = get_first_available_date(ticker)
        #    df.at[i, 'first_date'] = first_date
        #    logger.debug(f"Тикер {ticker}: первая доступная дата {first_date}")
        
        logger.info(f"✅ Успешно получено {len(df)} тикеров")
        return tickers
    except Exception as e:
        logger.error(f"❌ Ошибка при получении списка тикеров: {str(e)}")
        return pd.DataFrame()
    
def test_moex_data_fetcher():
    """Тестирование функции получения данных с Московской биржи"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ get_moex_data()")
    print("="*50)
    
    
    # Тест 5: Получение данных с автоматическим определением первой доступной даты
    print("\nТест 5: Получение данных с автоматическим определением периода")
    first_date = get_first_available_date('SBER')
    assert first_date is not None, "Не удалось определить первую доступную дату для SBER"
    print(f"  ✅ Первая доступная дата для SBER: {first_date.date()}")
    
    # Тест 6: Получение списка всех тикеров
    print("\nТест 6: Получение списка всех тикеров")
    tickers = get_available_tickers()
    assert not tickers.empty, "Не удалось получить список тикеров"
    assert 'SECID' in tickers.columns, "Отсутствует колонка SECID в списке тикеров"
    print(f"  ✅ Успешно получено {len(tickers)} тикеров")
    print(f"  Пример тикеров:\n{tickers[['SECID', 'NAME', 'first_date']].head()}")
    
    print("\n" + "="*50)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("="*50)
    return True

# Запуск теста
if __name__ == "__main__":
    try:
        test_moex_data_fetcher()
    except AssertionError as e:
        print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН: {str(e)}")