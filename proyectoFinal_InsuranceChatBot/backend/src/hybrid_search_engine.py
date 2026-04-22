from typing import List, Dict, Optional, Tuple
from chroma_rag_core import ChromaRAGCore
from brave_search_client import BraveSearchClient
import re
import os
from dotenv import load_dotenv

# LangChain imports for tool-based decision logic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool

# Load environment variables
load_dotenv()

class HybridSearchEngine:
    """
    Hybrid search engine that combines ChromaDB vector search with Brave web search.
    """
    
    def __init__(self, 
                 chroma_db_path: str = "../chroma_db",
                 brave_api_key: str = None,
                 default_local_results: int = 3,
                 default_web_results: int = 2):
        """
        Initialize hybrid search engine.
        
        Args:
            chroma_db_path: Path to ChromaDB database
            brave_api_key: Brave Search API key
            default_local_results: Default number of local results to retrieve
            default_web_results: Default number of web results to retrieve
        """
        
        # Initialize ChromaDB RAG core
        try:
            self.rag_core = ChromaRAGCore(db_path=chroma_db_path)
            print(f"✅ Connected to ChromaDB with {self.rag_core.collection.count()} documents")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB: {e}")
        
        # Initialize Brave Search client
        try:
            self.brave_client = BraveSearchClient(api_key=brave_api_key)
            print("✅ Brave Search client initialized")
        except Exception as e:
            print(f"⚠️ Brave Search client not available: {e}")
            self.brave_client = None
        
        self.default_local_results = default_local_results
        self.default_web_results = default_web_results
    
    def should_use_web_search(self, query: str) -> bool:
        """
        Intelligent query classification to determine search strategy.
        Uses enhanced heuristic as primary method with LLM as backup when available.
        
        Args:
            query: User's query
            
        Returns:
            Boolean: True if web search is needed, False for internal RAG
        """
        # First, try enhanced heuristic approach (fast and reliable)
        heuristic_result = self._enhanced_heuristic_decision(query)
        
        # For now, rely primarily on heuristic to avoid API quota issues
        # TODO: Re-enable LLM classification when API quota is sufficient
        print(f"🧠 Enhanced heuristic decision: {'WEB SEARCH' if heuristic_result else 'INTERNAL RAG'} for query: '{query}'")
        return heuristic_result
        
        # LLM classification disabled due to quota limits
        # Uncomment below when API quota is available
        """
        try:
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if not google_api_key:
                print("⚠️ GOOGLE_API_KEY not found, using enhanced heuristic")
                return heuristic_result
            
            # Only use LLM for borderline cases where heuristic is uncertain
            if self._is_borderline_query(query):
                return self._llm_classification(query, google_api_key)
            else:
                return heuristic_result
                
        except Exception as e:
            print(f"⚠️ LLM classification error: {e}, using enhanced heuristic")
            return heuristic_result
        """
    
    def _enhanced_heuristic_decision(self, query: str) -> bool:
        """
        Enhanced heuristic method with better pattern recognition.
        
        Args:
            query: User's query
            
        Returns:
            Boolean: True if web search seems needed, False otherwise
        """
        query_lower = query.lower()
        
        # Strong indicators for INTERNAL search (Queplan policies)
        internal_keywords = [
            # Policy-specific terms
            'póliza', 'poliza', 'queplan', 'cobertura', 'exclusión', 'exclusion',
            'deducible', 'prima', 'artículo', 'articulo', 'cláusula', 'clausula',
            'reclamación', 'reclamacion', 'siniestro', 'beneficiario',
            
            # Medical coverage terms
            'gastos médicos', 'gastos medicos', 'hospitalización', 'hospitalizacion',
            'cirugía', 'cirugia', 'ambulancia', 'urgencias', 'emergencia',
            'covid-19', 'covid', 'coronavirus',
            
            # Policy operations
            'mi seguro', 'mi póliza', 'mi poliza', 'está cubierto', 'esta cubierto',
            'tengo derecho', 'puedo reclamar', 'incluido en'
        ]
        
        # Strong indicators for EXTERNAL search (web/market info)
        external_keywords = [
            # Market and competition
            'mercado', 'competencia', 'competidor', 'comparar', 'comparación', 'comparacion',
            'mejor seguro', 'mejores seguros', 'ranking', 'top', 'más popular', 'mas popular',
            
            # Industry and regulations
            'regulación', 'regulacion', 'regulaciones', 'ley', 'nueva ley', 'normativa',
            'directiva', 'real decreto', 'gobierno', 'ministerio',
            
            # Market trends and news
            'tendencia', 'tendencias', 'actualidad', 'noticias', 'novedades',
            'este año', 'en 2024', 'en 2025', 'últimamente', 'recientemente',
            'actualmente', 'hoy en día', 'en el mercado',
            
            # Price and commercial info
            'precio', 'precios', 'tarifa', 'costo', 'coste', 'cuánto cuesta', 'cuanto cuesta',
            'oferta', 'promoción', 'promocion', 'descuento',
            
            # External entities
            'sanitas', 'adeslas', 'mapfre', 'allianz', 'axa', 'dkv', 'asisa',
            'mutua', 'seg. social', 'seguridad social'
        ]
        
        # Check for internal keywords first (higher priority)
        internal_score = sum(1 for keyword in internal_keywords if keyword in query_lower)
        external_score = sum(1 for keyword in external_keywords if keyword in query_lower)
        
        # Decision logic
        if internal_score > 0 and external_score == 0:
            return False  # Clearly internal
        elif external_score > 0 and internal_score == 0:
            return True   # Clearly external
        elif external_score > internal_score:
            return True   # More external indicators
        elif internal_score > external_score:
            return False  # More internal indicators
        else:
            # Tie or no clear indicators - use additional heuristics
            return self._additional_heuristics(query_lower)
    
    def _additional_heuristics(self, query_lower: str) -> bool:
        """Additional heuristics for unclear cases."""
        
        # Question patterns that suggest external search
        external_patterns = [
            r'cu[aá]l es el mejor',
            r'qu[eé] .* son .* populares',
            r'cu[aá]les son las .* regulacion',
            r'qu[eé] dice la .* ley',
            r'nuevas? .* regulacion',
            r'en el mercado',
            r'comparado con',
        ]
        
        # Question patterns that suggest internal search
        internal_patterns = [
            r'qu[eé] .* cubre',
            r'qu[eé] .* cubierto',
            r'c[oó]mo funciona .* deducible',
            r'tengo .* cobertura',
            r'est[aá] .* incluido',
            r'puedo .* reclamar',
        ]
        
        import re
        
        for pattern in external_patterns:
            if re.search(pattern, query_lower):
                return True
        
        for pattern in internal_patterns:
            if re.search(pattern, query_lower):
                return False
        
        # Default to internal search when uncertain
        return False
    
    def _simple_heuristic_decision(self, query: str) -> bool:
        """
        Legacy simple heuristic method for backward compatibility.
        
        Args:
            query: User's query
            
        Returns:
            Boolean: True if web search seems needed, False otherwise
        """
        # Use the enhanced heuristic instead
        return self._enhanced_heuristic_decision(query)
    
    def search_local(self, query: str, k: int = None) -> List[Dict]:
        """
        Search local ChromaDB for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents from ChromaDB
        """
        if k is None:
            k = self.default_local_results
        
        print(f"🏠 Searching local ChromaDB for: '{query}' (k={k})")
        return self.rag_core.search(query, k=k)
    
    def search_web(self, query: str, count: int = None) -> List[Dict]:
        """
        Search the web using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            List of web search results formatted for RAG
        """
        if not self.brave_client:
            print("⚠️ Web search not available - Brave client not initialized")
            return []
        
        if count is None:
            count = self.default_web_results
        
        print(f"🌐 Searching web for: '{query}' (count={count})")
        return self.brave_client.search_insurance_related(query, count=count)
    
    def hybrid_search(self, 
                     query: str, 
                     force_web_search: bool = False,
                     local_results: int = None,
                     web_results: int = None) -> Tuple[List[Dict], Dict]:
        """
        Perform hybrid search combining local and web results.
        
        Args:
            query: Search query
            force_web_search: Force web search even if not detected as needed
            local_results: Number of local results to retrieve
            web_results: Number of web results to retrieve
            
        Returns:
            Tuple of (combined_results, search_metadata)
        """
        if local_results is None:
            local_results = self.default_local_results
        if web_results is None:
            web_results = self.default_web_results
        
        search_metadata = {
            "query": query,
            "used_local_search": True,
            "used_web_search": False,
            "local_results_count": 0,
            "web_results_count": 0,
            "total_results": 0
        }
        
        # Always search local ChromaDB first
        local_docs = self.search_local(query, k=local_results)
        search_metadata["local_results_count"] = len(local_docs)
        
        combined_results = local_docs.copy()
        
        # Determine if we should use web search
        use_web = force_web_search or self.should_use_web_search(query)
        
        if use_web and self.brave_client:
            search_metadata["used_web_search"] = True
            web_docs = self.search_web(query, count=web_results)
            search_metadata["web_results_count"] = len(web_docs)
            
            # Add web results to combined results
            combined_results.extend(web_docs)
        
        search_metadata["total_results"] = len(combined_results)
        
        # Sort combined results by relevance (distance for local, fixed score for web)
        combined_results.sort(key=lambda x: x.get("distance", 0.5))
        
        print(f"📊 Hybrid search completed: {search_metadata['local_results_count']} local + {search_metadata['web_results_count']} web = {search_metadata['total_results']} total")
        
        return combined_results, search_metadata
    
    def format_context_for_llm(self, search_results: List[Dict], search_metadata: Dict) -> str:
        """
        Format search results for LLM consumption.
        
        Args:
            search_results: Combined search results
            search_metadata: Metadata about the search
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No hay información relevante disponible."
        
        formatted_context = "INFORMACIÓN RELEVANTE:\n\n"
        
        # Add search metadata
        formatted_context += f"Fuentes consultadas: "
        sources = []
        if search_metadata["used_local_search"]:
            sources.append(f"Base de datos local ({search_metadata['local_results_count']} documentos)")
        if search_metadata["used_web_search"]:
            sources.append(f"Búsqueda web ({search_metadata['web_results_count']} resultados)")
        formatted_context += " + ".join(sources) + "\n\n"
        
        # Format each result
        for i, doc in enumerate(search_results, 1):
            metadata = doc.get("metadata", {})
            content = doc["content"]
            source_type = metadata.get("source", "unknown")
            
            formatted_context += f"FUENTE {i} ({'LOCAL' if source_type != 'brave_search' else 'WEB'}):\n"
            
            if source_type == "brave_search":
                # Web search result
                formatted_context += f"Título: {metadata.get('title', 'Sin título')}\n"
                formatted_context += f"URL: {metadata.get('url', '')}\n"
                formatted_context += f"Contenido: {content}\n"
            else:
                # Local database result
                formatted_context += f"Archivo: {metadata.get('file_name', 'Desconocido')}\n"
                if metadata.get("article_number"):
                    formatted_context += f"Artículo: {metadata['article_number']}\n"
                if metadata.get("article_title"):
                    formatted_context += f"Título: {metadata['article_title']}\n"
                formatted_context += f"Contenido: {content}\n"
            
            formatted_context += "-" * 80 + "\n\n"
        
        return formatted_context


def main():
    """Test the hybrid search engine."""
    try:
        # Initialize hybrid search engine
        hybrid_engine = HybridSearchEngine()
        
        # Test queries
        test_queries = [
            "¿Hay cobertura para COVID-19?",  # Should find in local DB
            "¿Cuáles son las nuevas regulaciones de seguros en España?",  # Should trigger web search
            "¿Qué gastos médicos están cubiertos?",  # Local only
            "¿Cuál es el mejor seguro médico del mercado?",  # Should trigger web search
        ]
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Testing hybrid search for: {query}")
            print('='*80)
            
            results, metadata = hybrid_engine.hybrid_search(query)
            
            print(f"\nSearch metadata:")
            print(f"- Local search: {metadata['used_local_search']} ({metadata['local_results_count']} results)")
            print(f"- Web search: {metadata['used_web_search']} ({metadata['web_results_count']} results)")
            print(f"- Total results: {metadata['total_results']}")
            
            print(f"\nFormatted context preview:")
            context = hybrid_engine.format_context_for_llm(results, metadata)
            print(context[:500] + "..." if len(context) > 500 else context)
        
    except Exception as e:
        print(f"❌ Error testing hybrid search: {e}")


if __name__ == "__main__":
    main()