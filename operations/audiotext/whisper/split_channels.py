import wave, struct

# файл делится на две дорожки и создается два файла
source_file_name = 'segments/segment_5'

audio_file = wave.open(source_file_name + '.wav')

SAMPLE_WIDTH = audio_file.getsampwidth() # глубина звука
CHANNELS = audio_file.getnchannels() # количество каналов
FRAMERATE = audio_file.getframerate() # частота дискретизации
N_SAMPLES = audio_file.getnframes() # кол-во семплов на каждый канал

N_FRAMES = audio_file.getnframes()

# Определяем параметры аудиофайла

nchannels = CHANNELS
sampwidth = SAMPLE_WIDTH
framerate = FRAMERATE
nframes = N_FRAMES

comptype = "NONE"  # тип компрессии
compname = "not compressed"  # название компрессии

# узнаем кол-во семплов и каналов в источнике
N_SAMPLES = nframes
CHANNELS = nchannels

def create_file_one_channel(name):

    # создаем пустой файл в который мы будем записывать результат обработки в режиме wb (write binary)
    out_file = wave.open(name, "wb")

    # в "настройки" файла с результатом записываем те же параметры, что и у "исходника"
    out_file.setframerate(framerate)
    out_file.setsampwidth(sampwidth)
    out_file.setnchannels(CHANNELS)

    # обратно перегоняем список чисел в байт-строку
    audio_data = struct.pack(f"<{N_SAMPLES * CHANNELS}h", *values_copy)

    # записываем обработанные данные в файл с резхультатом
    out_file.writeframes(audio_data)

##########

print('started')

# читаем из файла все семплы
samples = audio_file.readframes(N_FRAMES)

# просим struct превратить строку из байт в список чисел
# < - обозначение порядка битов в байте (можно пока всегда писать так)
# По середине указывается общее количество чисел, это произведения кол-ва семплов в одном канале на кол-во каналоов
# h - обозначение того, что одно число занимает два байта

values = list(struct.unpack("<" + str(N_FRAMES * CHANNELS) + "h", samples))
print(values[:20])

values_copy = values[:]

# обнулим каждое четное значение
for index, i in enumerate(values_copy):
    if index % 2 == 0:
        values_copy[index] = 0

create_file_one_channel('channels/1_channel.wav')
print(values_copy[:20])

values_copy = values[:]

# обнулим каждое нечетное значение
for index, i in enumerate(values_copy):
    if index % 2 != 0:
        values_copy[index] = 0

create_file_one_channel('channels/2_channel.wav')
print(values_copy[:20])