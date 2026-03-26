# RAG System for Confluence Knowledge Base

Система векторного поиска и RAG (Retrieval-Augmented Generation) для базы знаний Confluence.

## Установка

```bash
pip install -r requirements.txt
```

## Быстрый старт

### 1. Построение векторного индекса

```bash
python main.py build
```

Параметры:
- `--chunk-size 2000` - размер чанка (по умолчанию 2000)
- `--chunk-overlap 200` - перекрытие между чанками (по умолчанию 200)

### 2. Интерактивный поиск

```bash
python main.py search
```

### 3. Единичный запрос (только поиск)

```bash
python main.py query "Что такое cx-flow?"
```

### 4. Запрос с ответом от LLM (RAG)

```bash
python main.py rag "Как использовать автоматический переход?"
python main.py rag "Что такое cx-flow?"
 python main.py rag "Как написать конфигурацию flow используя  cx-flow?" --output response.txt --top-k 20
```

## Команды

| Команда | Описание |
|---------|----------|
| `build` | Построить векторный индекс из документов |
| `search` | Интерактивный режим поиска |
| `query "вопрос"` | Выполнить единичный запрос (поиск) |
| `rag "вопрос"` | Выполнить запрос с ответом от LLM |
| `stats` | Показать статистику индекса |

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    RAG System                            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  Document    │ -> │   Vector     │ -> │    LLM    │ │
│  │   Loader     │    │   Store      │    │  (llama)  │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                   │       │
│         v                   v                   v       │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Markdown   │    │    FAISS     │    │  RAG      │ │
│  │   + YAML     │    │   Index      │    │  Response │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Компоненты

### document_loader.py
- Загрузка Markdown файлов из Confluence
- Парсинг YAML frontmatter
- Объединение всех документов в один текст
- Разбиение на чанки (TextSplitter)

### vector_store.py
- Embedding модель: `paraphrase-multilingual-MiniLM-L12-v2`
- FAISS индекс (IndexFlatL2)
- Пакетное создание эмбеддингов
- Сохранение/загрузка индекса

### rag.py
- LLM клиент для работы с llama3.1:8b
- RAG система для генерации ответов
- Контекстуализация запросов

### main.py
- CLI интерфейс
- Режимы: build, search, query, rag, stats

## API

### LLM Configuration

```python
LLM_URL = "http://10.32.3.8:11435/v1/chat/completions"
LLM_API_KEY = "1coy61eq8u9h42lf"
LLM_MODEL = "llama3.1:8b"
```

### Пример использования в коде

```python
from vector_store import VectorStore, create_faiss_db
from rag import RAGSystem, LLMClient

# Создание векторной базы
vector_store = create_faiss_db(
    "path/to/confluence_docs",
    chunk_size=2000,
    chunk_overlap=200
)
vector_store.save("vector_store")

# Загрузка существующей базы
vector_store = VectorStore()
vector_store.load("vector_store")

# Поиск
results = vector_store.search("Что такое cx-flow?", top_k=5)
for r in results:
    print(f"Title: {r['metadata'].get('title')}")
    print(f"Score: {r['similarity_score']}")
    print(f"Content: {r['content'][:200]}...")

# RAG с LLM
llm_client = LLMClient()
rag = RAGSystem(vector_store, llm_client)
response = rag.query("Как работает cx-flow?")

print(response.answer)
print(response.sources)  # Источники
```

## Примеры запросов

```
Как использовать автоматический переход в следующее состояние?
Что такое cx-flow и как его конфигурировать?
Как работает механизм отката состояний?
Как интегрироваться с cx-messaging?
Что такое FlowInfo и контекст операции?
Как работает механизм таймаут?
```

## Производительность

- 92 документа → 518K символов → 290 чанков
- Время создания эмбеддингов: ~8 секунд (пакетная обработка)
- Размерность эмбеддингов: 384
- Модель: multilingual (поддержка русского языка)
