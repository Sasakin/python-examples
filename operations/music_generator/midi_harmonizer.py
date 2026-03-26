import argparse
from music21 import *
import numpy as np
from collections import Counter

def extract_melody(input_path, output_path, min_velocity=25, min_note_duration=0.25):
    """
    Выделяет основную мелодию из MIDI-файла.
    
    Параметры:
    min_velocity - минимальная громкость для учёта ноты (0-127)
    min_note_duration - минимальная длительность ноты в тактах (0.25 = четверть)
    """
    # Загружаем MIDI
    score = converter.parse(input_path)
    print(f"✅ Загружен MIDI: {input_path}")
    print(f"- Мин. громкость: {min_velocity}, Мин. длительность: {min_note_duration} тактов")

    # 1. СОБИРАЕМ ВСЕ КАНДИДАТЫ В МЕЛОДИЮ
    candidates = []
    for part in score.parts:
        for element in part.recurse():
            if isinstance(element, note.Note):
                # Фильтруем по громкости и длительности
                if element.volume.getRealized() >= min_velocity and element.quarterLength >= min_note_duration:
                    candidates.append({
                        'pitch': element.pitch.midi,
                        'velocity': element.volume.getRealized(),
                        'offset': element.offset,
                        'duration': element.quarterLength,
                        'part_id': id(part)
                    })

    if not candidates:
        print("❌ Нет подходящих нот для мелодии. Попробуйте уменьшить min_velocity или min_note_duration.")
        return

    # 2. ОПРЕДЕЛЯЕМ ГЛАВНУЮ ДОРОЖКУ ПО 3 КРИТЕРИЯМ
    # Критерий 1: Самые высокие ноты (но не крайности)
    high_pitch = np.percentile([c['pitch'] for c in candidates], 90)
    filtered_by_pitch = [c for c in candidates if c['pitch'] >= high_pitch - 12]  # Не учитываем ультра-высокие шумы

    # Критерий 2: Наибольшая громкость
    loud_candidates = sorted(filtered_by_pitch, key=lambda x: x['velocity'], reverse=True)[:len(filtered_by_pitch)//2]

    # Критерий 3: Повторяющиеся ритмические паттерны
    rhythm_patterns = Counter([(round(c['offset'] % 4, 2), round(c['duration'], 2)) for c in loud_candidates])
    common_rhythm = [pattern for pattern, count in rhythm_patterns.most_common(3)]
    rhythm_filtered = [c for c in loud_candidates 
                      if (round(c['offset'] % 4, 2), round(c['duration'], 2)) in common_rhythm]

    # 3. ВЫБИРАЕМ ДОРОЖКУ С МАКСИМУМОМ КАНДИДАТОВ
    part_counts = Counter(c['part_id'] for c in rhythm_filtered)
    main_part_id = part_counts.most_common(1)[0][0] if part_counts else None

    # Если не нашли явного лидера — берём самую высокую дорожку
    if not main_part_id:
        highest_part = max(score.parts, key=lambda p: np.mean([n.pitch.midi for n in p.recurse() if isinstance(n, note.Note)] or [0]))
        main_part_id = id(highest_part)

    # 4. ИЗВЛЕКАЕМ МЕЛОДИЮ
    melody = stream.Part()
    notes_added = 0
    for element in score.recurse():
        if isinstance(element, note.Note) and id(element.activeSite) == main_part_id:
            # Удаляем артефакты: очень короткие ноты и повторы на том же смещении
            if element.quarterLength >= min_note_duration and not any(
                n.offset == element.offset and n.pitch == element.pitch for n in melody
            ):
                melody.append(element)
                notes_added += 1

    # 5. ОЧИСТКА ОТ ШУМА (дубликаты, артефакты)
    melody = melody.quantize(4)  # Выравниваем ритм
    melody = stream.Stream([n for n in melody if n.volume.getRealized() >= min_velocity])

    # Сохраняем результат
    melody.write('midi', fp=output_path)
    
    # Выводим пример нот для проверки
    sample_notes = [f"{n.pitch}({n.quarterLength})" for n in melody[:5]]
    print(f"\n✅ Мелодия извлечена! {notes_added} нот сохранено в {output_path}")
    print(f"Первые 5 нот: {', '.join(sample_notes)}")
    print("\nСоветы:")
    print("- Если мелодия прерывистая: уменьшите min_note_duration (например, до 0.125)")
    print("- Если много шума: увеличьте min_velocity (например, до 35)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Извлечение основной мелодии из MIDI')
    parser.add_argument('--input', required=True, help='Путь к входному MIDI-файлу')
    parser.add_argument('--output', required=True, help='Путь к выходному MIDI-файлу')
    parser.add_argument('--min-velocity', type=int, default=25, help='Минимальная громкость (0-127). По умолчанию: 25')
    parser.add_argument('--min-duration', type=float, default=0.25, help='Минимальная длительность ноты в тактах (0.25 = четверть). По умолчанию: 0.25')
    
    args = parser.parse_args()
    extract_melody(args.input, args.output, args.min_velocity, args.min_duration)