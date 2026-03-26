"""
Document loader for Confluence Markdown files.
Simplified version - combines all documents into one text.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
import yaml


class ConfluenceDocumentLoader:
    """Loader for Confluence markdown documents."""
    
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    def __init__(self, docs_directory: str):
        self.docs_directory = Path(docs_directory)
        if not self.docs_directory.exists():
            raise FileNotFoundError(f"Directory not found: {docs_directory}")
    
    def load_all_texts(self) -> Tuple[str, List[dict]]:
        """
        Load all markdown files and combine into one text.
        Returns combined text and list of document metadata.
        """
        all_texts = []
        documents_meta = []
        
        for md_file in sorted(self.docs_directory.glob("*.md")):
            text, meta = self._load_file(md_file)
            if text:
                all_texts.append(f"\n\n=== {meta.get('title', md_file.stem)} ===\n\n{text}")
                documents_meta.append(meta)
        
        combined_text = "\n".join(all_texts)
        return combined_text, documents_meta
    
    def _load_file(self, file_path: Path) -> Tuple[Optional[str], dict]:
        """Load a single file and return text with metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter = {}
            body = content
            
            match = self.FRONTMATTER_PATTERN.match(content)
            if match:
                frontmatter_text = match.group(1)
                frontmatter = yaml.safe_load(frontmatter_text) or {}
                body = content[match.end():]
            
            frontmatter['source_path'] = str(file_path)
            return body.strip(), frontmatter
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None, {}


class TextSplitter:
    """Splits text into chunks for embedding."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
            
            # Try to break at sentence boundary
            while end > start and text[end] not in ['\n', '.', ' ', '\t']:
                end -= 1
            
            if end <= start:
                end = start + self.chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
