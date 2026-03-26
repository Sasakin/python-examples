"""
RAG (Retrieval-Augmented Generation) implementation.
Combines vector search with LLM for knowledge base Q&A.
"""

import json
from dataclasses import dataclass
from typing import List, Optional
import requests

from vector_store import VectorStore


@dataclass
class RAGResponse:
    """Response from RAG system."""
    answer: str
    sources: List[dict]
    query: str
    model_used: str


class LLMClient:
    """Client for LLM API calls."""
    
    def __init__(
        self,
        base_url,
        api_key,
        model,
        temperature: float = 1
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
    
    def chat(self, messages: List[dict], temperature: Optional[float] = None) -> str:
        """Send chat request to LLM."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=12000
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


class RAGSystem:
    """RAG system for knowledge base Q&A."""
    
    SYSTEM_PROMPT = """Ты - помощник по базе знаний Confluence. Отвечай на вопросы пользователя, используя предоставленный контекст.

Правила:
1. Не добавляй ничего от себя
2. Используй только информацию из предоставленного контекста
3. Если в контексте нет информации для ответа, скажи об этом
4. Цитируй источники, когда это уместно
5. Отвечай подробно и информативно
6. Сохраняй техническую точность
7. Если в ответе требуется код - цитируй код строго из источника.
8. Отвечай на русском языке"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm_client: Optional[LLMClient] = None,
        top_k: int = 5
    ):
        self.vector_store = vector_store
        self.llm_client = llm_client or LLMClient()
        self.top_k = top_k
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[dict]:
        """Search for relevant documents."""
        k = top_k if top_k is not None else self.top_k
        return self.vector_store.search(query, k)
    
    def _build_context(self, results: List[dict]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            title = result.get('metadata', {}).get('title', 'Без названия')
            
            context_parts.append(
                f"[Источник {i}: {title}]\n{result['content']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def query(self, question: str, top_k: Optional[int] = None) -> RAGResponse:
        """
        Query the RAG system.
        Retrieves relevant documents and generates answer using LLM.
        """
        results = self.search(question, top_k)
        
        if not results:
            return RAGResponse(
                answer="Не найдено релевантных документов в базе знаний.",
                sources=[],
                query=question,
                model_used=self.llm_client.model
            )
        
        context = self._build_context(results)
        
        user_prompt = f"""Контекст из базы знаний:
{context}

Вопрос пользователя: {question}

Ответ:"""
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        answer = self.llm_client.chat(messages)
        
        return RAGResponse(
            answer=answer,
            sources=results,
            query=question,
            model_used=self.llm_client.model
        )
    
    def query_without_llm(self, question: str, top_k: Optional[int] = None) -> List[dict]:
        """Search without LLM - just return relevant chunks."""
        return self.search(question, top_k)
