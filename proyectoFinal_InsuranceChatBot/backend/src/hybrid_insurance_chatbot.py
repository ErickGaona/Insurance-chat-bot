import os
import google.generativeai as genai
from typing import List, Dict, Optional
from hybrid_search_engine import HybridSearchEngine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class HybridInsuranceChatbot:
    """
    Enhanced insurance policy chatbot using hybrid search (ChromaDB + Brave Search) and Google Gemini.
    """
    
    def __init__(self, 
                 chroma_db_path: str = "../chroma_db",
                 google_api_key: str = None,
                 brave_api_key: str = None,
                 model: str = "gemini-2.0-flash-exp",
                 max_local_docs: int = 10,
                 max_web_docs: int = 3):
        """
        Initialize the hybrid insurance chatbot.
        
        Args:
            chroma_db_path: Path to ChromaDB database
            google_api_key: Google API key for Gemini
            brave_api_key: Brave Search API key
            model: Gemini model to use
            max_local_docs: Maximum number of local documents to retrieve
            max_web_docs: Maximum number of web search results to retrieve
        """
        
        # Initialize Hybrid Search Engine
        try:
            self.search_engine = HybridSearchEngine(
                chroma_db_path=chroma_db_path,
                brave_api_key=brave_api_key,
                default_local_results=max_local_docs,
                default_web_results=max_web_docs
            )
            print(f"✅ Hybrid search engine initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize hybrid search engine: {e}")
        
        # Set up Google Gemini API
        self.api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable or pass google_api_key parameter.")
        self.model = model
        
        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # Enhanced system prompt for hybrid search
        self.system_prompt = """Eres un asistente especializado en pólizas de seguros médicos con acceso tanto a una base de datos interna de pólizas como a información actualizada de internet. Tu trabajo es ayudar a los usuarios a entender las coberturas, exclusiones, y términos de sus pólizas de seguro.

INSTRUCCIONES:
1. Responde basándote en la información proporcionada en el contexto
2. Si tienes información de la base de datos interna (LOCAL), úsala como fuente primaria y más confiable
3. Si tienes información de internet (WEB), úsala para complementar o proporcionar contexto actualizado
4. Indica claramente las fuentes de tu información (base de datos interna vs. información web)
5. Si la información no está disponible en ninguna fuente, di claramente que no tienes esa información específica
6. Sé preciso y cita los artículos específicos cuando sea relevante para información de la base de datos
7. Para información web, menciona que es información complementaria de internet
8. Usa un lenguaje claro y profesional
9. Si hay diferencias entre fuentes, explica las discrepancias

FORMATO DE RESPUESTA:
- Respuesta directa a la pregunta
- Cita las fuentes específicas (artículos de pólizas para info local, URLs para info web)
- Si aplica, menciona limitaciones o condiciones importantes
- Distingue claramente entre información oficial de pólizas e información complementaria de internet"""

    def get_relevant_context(self, query: str, force_web_search: bool = False) -> tuple:
        """
        Retrieve relevant context using hybrid search.
        
        Args:
            query: User's question
            force_web_search: Force web search even if not auto-detected
            
        Returns:
            Tuple of (search_results, search_metadata)
        """
        return self.search_engine.hybrid_search(
            query=query,
            force_web_search=force_web_search
        )
    
    def generate_response(self, user_question: str, context: str, search_metadata: Dict) -> str:
        """
        Generate a response using Gemini with hybrid context.
        
        Args:
            user_question: User's question
            context: Formatted context from hybrid search
            search_metadata: Metadata about the search performed
            
        Returns:
            Generated response
        """
        try:
            # Create enhanced prompt with search context information
            search_info = f"[INFORMACIÓN DE BÚSQUEDA: Se consultó base de datos local: {search_metadata['used_local_search']}, se consultó internet: {search_metadata['used_web_search']}]"
            
            full_prompt = f"{self.system_prompt}\n\n{search_info}\n\nCONTEXTO:\n{context}\n\nPREGUNTA: {user_question}"
            
            # Generate content using Gemini
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for factual responses
                    max_output_tokens=1200,  # Increased for hybrid responses
                    top_p=0.8,
                    top_k=10
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Error generando respuesta: {e}"
    
    def chat(self, user_question: str, force_web_search: bool = False, verbose: bool = False) -> Dict:
        """
        Main chat function that combines hybrid retrieval and generation.
        
        Args:
            user_question: User's question
            force_web_search: Force web search even if not auto-detected
            verbose: Whether to return additional information
            
        Returns:
            Dictionary containing response and metadata
        """
        print(f"🔍 Processing question: {user_question}")
        
        # Retrieve relevant context using hybrid search
        search_results, search_metadata = self.get_relevant_context(
            user_question, 
            force_web_search=force_web_search
        )
        
        if verbose:
            print(f"📊 Search summary: {search_metadata['local_results_count']} local + {search_metadata['web_results_count']} web = {search_metadata['total_results']} total")
        
        # Format context for LLM
        formatted_context = self.search_engine.format_context_for_llm(search_results, search_metadata)
        
        # Generate response
        print("🤖 Generating response...")
        response = self.generate_response(user_question, formatted_context, search_metadata)
        
        result = {
            "question": user_question,
            "answer": response,
            "sources_used": search_metadata['total_results'],
            "local_sources": search_metadata['local_results_count'],
            "web_sources": search_metadata['web_results_count'],
            "used_web_search": search_metadata['used_web_search'],
            "search_strategy": "hybrid" if search_metadata['used_web_search'] else "local_only"
        }
        
        if verbose:
            result["search_results"] = search_results
            result["search_metadata"] = search_metadata
            result["formatted_context"] = formatted_context
        
        return result
    
    def interactive_chat(self):
        """Run an interactive chat session with hybrid search capabilities."""
        
        print("🏥💻 Chatbot Híbrido de Seguros Médicos")
        print("=" * 60)
        print("Pregúntame sobre coberturas, exclusiones, o cualquier aspecto de las pólizas de seguro.")
        print("Tengo acceso a la base de datos de pólizas y a información actualizada de internet.")
        print("Escribe 'salir' para terminar, 'ayuda' para ver ejemplos, 'web' para forzar búsqueda web.")
        print()
        
        while True:
            try:
                user_input = input("👤 Tu pregunta: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if user_input.lower() == 'ayuda':
                    self.show_help_examples()
                    continue
                
                if not user_input:
                    print("Por favor, escribe una pregunta.")
                    continue
                
                # Check if user wants to force web search
                force_web = user_input.lower().startswith('web ')
                if force_web:
                    user_input = user_input[4:].strip()  # Remove 'web ' prefix
                    print("🌐 Forzando búsqueda web...")
                
                # Get chatbot response
                result = self.chat(user_input, force_web_search=force_web, verbose=False)
                
                print(f"\n🤖 Respuesta:")
                print(result["answer"])
                
                # Show source information
                search_strategy = "🏠 Solo base local" if result["search_strategy"] == "local_only" else "🏠💻 Búsqueda híbrida"
                print(f"\n📊 {search_strategy}")
                print(f"   └─ Fuentes locales: {result['local_sources']}, Fuentes web: {result['web_sources']}")
                print("-" * 60)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help_examples(self):
        """Show example questions for hybrid search."""
        print("\n💡 Ejemplos de preguntas:")
        print("\n🏠 Preguntas para base de datos local:")
        print("• ¿Qué gastos médicos están cubiertos en hospitalización?")
        print("• ¿Cuáles son las principales exclusiones de la póliza?")
        print("• ¿Cómo funciona el deducible?")
        print("• ¿Hay cobertura para COVID-19?")
        
        print("\n🌐 Preguntas que pueden usar búsqueda web:")
        print("• ¿Cuáles son las nuevas regulaciones de seguros en España?")
        print("• ¿Qué seguros médicos son más populares actualmente?")
        print("• ¿Cuáles son las tendencias en seguros de salud?")
        print("• ¿Qué opinan los usuarios sobre diferentes aseguradoras?")
        
        print("\n💡 Usa 'web [pregunta]' para forzar búsqueda web en cualquier pregunta")
        print()


def main():
    """Main function to run the hybrid chatbot."""
    
    try:
        # Initialize hybrid chatbot
        chatbot = HybridInsuranceChatbot()
        
        # Test with a few questions first
        print("🧪 Testing hybrid chatbot...")
        
        test_questions = [
            ("¿Hay cobertura para COVID-19?", False),  # Should find in local DB
            ("¿Cuáles son las nuevas regulaciones de seguros en España?", False),  # Should trigger web search
            ("¿Qué gastos médicos están cubiertos?", True),  # Force web search
        ]
        
        for question, force_web in test_questions:
            print(f"\n➡️ Test question: {question}")
            if force_web:
                print("   (Forcing web search)")
            
            result = chatbot.chat(question, force_web_search=force_web)
            print(f"🤖 Strategy: {result['search_strategy']}")
            print(f"📊 Sources: {result['local_sources']} local + {result['web_sources']} web")
            print(f"💬 Response: {result['answer'][:200]}...")
        
        print("\n" + "="*60)
        print("✅ Hybrid chatbot working correctly!")
        print("Starting interactive session...")
        print()
        
        # Start interactive session
        chatbot.interactive_chat()
        
    except Exception as e:
        print(f"❌ Error initializing hybrid chatbot: {e}")


if __name__ == "__main__":
    main()