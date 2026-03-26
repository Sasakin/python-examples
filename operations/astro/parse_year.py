import swisseph as swe
import datetime
import json
from dateutil.relativedelta import relativedelta

# Инициализация (автоматически скачает эфемериды при первом запуске)
swe.set_ephe_path('./ephemeris')  # папка для файлов эфемерид

# Константы планет
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO
}

def get_transits_for_date(date: datetime.datetime, latitude: float, longitude: float):
    """Рассчитать транзиты на указанную дату и координаты"""
    jd = swe.utc_to_jd(date.year, date.month, date.day, 
                       date.hour, date.minute, date.second, 
                       swe.GREG_CAL)[1]
    
    transits = {}
    for name, planet_id in PLANETS.items():
        # Положение планеты в эклиптических координатах
        pos = swe.calc_ut(jd, planet_id)[0]
        transits[name] = {
            'longitude': pos[0],  # долгота в градусах
            'latitude': pos[1],   # широта
            'distance': pos[2]    # расстояние от Земли
        }
    
    # Асцендент и МС для указанного места
    houses = swe.houses(jd, latitude, longitude)
    transits['Ascendant'] = houses[0][0]
    transits['MC'] = houses[0][9]
    
    return transits

def generate_yearly_transits(start_date: datetime.datetime, 
                             latitude: float, 
                             longitude: float,
                             output_file: str = 'transits_2026.json'):
    """Сгенерировать транзиты на каждый день года"""
    results = {}
    current = start_date
    end_date = start_date + relativedelta(years=1)
    
    print(f"Расчёт транзитов с {start_date.date()} по {end_date.date()}...")
    
    day_count = 0
    while current < end_date:
        date_str = current.strftime('%Y-%m-%d')
        try:
            transits = get_transits_for_date(current, latitude, longitude)
            results[date_str] = transits
            day_count += 1
            
            if day_count % 30 == 0:
                print(f"  Обработано {day_count} дней...")
                
        except Exception as e:
            print(f"Ошибка для {date_str}: {e}")
            results[date_str] = {'error': str(e)}
        
        current += datetime.timedelta(days=1)
    
    # Сохранение в JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nГотово! Результаты сохранены в {output_file}")
    return results

if __name__ == '__main__':
    # Пример использования для Москвы (ваши координаты из памяти: Одинцово)
    MOSCOW_LAT = 55.6678  # Одинцово
    MOSCOW_LON = 37.2828
    
    start = datetime.datetime(2026, 1, 1, 12, 0, 0)  # полдень по местному времени
    generate_yearly_transits(start, MOSCOW_LAT, MOSCOW_LON)