"""Chatbot service for managing chatbot instances and operations."""

import os
from typing import Optional, Dict, Any

from insurance_chatbot import InsuranceChatbot
from hybrid_insurance_chatbot import HybridInsuranceChatbot


class ChatbotService:
    """Service class for managing chatbot instances and operations."""
    
    def __init__(self, chroma_db_path: str):
        """Initialize the chatbot service with ChromaDB path."""
        self.chroma_db_path = chroma_db_path
        self.chatbot: Optional[InsuranceChatbot] = None
        self.hybrid_chatbot: Optional[HybridInsuranceChatbot] = None
        self._initialize_chatbots()
    
    def _initialize_chatbots(self) -> bool:
        """Initialize both standard and hybrid chatbot instances."""
        print(f"🔍 Looking for ChromaDB at: {self.chroma_db_path}")
        
        # Initialize standard chatbot
        try:
            self.chatbot = InsuranceChatbot(chroma_db_path=self.chroma_db_path)
            print("✅ Standard chatbot initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize standard chatbot: {e}")
            self.chatbot = None
        
        # Initialize hybrid chatbot
        try:
            self.hybrid_chatbot = HybridInsuranceChatbot(chroma_db_path=self.chroma_db_path)
            print("✅ Hybrid chatbot initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize hybrid chatbot: {e}")
            print("   Falling back to standard chatbot only")
            self.hybrid_chatbot = None
        
        return self.chatbot is not None or self.hybrid_chatbot is not None
    
    def get_active_chatbot(self):
        """Get the best available chatbot (hybrid preferred, standard as fallback)."""
        return self.hybrid_chatbot if self.hybrid_chatbot is not None else self.chatbot
    
    def is_available(self) -> bool:
        """Check if any chatbot is available."""
        return self.chatbot is not None or self.hybrid_chatbot is not None
    
    def is_hybrid_available(self) -> bool:
        """Check if hybrid chatbot is available."""
        return self.hybrid_chatbot is not None
    
    def chat(self, message: str, verbose: bool = False, force_web_search: bool = False) -> Dict[str, Any]:
        """Process a chat message and return response."""
        active_chatbot = self.get_active_chatbot()
        
        if not active_chatbot:
            raise RuntimeError("No chatbot available")
        
        # Get response from chatbot
        if self.hybrid_chatbot is not None:
            # Use hybrid chatbot with web search capability
            result = self.hybrid_chatbot.chat(
                message, 
                force_web_search=force_web_search,
                verbose=verbose
            )
            
            response = {
                "question": result["question"],
                "answer": result["answer"],
                "sources_used": result["sources_used"],
                "local_sources": result["local_sources"],
                "web_sources": result["web_sources"],
                "search_strategy": result["search_strategy"],
                "used_web_search": result["used_web_search"],
                "chatbot_type": "hybrid",
                "status": "success"
            }
        else:
            # Fall back to standard chatbot
            result = self.chatbot.chat(message, verbose=verbose)
            
            response = {
                "question": result["question"],
                "answer": result["answer"],
                "sources_used": result["sources_used"],
                "local_sources": result["sources_used"],
                "web_sources": 0,
                "search_strategy": "local_only",
                "used_web_search": False,
                "chatbot_type": "standard",
                "status": "success"
            }
        
        if verbose and self.hybrid_chatbot is not None:
            response["search_results"] = result.get("search_results", [])
            response["search_metadata"] = result.get("search_metadata", {})
        elif verbose:
            response["context_docs"] = result.get("context_docs", [])
        
        return response
    
    def search(self, query: str, num_results: int = 10, include_metadata: bool = True) -> Dict[str, Any]:
        """Search documents in the knowledge base."""
        active_chatbot = self.get_active_chatbot()
        
        if not active_chatbot:
            raise RuntimeError("No chatbot available")
        
        # Use the RAG core for searching
        if self.hybrid_chatbot is not None:
            rag_core = self.hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = self.chatbot.rag_core
        
        # Perform search
        results = rag_core.search(query, num_results=num_results)
        
        return {
            "query": query,
            "results": results,
            "num_results": len(results),
            "status": "success"
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the chatbot service."""
        return {
            "status": "healthy" if self.is_available() else "unhealthy",
            "chatbot_ready": self.chatbot is not None,
            "hybrid_chatbot_ready": self.hybrid_chatbot is not None,
            "chatbot_type": (
                "hybrid" if self.hybrid_chatbot is not None 
                else "standard" if self.chatbot is not None 
                else "none"
            )
        }


# Global chatbot service instance
chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """Get the global chatbot service instance."""
    global chatbot_service
    if chatbot_service is None:
        raise RuntimeError("Chatbot service not initialized")
    return chatbot_service


def initialize_chatbot_service(chroma_db_path: str) -> bool:
    """Initialize the global chatbot service."""
    global chatbot_service
    try:
        chatbot_service = ChatbotService(chroma_db_path)
        return chatbot_service.is_available()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot service: {e}")
        return False