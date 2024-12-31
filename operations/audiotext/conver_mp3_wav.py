import os
from pydub import AudioSegment

# Функция для преобразования MP3 в WAV
def convert_mp3_to_wav(mp3_file):
    sound = AudioSegment.from_mp3(mp3_file)
    wav_file = mp3_file.replace('.mp3', '.wav')
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    sound.export(wav_file, format='wav')
    return wav_file

def main(mp3_file):
    if not os.path.exists(mp3_file):
       print("Файл не найден!")
       return
    convert_mp3_to_wav(mp3_file)

# Пример использования
if __name__ == "__main__":
    mp3_file_path = "input/video.mp3"  # Укажите путь к вашему MP3 файлу
    main(mp3_file_path)