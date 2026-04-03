# Confluence Parser

Парсер для экспорта страниц Confluence в Markdown файлы.

## Установка

```bash
pip install requests beautifulsoup4 pyyaml truststore
```

## Настройка

Установите переменные окружения:

### Windows (CMD)
```cmd
set CONFLUENCE_URL=https://your-confluence.atlassian.net
set CONFLUENCE_TOKEN=your_api_token
```

### Windows (PowerShell)
```powershell
$env:CONFLUENCE_URL="https://your-confluence.atlassian.net"
$env:CONFLUENCE_TOKEN="your_api_token"
```

### Linux / macOS
```bash
export CONFLUENCE_URL="https://your-confluence.atlassian.net"
export CONFLUENCE_TOKEN="your_api_token"
```

## Запуск

```bash
# Обязательный параметр: -p (ID страницы)
python confluence_parser.py -p 89021667

# С указанием глубины обхода
python confluence_parser.py -p 89021667 -d 3

# С указанием папки вывода
python confluence_parser.py -p 89021667 -o my_docs

# Все параметры
python confluence_parser.py -p 89021667 -d 3 -o my_docs

# Справка
python confluence_parser.py --help
```

## Параметры командной строки

| Параметр | Описание | Обязательный | По умолчанию |
|----------|----------|:------------:|:------------:|
| `-p`, `--page-id` | ID корневой страницы для экспорта | ✅ | — |
| `-d`, `--depth` | Глубина обхода дочерних страниц | ❌ | `2` |
| `-o`, `--output` | Папка для сохранения файлов | ❌ | `confluence_docs` |

## Результат

После запуска в папке `confluence_docs/` появятся:
- `.md` файлы — экспортированные страницы Confluence
- `README.md` — оглавление с ссылками на все страницы

Каждый `.md` файл содержит frontmatter с метаданными:
```yaml
---
title: "Название страницы"
confluence_id: "89021667"
space: "SDK"
version: 3
url: "https://your-confluence.atlassian.net/display/SDK/Page+Name"
exported: "2026-04-03T12:00:00"
---
```
