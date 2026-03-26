#!/usr/bin/env python3
"""
Main script for Confluence Knowledge Base RAG System.
Builds vector index and provides search functionality.

Usage:
    python main.py build    - Build vector index from documents
    python main.py search   - Search mode (interactive)
    python main.py query "Вопрос" - Single query
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os

from document_loader import ConfluenceDocumentLoader, TextSplitter
from vector_store import VectorStore, create_faiss_db
from rag import RAGSystem, LLMClient


# Load environment variables
load_dotenv()

# Configuration
DEFAULT_DOCS_DIR = Path(__file__).parent.parent.parent / "confluence_docs"
DEFAULT_VECTOR_STORE_DIR = Path(__file__).parent / "vector_store"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 10

# LLM Configuration (MISTRAL)
LLM_URL = os.getenv("MISTRAL_API", "https://api.mistral.ai") + "/v1/chat/completions"
LLM_API_KEY = os.getenv("MISTRAL_API_KEY")
LLM_MODEL = os.getenv("MISTRALE_MODEL", "codestral-latest")


def build_index(
    docs_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> VectorStore:
    """Build vector index from documents."""
    
    docs_path = Path(docs_dir) if docs_dir else DEFAULT_DOCS_DIR
    store_path = Path(output_dir) if output_dir else DEFAULT_VECTOR_STORE_DIR
    
    # Create FAISS database
    vector_store = create_faiss_db(
        str(docs_path),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    print(f"\n💾 Saving vector store to: {store_path}")
    vector_store.save(str(store_path))
    
    stats = vector_store.get_stats()
    print(f"\n📈 Index statistics:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Total chunks: {stats['total_documents']}")
    print(f"   Dimension: {stats['dimension']}")
    
    return vector_store


def load_index(store_dir: Optional[str] = None) -> VectorStore:
    """Load existing vector index."""
    store_path = Path(store_dir) if store_dir else DEFAULT_VECTOR_STORE_DIR
    
    vector_store = VectorStore()
    
    if not vector_store.load(str(store_path)):
        print(f"❌ Vector store not found at {store_path}")
        print("   Run 'python main.py build' first to create the index.")
        sys.exit(1)
    
    return vector_store


def interactive_search(vector_store: VectorStore):
    """Interactive search mode."""
    print("\n🔍 Interactive search mode")
    print("   Type your question and press Enter")
    print("   Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            query = input("❓ Вопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        if query.lower() in ('quit', 'exit', 'q'):
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        print("\n⏳ Searching...\n")
        
        results = vector_store.search(query, top_k=TOP_K)
        
        print(f"📎 Найдено результатов: {len(results)}\n")
        for i, result in enumerate(results, 1):
            title = result['metadata'].get('title', 'Без названия')
            score = result['similarity_score']
            print(f"{i}. {title} (score: {score:.4f})")
            print(f"   {result['content'][:200]}...")
            print()
        
        print("=" * 60)


def single_query_search(vector_store: VectorStore, question: str, top_k: int = TOP_K, output_file: Optional[str] = None):
    """
    Execute single query and print search results.
    If output_file is specified, save results to file (overwrite if exists).
    """
    results = vector_store.search(question, top_k=top_k)
    
    # Format results
    output_lines = []
    output_lines.append(f"Query: {question}")
    output_lines.append(f"Results: {len(results)}")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    for i, result in enumerate(results, 1):
        title = result['metadata'].get('title', 'Без названия')
        score = result['similarity_score']
        source_path = result['metadata'].get('source_path', 'Unknown')
        
        output_lines.append(f"{i}. {title} (score: {score:.4f})")
        output_lines.append(f"   Source: {source_path}")
        output_lines.append(f"   Content:\n{result['content']}")
        output_lines.append("")
        output_lines.append("-" * 60)
        output_lines.append("")
    
    output_text = "\n".join(output_lines)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"✅ Results saved to: {output_file}")
    
    # Print to console
    print(f"\n📎 Найдено результатов: {len(results)}\n")
    for i, result in enumerate(results, 1):
        title = result['metadata'].get('title', 'Без названия')
        score = result['similarity_score']
        print(f"{i}. {title} (score: {score:.4f})")
        print(f"   {result['content'][:300]}...")
        print()


def single_query_rag(rag: RAGSystem, question: str, top_k: int = TOP_K):
    """Execute single query with RAG and LLM."""
    response = rag.query(question)
    
    print(f"\n🤖 Ответ ({response.model_used}):\n")
    print(response.answer)
    
    if response.sources:
        print(f"\n📎 Источники ({len(response.sources)}):")
        for i, src in enumerate(response.sources, 1):
            title = src['metadata'].get('title', 'Без названия')
            score = src['similarity_score']
            print(f"   {i}. {title} (score: {score:.4f})")


def main():
    parser = argparse.ArgumentParser(
        description="Confluence Knowledge Base RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py build                      Build vector index
  python main.py build --chunk-size 500     Build with custom chunk size
  python main.py search                     Interactive search mode
  python main.py query "Что такое cx-flow?" Single query (search only)
  python main.py rag "Что такое cx-flow?"   Single query with LLM answer
  python main.py stats                      Show index statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build vector index")
    build_parser.add_argument("--docs-dir", type=str, help="Documents directory")
    build_parser.add_argument("--output-dir", type=str, help="Output directory for vector store")
    build_parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Chunk size")
    build_parser.add_argument("--chunk-overlap", type=int, default=CHUNK_OVERLAP, help="Chunk overlap")
    
    # Search command
    subparsers.add_parser("search", help="Interactive search mode")
    
    # Query command (search only)
    query_parser = subparsers.add_parser("query", help="Single query (search only)")
    query_parser.add_argument("question", type=str, help="Question to ask")
    query_parser.add_argument("--top-k", type=int, default=TOP_K, help="Number of results")
    query_parser.add_argument("--output", "-o", type=str, help="Output file path (overwrite if exists)")
    
    # RAG command (with LLM)
    rag_parser = subparsers.add_parser("rag", help="Single query with LLM answer")
    rag_parser.add_argument("question", type=str, help="Question to ask")
    rag_parser.add_argument("--top-k", type=int, default=TOP_K, help="Number of results")
    rag_parser.add_argument("--output", "-o", type=str, help="Output file path (overwrite if exists)")
    
    # Stats command
    subparsers.add_parser("stats", help="Show index statistics")
    
    args = parser.parse_args()
    
    if args.command == "build":
        build_index(
            docs_dir=args.docs_dir,
            output_dir=args.output_dir,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
    
    elif args.command == "search":
        vector_store = load_index()
        interactive_search(vector_store)
    
    elif args.command == "query":
        vector_store = load_index()
        single_query_search(vector_store, args.question, args.top_k, args.output)
    
    elif args.command == "rag":
        vector_store = load_index()
        llm_client = LLMClient(base_url=LLM_URL, api_key=LLM_API_KEY, model=LLM_MODEL)
        rag = RAGSystem(vector_store, llm_client, top_k=args.top_k)
        single_query_rag(rag, args.question)
    
    elif args.command == "stats":
        vector_store = load_index()
        stats = vector_store.get_stats()
        print("\n📈 Vector Store Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    else:
        parser.print_help()
        print("\nNo command specified. Use --help for usage information.")


if __name__ == "__main__":
    main()
