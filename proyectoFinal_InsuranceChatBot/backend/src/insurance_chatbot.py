import os
import google.generativeai as genai
from typing import List, Dict, Optional
from chroma_rag_core import ChromaRAGCore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class InsuranceChatbot:
    """
    Insurance policy chatbot using ChromaDB for retrieval and DeepSeek for generation.
    """
    
    def __init__(self, 
                 chroma_db_path: str = "../chroma_db",
                 google_api_key: str = None,
                 model: str = "gemini-2.5-flash",
                 max_context_docs: int = 15):
        """
        Initialize the insurance chatbot.
        
        Args:
            chroma_db_path: Path to ChromaDB database
            google_api_key: Google API key for Gemini
            model: Gemini model to use
            max_context_docs: Maximum number of context documents to retrieve
        """
        
        # Initialize ChromaDB RAG core
        try:
            self.rag_core = ChromaRAGCore(db_path=chroma_db_path)
            print(f"✅ Connected to ChromaDB with {self.rag_core.collection.count()} documents")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB: {e}")
        
        # Set up Google Gemini API - NEVER hardcode API keys!
        self.api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable or pass google_api_key parameter.")
        self.model = model
        self.max_context_docs = max_context_docs
        
        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
        
        # System prompt for the insurance chatbot
        self.system_prompt = """Eres un asistente especializado en pólizas de seguros médicos. Tu trabajo es ayudar a los usuarios a entender las coberturas, exclusiones, y términos de sus pólizas de seguro.

INSTRUCCIONES:
1. Responde SOLO basándote en la información proporcionada en el contexto de las pólizas
2. Si la información no está disponible en el contexto, di claramente que no tienes esa información específica
3. Sé preciso y cita los artículos específicos cuando sea relevante
4. Usa un lenguaje claro y profesional
5. Si hay múltiples pólizas con información diferente, menciona las diferencias

FORMATO DE RESPUESTA:
- Respuesta directa a la pregunta
- Cita los artículos y pólizas relevantes
- Si aplica, menciona limitaciones o condiciones importantes"""

    def get_relevant_context(self, query: str, num_docs: int = None) -> List[Dict]:
        """
        Retrieve relevant context documents for a query.
        
        Args:
            query: User's question
            num_docs: Number of documents to retrieve (defaults to max_context_docs)
            
        Returns:
            List of relevant documents with metadata
        """
        if num_docs is None:
            num_docs = self.max_context_docs
            
        return self.rag_core.search(query, k=num_docs)
    
    def format_context_for_llm(self, context_docs: List[Dict]) -> str:
        """
        Format context documents for the LLM prompt.
        
        Args:
            context_docs: List of context documents
            
        Returns:
            Formatted context string
        """
        if not context_docs:
            return "No hay información relevante disponible en las pólizas."
        
        formatted_context = "INFORMACIÓN DE PÓLIZAS DE SEGURO:\n\n"
        
        for i, doc in enumerate(context_docs, 1):
            metadata = doc.get("metadata", {})
            content = doc["content"]
            
            formatted_context += f"DOCUMENTO {i}:\n"
            formatted_context += f"Archivo: {metadata.get('file_name', 'Desconocido')}\n"
            
            if metadata.get("article_number"):
                formatted_context += f"Artículo: {metadata['article_number']}\n"
            
            if metadata.get("article_title"):
                formatted_context += f"Título: {metadata['article_title']}\n"
                
            formatted_context += f"Contenido: {content}\n"
            formatted_context += "-" * 80 + "\n\n"
        
        return formatted_context
    
    def generate_response(self, user_question: str, context: str) -> str:
        """
        Generate a response using Gemini.
        
        Args:
            user_question: User's question
            context: Formatted context from ChromaDB
            
        Returns:
            Generated response
        """
        try:
            # Combine system prompt, context, and user question
            full_prompt = f"{self.system_prompt}\n\nCONTEXTO:\n{context}\n\nPREGUNTA: {user_question}"
            
            # Generate content using Gemini
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for more consistent, factual responses
                    max_output_tokens=2500,
                    top_p=0.8,
                    top_k=10
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Error generando respuesta: {e}"
    
    def chat(self, user_question: str, verbose: bool = False) -> Dict:
        """
        Main chat function that combines retrieval and generation.
        
        Args:
            user_question: User's question
            verbose: Whether to return additional information
            
        Returns:
            Dictionary containing response and metadata
        """
        print(f"🔍 Procesando pregunta: {user_question}")
        
        # Retrieve relevant context
        context_docs = self.get_relevant_context(user_question)
        
        if verbose:
            print(f"📚 Encontrados {len(context_docs)} documentos relevantes")
        
        # Format context for LLM
        formatted_context = self.format_context_for_llm(context_docs)
        
        # Generate response
        print("🤖 Generando respuesta...")
        response = self.generate_response(user_question, formatted_context)
        
        result = {
            "question": user_question,
            "answer": response,
            "sources_used": len(context_docs)
        }
        
        if verbose:
            result["context_docs"] = context_docs
            result["formatted_context"] = formatted_context
        
        return result
    
    def interactive_chat(self):
        """Run an interactive chat session."""
        
        print("🏥 Chatbot de Seguros Médicos")
        print("=" * 50)
        print("Pregúntame sobre coberturas, exclusiones, o cualquier aspecto de las pólizas de seguro.")
        print("Escribe 'salir' para terminar, 'ayuda' para ver ejemplos.")
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
                
                # Get chatbot response
                result = self.chat(user_input, verbose=False)
                
                print(f"\n🤖 Respuesta:")
                print(result["answer"])
                print(f"\n📊 Información basada en {result['sources_used']} documentos de pólizas")
                print("-" * 60)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help_examples(self):
        """Show example questions."""
        print("\n💡 Ejemplos de preguntas:")
        print("• ¿Qué gastos médicos están cubiertos en hospitalización?")
        print("• ¿Cuáles son las principales exclusiones de la póliza?")
        print("• ¿Cómo funciona el deducible?")
        print("• ¿Qué cobertura tiene el servicio de ambulancia?")
        print("• ¿Cuánto tiempo dura el período de carencia?")
        print("• ¿Qué documentos necesito para hacer un reclamo?")
        print("• ¿Está cubierta la cirugía ambulatoria?")
        print()


def main():
    """Main function to run the chatbot."""
    
    try:
        # Initialize chatbot
        chatbot = InsuranceChatbot()
        
        # Test with a few questions first
        print("🧪 Probando el chatbot con algunas preguntas...")
        
        test_questions = [
            "¿Qué gastos médicos están cubiertos?",
            "¿Cuáles son las exclusiones principales?"
        ]
        
        for question in test_questions:
            print(f"\n➡️ Pregunta de prueba: {question}")
            result = chatbot.chat(question)
            print(f"🤖 Respuesta: {result['answer'][:200]}...")
            print(f"📊 Fuentes: {result['sources_used']} documentos")
        
        print("\n" + "="*60)
        print("✅ Chatbot funcionando correctamente!")
        print("Iniciando sesión interactiva...")
        print()
        
        # Start interactive session
        chatbot.interactive_chat()
        
    except Exception as e:
        print(f"❌ Error inicializando chatbot: {e}")


if __name__ == "__main__":
    main()