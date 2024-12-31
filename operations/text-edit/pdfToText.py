import PyPDF2
from docx import Document

def extract_text_from_pdf(pdf_path):
    # Открываем PDF файл
    with open(pdf_path, 'rb') as file:
        # Создаем объект PDF Reader
        pdf_reader = PyPDF2.PdfReader(file)

        # Извлекаем текст из каждой страницы
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"  # Добавляем текст страницы и новую строку

    return text

def save_text_to_word(text, word_path):
    # Создаем новый документ Word
    doc = Document()
    # Добавляем текст в документ
    doc.add_paragraph(text)
    # Сохраняем документ
    doc.save(word_path)

# Укажите путь к вашему PDF файлу
pdf_file_path = 'in/Как_за_пять_лет_стать_чемпионом_мира.pdf'
# Укажите путь для сохранения Word файла
word_file_path = 'out/output.docx'

# Извлекаем текст
extracted_text = extract_text_from_pdf(pdf_file_path)

# Записываем извлеченный текст в Word файл
save_text_to_word(extracted_text, word_file_path)

print(f"Текст успешно извлечен и сохранен в {word_file_path}")