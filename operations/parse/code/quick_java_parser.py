# quick_java_parser.py - упрощенная версия

import os
import glob

def parse_java_to_single_file(input_dir, output_file):
    """
    Простой парсер: собирает все Java файлы в один текстовый файл
    """
    # Находим все Java файлы рекурсивно
    java_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    
    if not java_files:
        print(f"Java файлы не найдены в {input_dir}")
        return
    
    print(f"Найдено {len(java_files)} Java файлов")
    
    # Сохраняем в один файл
    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.write(f"// Собрано Java файлов: {len(java_files)}\n")
        out_f.write(f"// Исходная директория: {input_dir}\n")
        out_f.write("//\n\n")
        
        for i, java_file in enumerate(java_files):
            out_f.write(f"\n{'='*80}\n")
            out_f.write(f"ФАЙЛ {i+1}: {java_file}\n")
            out_f.write(f"{'='*80}\n\n")
            
            try:
                with open(java_file, 'r', encoding='utf-8') as in_f:
                    content = in_f.read()
                    out_f.write(content)
                    out_f.write("\n")
            except Exception as e:
                out_f.write(f"// Ошибка при чтении файла: {e}\n")
    
    print(f"Все файлы сохранены в {output_file}")

# Пример использования
if __name__ == "__main__":
    # Укажите вашу директорию с Java файлами
    input_directory = "./src/main/java"  # Измените на вашу директорию
    output_directory = "all_java_code.txt"  # Выходной файл
    
    parse_java_to_single_file(input_directory, output_directory)