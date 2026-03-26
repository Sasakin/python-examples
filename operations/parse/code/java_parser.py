import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional
import json
import argparse

class JavaCodeParser:
    def __init__(self, output_format: str = 'txt'):
        """
        Инициализация парсера Java кода
        
        Args:
            output_format: формат вывода (txt, json, markdown)
        """
        self.output_format = output_format
        self.java_files = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_classes': 0,
            'total_methods': 0,
            'file_details': []
        }
    
    def find_java_files(self, directory: str) -> List[str]:
        """
        Рекурсивный поиск всех Java файлов в директории
        
        Args:
            directory: путь к директории
            
        Returns:
            Список путей к Java файлам
        """
        java_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.java'):
                    full_path = os.path.join(root, file)
                    java_files.append(full_path)
        
        return java_files
    
    def parse_java_file(self, file_path: str) -> Dict:
        """
        Парсинг одного Java файла
        
        Args:
            file_path: путь к Java файлу
            
        Returns:
            Словарь с информацией о файле
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'directory': os.path.dirname(file_path),
                'content': content,
                'lines': content.count('\n') + 1,
                'classes': self.extract_classes(content),
                'methods': self.extract_methods(content),
                'imports': self.extract_imports(content),
                'package': self.extract_package(content)
            }
            
            return file_info
            
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return None
    
    def extract_package(self, content: str) -> Optional[str]:
        """Извлекает package declaration"""
        match = re.search(r'^\s*package\s+([\w.]+)\s*;', content, re.MULTILINE)
        return match.group(1) if match else None
    
    def extract_imports(self, content: str) -> List[str]:
        """Извлекает все импорты"""
        imports = re.findall(r'^\s*import\s+([\w.*]+)\s*;', content, re.MULTILINE)
        return imports
    
    def extract_classes(self, content: str) -> List[Dict]:
        """Извлекает информацию о классах"""
        classes = []
        
        # Регулярное выражение для поиска классов, интерфейсов, enum
        class_pattern = r'(?:public|private|protected|abstract|final|static)?\s*(?:class|interface|enum|@?record)\s+(\w+)'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line.strip())
            if match and not line.strip().startswith('//'):
                class_info = {
                    'name': match.group(1),
                    'line_number': i + 1,
                    'type': 'class' if 'class' in line else 
                           'interface' if 'interface' in line else 
                           'enum' if 'enum' in line else 'record'
                }
                classes.append(class_info)
        
        return classes
    
    def extract_methods(self, content: str) -> List[Dict]:
        """Извлекает информацию о методах"""
        methods = []
        
        # Регулярное выражение для поиска методов
        # Улучшенное регулярное выражение для лучшего распознавания методов
        method_pattern = r'(?:public|private|protected|static|abstract|final|synchronized|native|strictfp)?\s*(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{?'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_trimmed = line.strip()
            
            # Пропускаем комментарии и пустые строки
            if line_trimmed.startswith('//') or line_trimmed.startswith('*') or not line_trimmed:
                continue
            
            # Ищем метод (упрощенная проверка)
            if re.search(r'^\s*(?:public|private|protected|static)\s+', line_trimmed) and '(' in line_trimmed and ')' in line_trimmed:
                # Пытаемся извлечь имя метода
                match = re.search(r'\s+(\w+)\s*\(', line_trimmed)
                if match and match.group(1) not in ['if', 'for', 'while', 'switch', 'catch', 'try']:
                    method_info = {
                        'name': match.group(1),
                        'line_number': i + 1,
                        'signature': line_trimmed
                    }
                    methods.append(method_info)
        
        return methods
    
    def save_as_text(self, files_data: List[Dict], output_file: str):
        """Сохранение в текстовом формате"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ПАРСИНГ JAVA КОДА ИЗ ДИРЕКТОРИИ\n")
            f.write("=" * 80 + "\n\n")
            
            for file_info in files_data:
                f.write(f"ФАЙЛ: {file_info['path']}\n")
                f.write(f"Размер: {file_info['lines']} строк\n")
                
                if file_info['package']:
                    f.write(f"Package: {file_info['package']}\n")
                
                if file_info['imports']:
                    f.write(f"Импорты ({len(file_info['imports'])}):\n")
                    for imp in file_info['imports']:
                        f.write(f"  import {imp};\n")
                
                if file_info['classes']:
                    f.write(f"Классы/Интерфейсы/Enum ({len(file_info['classes'])}):\n")
                    for cls in file_info['classes']:
                        f.write(f"  {cls['type'].upper()}: {cls['name']} (строка {cls['line_number']})\n")
                
                if file_info['methods']:
                    f.write(f"Методы ({len(file_info['methods'])}):\n")
                    for method in file_info['methods']:
                        f.write(f"  {method['name']}() (строка {method['line_number']})\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("СОДЕРЖАНИЕ ФАЙЛА:\n")
                f.write("=" * 60 + "\n\n")
                f.write(file_info['content'])
                f.write("\n" + "=" * 80 + "\n\n")
    
    def save_as_json(self, files_data: List[Dict], output_file: str):
        """Сохранение в JSON формате"""
        output_data = {
            'statistics': self.stats,
            'files': files_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def save_as_markdown(self, files_data: List[Dict], output_file: str):
        """Сохранение в Markdown формате"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Парсинг Java кода\n\n")
            f.write(f"## Статистика\n\n")
            f.write(f"- Всего файлов: {self.stats['total_files']}\n")
            f.write(f"- Всего строк кода: {self.stats['total_lines']}\n")
            f.write(f"- Всего классов: {self.stats['total_classes']}\n")
            f.write(f"- Всего методов: {self.stats['total_methods']}\n\n")
            
            f.write("## Файлы\n\n")
            
            for file_info in files_data:
                f.write(f"### {file_info['filename']}\n\n")
                f.write(f"**Путь:** `{file_info['path']}`\n\n")
                f.write(f"**Размер:** {file_info['lines']} строк\n\n")
                
                if file_info['package']:
                    f.write(f"**Package:** `{file_info['package']}`\n\n")
                
                if file_info['imports']:
                    f.write(f"**Импорты ({len(file_info['imports'])}):**\n\n")
                    for imp in file_info['imports']:
                        f.write(f"- `{imp}`\n")
                    f.write("\n")
                
                if file_info['classes']:
                    f.write(f"**Классы ({len(file_info['classes'])}):**\n\n")
                    for cls in file_info['classes']:
                        f.write(f"- `{cls['name']}` ({cls['type']}, строка {cls['line_number']})\n")
                    f.write("\n")
                
                if file_info['methods']:
                    f.write(f"**Методы ({len(file_info['methods'])}):**\n\n")
                    for method in file_info['methods']:
                        f.write(f"- `{method['name']}()` (строка {method['line_number']})\n")
                    f.write("\n")
                
                f.write("**Исходный код:**\n\n")
                f.write("```java\n")
                f.write(file_info['content'])
                f.write("\n```\n\n")
                f.write("---\n\n")
    
    def save_raw_java_files(self, files_data: List[Dict], output_dir: str):
        """
        Сохраняет все Java файлы в одну директорию (плоская структура)
        
        Args:
            files_data: данные о файлах
            output_dir: выходная директория
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for file_info in files_data:
            # Создаем безопасное имя файла
            safe_name = file_info['filename'].replace('.java', '')
            if file_info['package']:
                safe_name = f"{file_info['package'].replace('.', '_')}_{safe_name}"
            
            output_path = os.path.join(output_dir, f"{safe_name}.java")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"// Source: {file_info['path']}\n")
                f.write(f"// Package: {file_info['package'] or 'N/A'}\n")
                f.write(f"// Lines: {file_info['lines']}\n")
                f.write("//\n")
                f.write(file_info['content'])
    
    def parse_directory(self, directory: str) -> List[Dict]:
        """
        Основной метод парсинга директории
        
        Args:
            directory: путь к директории для парсинга
            
        Returns:
            Список с данными о файлах
        """
        print(f"Поиск Java файлов в директории: {directory}")
        
        # Находим все Java файлы
        self.java_files = self.find_java_files(directory)
        
        if not self.java_files:
            print("Java файлы не найдены!")
            return []
        
        print(f"Найдено Java файлов: {len(self.java_files)}")
        
        # Парсим каждый файл
        files_data = []
        total_classes = 0
        total_methods = 0
        total_lines = 0
        
        for i, file_path in enumerate(self.java_files):
            print(f"Парсинг файла {i+1}/{len(self.java_files)}: {os.path.basename(file_path)}")
            
            file_info = self.parse_java_file(file_path)
            if file_info:
                files_data.append(file_info)
                total_classes += len(file_info['classes'])
                total_methods += len(file_info['methods'])
                total_lines += file_info['lines']
        
        # Обновляем статистику
        self.stats.update({
            'total_files': len(files_data),
            'total_lines': total_lines,
            'total_classes': total_classes,
            'total_methods': total_methods,
            'file_details': [{
                'path': f['path'],
                'lines': f['lines'],
                'classes': len(f['classes']),
                'methods': len(f['methods'])
            } for f in files_data]
        })
        
        return files_data
    
    def run(self, directory: str, output_file: str = None, mode: str = None):
        """
        Запуск парсера
        
        Args:
            directory: входная директория
            output_file: выходной файл (опционально)
            mode: режим сохранения (txt, json, md, raw)
        """
        # Определяем режим сохранения
        save_mode = mode or self.output_format
        
        # Парсим директорию
        files_data = self.parse_directory(directory)
        
        if not files_data:
            print("Нет данных для сохранения")
            return
        
        # Определяем имя выходного файла если не задано
        if not output_file:
            base_name = os.path.basename(os.path.normpath(directory))
            if save_mode == 'json':
                output_file = f"java_parsed_{base_name}.json"
            elif save_mode == 'md' or save_mode == 'markdown':
                output_file = f"java_parsed_{base_name}.md"
            elif save_mode == 'raw':
                output_file = f"java_raw_{base_name}"
            else:
                output_file = f"java_parsed_{base_name}.txt"
        
        # Сохраняем в нужном формате
        if save_mode == 'json':
            self.save_as_json(files_data, output_file)
            print(f"Данные сохранены в JSON файл: {output_file}")
        
        elif save_mode == 'md' or save_mode == 'markdown':
            self.save_as_markdown(files_data, output_file)
            print(f"Данные сохранены в Markdown файл: {output_file}")
        
        elif save_mode == 'raw':
            self.save_raw_java_files(files_data, output_file)
            print(f"Java файлы сохранены в директорию: {output_file}")
        
        else:  # txt по умолчанию
            self.save_as_text(files_data, output_file)
            print(f"Данные сохранены в текстовый файл: {output_file}")
        
        # Выводим статистику
        print("\n" + "=" * 50)
        print("СТАТИСТИКА:")
        print("=" * 50)
        print(f"Всего файлов: {self.stats['total_files']}")
        print(f"Всего строк кода: {self.stats['total_lines']}")
        print(f"Всего классов: {self.stats['total_classes']}")
        print(f"Всего методов: {self.stats['total_methods']}")
        print("=" * 50)

def main():
    """Основная функция для запуска из командной строки"""
    parser = argparse.ArgumentParser(description='Парсинг Java кода из директории')
    parser.add_argument('directory', help='Путь к директории с Java файлами')
    parser.add_argument('-o', '--output', help='Путь к выходному файлу')
    parser.add_argument('-f', '--format', choices=['txt', 'json', 'md', 'markdown', 'raw'],
                       default='txt', help='Формат вывода (по умолчанию: txt)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    # Проверяем существование директории
    if not os.path.isdir(args.directory):
        print(f"Ошибка: Директория '{args.directory}' не существует!")
        sys.exit(1)
    
    # Создаем и запускаем парсер
    parser = JavaCodeParser(output_format=args.format)
    parser.run(args.directory, args.output, args.format)

if __name__ == "__main__":
    # Пример использования без аргументов командной строки
    if len(sys.argv) > 1:
        main()
    else:
        # Пример интерактивного использования
        print("=" * 60)
        print("ПАРСЕР JAVA КОДА")
        print("=" * 60)
        
        directory = input("Введите путь к директории с Java файлами: ").strip()
        
        if not os.path.isdir(directory):
            print("Ошибка: Указанная директория не существует!")
            sys.exit(1)
        
        print("\nДоступные форматы вывода:")
        print("1. txt - Текстовый файл со всей информацией")
        print("2. json - JSON файл со структурированными данными")
        print("3. md/markdown - Markdown файл с форматированием")
        print("4. raw - Сохранить все Java файлы в отдельную директорию")
        
        format_choice = input("\nВыберите формат вывода (1-4 или название): ").strip().lower()
        
        format_map = {
            '1': 'txt',
            '2': 'json', 
            '3': 'md',
            '4': 'raw',
            'txt': 'txt',
            'json': 'json',
            'md': 'md',
            'markdown': 'md',
            'raw': 'raw'
        }
        
        output_format = format_map.get(format_choice, 'txt')
        
        output_file = input("\nВведите путь к выходному файлу (оставьте пустым для автоимени): ").strip()
        if not output_file:
            output_file = None
        
        parser = JavaCodeParser(output_format=output_format)
        parser.run(directory, output_file, output_format)