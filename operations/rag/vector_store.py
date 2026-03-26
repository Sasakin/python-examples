"""
Vector Store for document embeddings using FAISS.
Simple implementation based on example.md pattern.
"""

import os
import pickle
import numpy as np
import faiss
from pathlib import Path
from typing import List, Optional, Tuple

# Use truststore for corporate SSL certificates
import truststore
truststore.inject_into_ssl()

from sentence_transformers import SentenceTransformer

from document_loader import ConfluenceDocumentLoader, TextSplitter


class VectorStore:
    """FAISS-based vector store for document chunks."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize vector store with embedding model.
        Uses multilingual model for Russian language support.
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.db: Optional[faiss.IndexFlatL2] = None
        self.embeddings: Optional[np.ndarray] = None
        self.documents: List[str] = []  # Text chunks
        self.documents_meta: List[dict] = []  # Metadata for each chunk
        self.store_path: Optional[Path] = None
        print(f"Model loaded, dimension: {self.dimension}")
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings from array of documents (batch processing)."""
        return self.model.encode(texts, show_progress_bar=True)
    
    def create_database(self, documents: List[str], documents_meta: List[dict] = None) -> None:
        """
        Create FAISS index from documents.
        
        Args:
            documents: List of text chunks to index
            documents_meta: Optional list of metadata dicts for each chunk
        """
        self.documents = documents
        self.documents_meta = documents_meta or [{} for _ in range(len(documents))]
        
        print(f"Creating embeddings for {len(documents)} chunks...")
        # Batch create embeddings (much faster than one by one)
        embeddings = self.create_embeddings(documents)
        
        # Convert to numpy float32 for FAISS
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index with L2 metric
        self.dimension = embeddings.shape[1]
        self.db = faiss.IndexFlatL2(self.dimension)
        
        # Add vectors to index
        self.db.add(embeddings)
        self.embeddings = embeddings
        
        print(f"✅ Created database with {self.db.ntotal} vectors")
    
    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of dicts with content, metadata, and score
        """
        if self.db is None:
            raise RuntimeError("Database not created. Call create_database() first.")
        
        # Create query embedding
        query_embedding = self.create_embeddings([query])
        query_vector = np.array(query_embedding).astype('float32')
        
        # Search in FAISS index
        distances, indices = self.db.search(query_vector, top_k)
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score
                similarity = 1.0 / (1.0 + distance)
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.documents_meta[idx] if idx < len(self.documents_meta) else {},
                    'similarity_score': float(similarity),
                    'chunk_id': int(idx)
                })
        
        return results
    
    def save(self, path: str) -> None:
        """Save vector store to disk."""
        store_path = Path(path)
        store_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.db, str(store_path / "index.faiss"))
        
        # Save embeddings
        np.save(store_path / "embeddings.npy", self.embeddings)
        
        # Save documents
        with open(store_path / "documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
        
        # Save metadata
        with open(store_path / "documents_meta.pkl", 'wb') as f:
            pickle.dump(self.documents_meta, f)
        
        # Save config
        with open(store_path / "config.pkl", 'wb') as f:
            pickle.dump({
                'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
                'dimension': self.dimension
            }, f)
        
        self.store_path = store_path
        print(f"✅ Vector store saved to {store_path}")
    
    def load(self, path: str) -> bool:
        """Load vector store from disk."""
        store_path = Path(path)
        
        if not store_path.exists():
            return False
        
        index_file = store_path / "index.faiss"
        embeddings_file = store_path / "embeddings.npy"
        documents_file = store_path / "documents.pkl"
        documents_meta_file = store_path / "documents_meta.pkl"
        
        if not index_file.exists() or not documents_file.exists():
            return False
        
        # Load FAISS index
        self.db = faiss.read_index(str(index_file))
        
        # Load embeddings
        self.embeddings = np.load(embeddings_file)
        
        # Load documents
        with open(documents_file, 'rb') as f:
            self.documents = pickle.load(f)
        
        # Load metadata
        if documents_meta_file.exists():
            with open(documents_meta_file, 'rb') as f:
                self.documents_meta = pickle.load(f)
        
        # Load config
        config_file = store_path / "config.pkl"
        if config_file.exists():
            with open(config_file, 'rb') as f:
                config = pickle.load(f)
                self.dimension = config.get('dimension', self.embeddings.shape[1])
        
        self.store_path = store_path
        print(f"✅ Loaded vector store with {self.db.ntotal} vectors")
        return True
    
    def get_stats(self) -> dict:
        """Get vector store statistics."""
        if self.db is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "loaded",
            "total_vectors": self.db.ntotal,
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "store_path": str(self.store_path) if self.store_path else None
        }


def create_faiss_db(
    docs_directory: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100
) -> VectorStore:
    """
    Create FAISS database from Confluence markdown documents.
    
    Args:
        docs_directory: Path to directory with markdown files
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        VectorStore instance
    """
    print(f"📚 Loading documents from: {docs_directory}")
    
    # Load all documents and combine into one text
    loader = ConfluenceDocumentLoader(docs_directory)
    combined_text, docs_meta = loader.load_all_texts()
    
    if not combined_text.strip():
        raise ValueError(f"No documents found in {docs_directory}")
    
    print(f"✅ Combined text length: {len(combined_text)} characters")
    
    # Split text into chunks
    print(f"✂️  Splitting into chunks (size={chunk_size}, overlap={chunk_overlap})...")
    splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(combined_text)
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Create vector store and database
    vector_store = VectorStore()
    vector_store.create_database(chunks, docs_meta)
    
    return vector_store
