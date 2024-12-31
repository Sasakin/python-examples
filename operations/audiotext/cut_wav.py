from pydub import AudioSegment
import os

# Функция для нарезки WAV файла
def split_audio(file_path, segment_length_ms):
    # Загружаем аудиофайл
    audio = AudioSegment.from_file(file_path)

    # Длина сегмента в миллисекундах
    segment_length = segment_length_ms * 1000  # переводим в миллисекунды

    # Получаем общее количество сегментов
    num_segments = len(audio) // segment_length + (1 if len(audio) % segment_length > 0 else 0)

    # Создаем папку для сохранения сегментов
    output_dir = "segments"
    os.makedirs(output_dir, exist_ok=True)

    # Нарезаем аудио на сегменты
    for i in range(num_segments):
        start_time = i * segment_length
        end_time = start_time + segment_length
        segment = audio[start_time:end_time]
        segment.export(os.path.join(output_dir, f"segment_{i + 1}.wav"), format="wav")

# Путь к вашему WAV файлу
file_path = "input/video.wav"  # Замените на путь к вашему файлу
segment_length = 500  # Длина сегмента в минутах

# Вызов функции
split_audio(file_path, segment_length)