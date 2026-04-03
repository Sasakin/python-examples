# confluence_export_md.py
import truststore
truststore.inject_into_ssl()

import requests
import os
import json
import re
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, unquote
from datetime import datetime
from pathlib import Path

import argparse
import sys

# ================= CONFIG =================
BASE_URL = os.getenv("CONFLUENCE_URL")
API_TOKEN = os.getenv("CONFLUENCE_TOKEN")
DEFAULT_MAX_DEPTH = 2
DEFAULT_OUTPUT_DIR = "confluence_docs"  # Папка для экспорта
# ==========================================

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json;charset=utf-8",
    "X-ExperimentalApi": "opt-in",
    "Accept": "application/json"
}

def make_request(url, params=None):
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Ошибка: {url} → {e}")
        return None

def slugify(text):
    """Преобразует заголовок в безопасное имя файла"""
    text = unquote(text).strip()
    text = re.sub(r'[^\w\s\u0400-\u04FF\-]', '', text)  # оставляем кириллицу
    text = re.sub(r'\s+', '-', text)
    return text.lower()[:100]

def confluence_to_markdown(html):
    """
    Конвертирует Confluence storage HTML → Markdown
    С защитой от ошибок парсинга
    """
    if not html:
        return ""
    
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"⚠️ Ошибка парсинга HTML: {e}")
        return html  # Возвращаем как есть, если не смогли распарсить
    
    # 1. Обрабатываем макросы с защитой от None
    for macro in soup.find_all("ac:structured-macro"):
        try:
            # Защита: если macro == None или не имеет метода get
            if macro is None or not hasattr(macro, 'get'):
                continue
                
            name = macro.get("ac:name", "")
            
            if name == "code":
                code_body = macro.find("ac:plain-text-body")
                if code_body:
                    lang = macro.find("ac:parameter", {"ac:name": "language"})
                    lang = lang.text if lang and hasattr(lang, 'text') else ""
                    macro.replace_with(f"\n```{lang}\n{code_body.text}\n```\n")
                else:
                    macro.decompose()
                    
            elif name in ("info", "note", "warning", "tip"):
                body = macro.find("ac:rich-text-body") or macro.find("ac:plain-text-body")
                if body:
                    marker = {"info": "ℹ️", "note": "📝", "warning": "⚠️", "tip": "💡"}.get(name, "📌")
                    macro.replace_with(f"\n> {marker} {body.get_text(strip=True)}\n")
                else:
                    macro.decompose()
            elif name == "children":
                macro.replace_with("\n*[Список дочерних страниц]*\n")
            else:
                # Неизвестный макрос — просто удаляем
                macro.decompose()
                
        except Exception as e:
            # Логируем ошибку, но не останавливаем парсинг
            print(f"⚠️ Ошибка обработки макроса: {e}")
            continue
    
    # 2. Ссылки <ac:link>
    for ac_link in soup.find_all("ac:link"):
        try:
            if ac_link is None:
                continue
            ri_page = ac_link.find("ri:page")
            if ri_page and hasattr(ri_page, 'get'):
                title = ri_page.get("ri:content-title", "Ссылка")
                ac_link.replace_with(f"[{title}](#{slugify(title)})")
            else:
                ac_link.replace_with(ac_link.get_text(strip=True) if hasattr(ac_link, 'get_text') else "")
        except Exception as e:
            print(f"⚠️ Ошибка обработки ac:link: {e}")
            continue
    
    # 3. Обычные <a>
    for a in soup.find_all("a", href=True):
        try:
            if a is None:
                continue
            href = a.get("href", "#")
            text = a.get_text(strip=True) or href
            if href.startswith("/"):
                href = urljoin(BASE_URL, href)
            a.replace_with(f"[{text}]({href})")
        except Exception as e:
            print(f"⚠️ Ошибка обработки <a>: {e}")
            continue
    
    # 4. Заголовки
    for i in range(1, 7):
        for tag in soup.find_all(f"h{i}"):
            try:
                if tag is None:
                    continue
                prefix = "#" * i + " "
                tag.replace_with(f"\n{prefix}{tag.get_text(strip=True)}\n")
            except:
                continue
    
    # 5. Код <pre><code>
    for pre in soup.find_all("pre"):
        try:
            if pre is None:
                continue
            code = pre.find("code")
            if code and hasattr(code, 'get_text'):
                lang = ""
                if code.get("class"):
                    classes = code.get("class") if isinstance(code.get("class"), list) else [code.get("class")]
                    lang = next((c.replace("language-", "") for c in classes if c.startswith("language-")), "")
                pre.replace_with(f"\n```{lang}\n{code.get_text()}\n```\n")
        except:
            continue
    
    # 6. Таблицы (базовая конверсия)
    for table in soup.find_all("table"):
        try:
            if table is None:
                continue
            rows = []
            for tr in table.find_all(["tr", "thead", "tbody"]):
                if tr is None:
                    continue
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"]) if hasattr(td, 'get_text')]
                if cells:
                    rows.append("| " + " | ".join(cells) + " |")
                    if len(rows) == 1:
                        rows.append("|" + "---|" * len(cells))
            if rows:
                table.replace_with("\n" + "\n".join(rows) + "\n")
        except:
            continue
    
    # 7. Списки
    for ul in soup.find_all("ul"):
        try:
            if ul is None:
                continue
            items = [f"- {li.get_text(strip=True)}" for li in ul.find_all("li") if hasattr(li, 'get_text')]
            if items:
                ul.replace_with("\n" + "\n".join(items) + "\n")
        except:
            continue
            
    for ol in soup.find_all("ol"):
        try:
            if ol is None:
                continue
            items = [f"{i+1}. {li.get_text(strip=True)}" for i, li in enumerate(ol.find_all("li")) if hasattr(li, 'get_text')]
            if items:
                ol.replace_with("\n" + "\n".join(items) + "\n")
        except:
            continue
    
    # 8. Извлекаем текст
    try:
        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    except Exception as e:
        print(f"⚠️ Ошибка извлечения текста: {e}")
        return ""

def get_full_page_content(page_id):
    """Загружает страницу с полным body.storage"""
    url = f"{BASE_URL}/rest/api/content/{page_id}"
    params = {"expand": "body.storage,space,version,ancestors,_links"}
    return make_request(url, params)

def get_child_pages(page_id, limit=100):
    url = f"{BASE_URL}/rest/api/content/{page_id}/child/page"
    params = {"start": 0, "limit": limit, "expand": "space"}
    data = make_request(url, params)
    return data.get("results", []) if data else []

def export_page_to_markdown(page_data, output_dir, path_prefix=""):
    """Сохраняет страницу как .md файл с обработкой ошибок"""
    try:
        title = page_data["title"]
        file_name = f"{slugify(title)}.md"
        file_path = Path(output_dir) / path_prefix / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Формируем полный URL из _links
        links = page_data.get('_links', {})
        base_url = links.get('base', BASE_URL)
        webui_path = links.get('webui', '')
        full_url = urljoin(base_url, webui_path) if webui_path else ''

        frontmatter = f"""---
title: "{title}"
confluence_id: "{page_data['id']}"
space: "{page_data.get('space', {}).get('key', '')}"
version: {page_data.get('version', {}).get('number', 0)}
url: "{full_url}"
exported: "{datetime.now().isoformat()}"
---

"""
        
        content = page_data.get("body", {}).get("storage", {}).get("value", "")
        markdown = frontmatter + confluence_to_markdown(content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        
        rel_path = file_path.relative_to(output_dir)
        return str(rel_path).replace("\\", "/")
        
    except Exception as e:
        # ⚠️ Логируем ошибку и возвращаем None — страница будет пропущена
        page_id = page_data.get("id", "unknown")
        page_title = page_data.get("title", "unknown")
        print(f"⚠️ WARN: Не удалось экспортировать страницу [{page_id}] '{page_title}': {e}")
        return None

def crawl_and_export(page_id, depth=0, max_depth=1, output_dir="", path_prefix="", visited=None):
    if visited is None:
        visited = set()
    if page_id in visited or depth > max_depth:
        return None
    visited.add(page_id)
    
    print(f"{'  ' * depth}📄 [{depth}] {page_id}")
    
    # Загружаем полную страницу
    data = get_full_page_content(page_id)
    if not data:
        print(f"⚠️ WARN: Не удалось загрузить страницу {page_id}")
        return None
    
    # Экспортируем в Markdown
    rel_path = export_page_to_markdown(data, output_dir, path_prefix)
    
    # Если экспорт не удался — логируем и продолжаем без этой страницы
    if rel_path is None:
        return None
    
    page_node = {
        "id": page_id,
        "title": data["title"],
        "file": rel_path,
        "depth": depth,
        "children": []
    }
    
    # Рекурсия по детям
    if depth < max_depth:
        children = get_child_pages(page_id)
        for child in children:
            try:
                child_node = crawl_and_export(
                    child["id"], 
                    depth + 1, 
                    max_depth, 
                    output_dir,
                    path_prefix,
                    visited
                )
                if child_node:
                    page_node["children"].append(child_node)
            except Exception as e:
                print(f"⚠️ WARN: Ошибка при обработке дочерней страницы {child['id']}: {e}")
                continue  # Пропускаем проблемную ветку
    
    return page_node

def generate_toc(tree, indent=0):
    """Генерирует оглавление в Markdown"""
    lines = []
    prefix = "  " * indent + "- "
    title = tree["title"]
    file = tree.get("file", "")
    lines.append(f"{prefix}[{title}]({file})")
    for child in tree.get("children", []):
        lines.extend(generate_toc(child, indent + 1))
    return lines

def main():
    parser = argparse.ArgumentParser(
        description="Экспорт страниц Confluence в Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python confluence_parser.py -p 12345678              Экспорт с указанной страницы
  python confluence_parser.py -p 12345678 -d 3         Глубина 3 уровня
  python confluence_parser.py -p 12345678 -o my_docs   Сохранить в my_docs/
        """
    )

    parser.add_argument(
        "-p", "--page-id",
        type=str,
        required=True,
        help="ID корневой страницы Confluence (обязательный параметр)"
    )
    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"Глубина обхода дочерних страниц (по умолчанию: {DEFAULT_MAX_DEPTH})"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Папка для сохранения файлов (по умолчанию: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    # Проверяем обязательные переменные окружения
    if not BASE_URL:
        print("❌ Не установлена переменная окружения CONFLUENCE_URL")
        sys.exit(1)
    if not API_TOKEN:
        print("❌ Не установлена переменная окружения CONFLUENCE_TOKEN")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Экспорт документации из {args.page_id}, глубина={args.depth}")
    print(f"📁 Вывод: {output_dir.absolute()}\n")

    # Загружаем корневую страницу для метаданных
    root_data = get_full_page_content(args.page_id)
    if not root_data:
        print("❌ Не удалось загрузить корневую страницу")
        return

    # Запускаем рекурсивный экспорт
    tree = crawl_and_export(
        args.page_id,
        depth=0,
        max_depth=args.depth,
        output_dir=str(output_dir)
    )

    if tree:
        # Генерируем README с оглавлением
        toc_lines = ["# 📚 Документация", "", f"Экспортировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", "## Оглавление", ""]
        toc_lines.extend(generate_toc(tree))

        readme_path = output_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("\n".join(toc_lines))

        print(f"\n✅ Готово!")
        print(f"📄 Файлы: {output_dir}/**/*.md")
        print(f"📑 Оглавление: {readme_path}")
        print(f"\n💡 Откройте в редакторе с поддержкой Markdown (VS Code, Obsidian, Typora)")
    else:
        print("❌ Экспорт не завершён")

if __name__ == "__main__":
    main()