import os
import whisper
import wave

# Функция для распознавания речи из файла WAV
def recognize_speech_from_wav(wav_file):
    # Загрузка модели Whisper
    model = whisper.load_model("medium")  # Вы можете выбрать 'tiny', 'base', 'small', 'medium', 'large'

    # Распознавание речи
    result = model.transcribe(wav_file, language='ru')
    return result['text']

# Основная функция
def main(wav_file):
    if not os.path.exists(wav_file):
        print("Файл не найден!")
        return

    audio_file = wave.open(wav_file)
    CHANNELS = audio_file.getnchannels()
    print("Количество каналов:", CHANNELS)

    text = recognize_speech_from_wav(wav_file)
    print("Распознанный текст:")
    print(text)

    # Сохранение текста в файл
    output_file_path = "../text/recognized_text6.txt"  # Укажите имя файла для сохранения

    # Открываем файл в режиме записи
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)  # Записываем текст в файл

    print(f"Распознанный текст сохранен в файл: {output_file_path}")


if __name__ == "__main__":
    wav_file_path = "../segments/segment_7.wav"  # Укажите путь к вашему MP3 файлу
    main(wav_file_path)