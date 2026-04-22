#!/usr/bin/env python3
"""
Script de diagnóstico para probar la función should_use_web_search
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_langchain_agent():
    """Test LangChain Agent decision logic independently."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.agents import AgentType, initialize_agent
        from langchain.tools import Tool
        
        # Check API key
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return False
        else:
            print(f"✅ GOOGLE_API_KEY found: {google_api_key[:10]}...")
        
        # Initialize the LLM
        print("🔧 Initializing LLM...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=google_api_key,
            temperature=0.0
        )
        print("✅ LLM initialized successfully")
        
        # Define tools
        tools = [
            Tool(
                name="policies_db_search",
                func=lambda x: "This tool searches Queplan Insurance internal policies database",
                description="Use for questions related to Queplan Insurance policies, coverage details, claims, exclusions, terms, conditions, or internal company facts. Examples: policy coverage, medical expenses, deductibles, article clauses, specific policy numbers."
            ),
            Tool(
                name="internet_search",
                func=lambda x: "This tool searches the internet for general information",
                description="Use for general knowledge, external news, market comparisons, industry trends, competitor information, or non-policy related information. Examples: latest insurance regulations, market trends, general health information, competitor pricing."
            )
        ]
        print("✅ Tools defined")
        
        # Test queries
        test_queries = [
            # Queries that should use INTERNAL RAG (False)
            "¿Qué gastos médicos están cubiertos en mi póliza?",
            "¿Cuáles son las exclusiones de la póliza Queplan?",
            "¿Hay cobertura para COVID-19 en las pólizas?",
            "¿Cómo funciona el deducible en mi seguro?",
            
            # Queries that should use WEB SEARCH (True)
            "¿Cuáles son las nuevas regulaciones de seguros en España 2024?",
            "¿Qué seguros médicos son más populares en el mercado actualmente?",
            "¿Cuáles son las tendencias en seguros de salud este año?",
            "¿Cuál es el mejor seguro médico del mercado español?",
            "¿Qué dice la nueva ley de seguros en España?",
        ]
        
        print("\n" + "="*80)
        print("🧪 Testing LangChain Agent Decision Logic")
        print("="*80)
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            try:
                # Create classification prompt
                classification_prompt = f"""You are a query classifier for an insurance chatbot system. 
Analyze this user query and decide which tool to use:

User Query: "{query}"

Instructions:
1. If the query is about Queplan Insurance policies, coverage, claims, or internal company information → use policies_db_search
2. If the query is about general knowledge, external information, market comparisons, or industry news → use internet_search
3. If the query is unanswerable or off-topic (e.g., unrelated to insurance) → use policies_db_search (we'll handle it gracefully)

Respond with ONLY the tool name: either "policies_db_search" or "internet_search"."""

                # Initialize agent
                agent = initialize_agent(
                    tools=tools,
                    llm=llm,
                    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True,  # Enable verbose for debugging
                    max_iterations=1,
                    handle_parsing_errors=True
                )
                
                # Get decision
                response = agent.run(classification_prompt)
                response_lower = response.lower()
                
                # Parse response
                if "internet_search" in response_lower or "web" in response_lower:
                    decision = "WEB SEARCH"
                    should_web_search = True
                else:
                    decision = "INTERNAL RAG"
                    should_web_search = False
                
                print(f"   🤖 Agent response: {response}")
                print(f"   ✅ Decision: {decision} (should_use_web_search = {should_web_search})")
                
            except Exception as e:
                print(f"   ❌ Error processing query: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed: pip install langchain langchain-google-genai")
        return False
    except Exception as e:
        print(f"❌ Error testing LangChain agent: {e}")
        return False

def test_simple_heuristic():
    """Test the simple heuristic fallback method."""
    print("\n" + "="*80)
    print("🧪 Testing Simple Heuristic Fallback")
    print("="*80)
    
    def _simple_heuristic_decision(query: str) -> bool:
        """Heuristic method for when LangChain is unavailable."""
        query_lower = query.lower()
        
        # Keywords suggesting external/web search
        web_keywords = [
            'mercado', 'competencia', 'comparar', 'mejor seguro', 'regulación', 'regulaciones',
            'nueva ley', 'actualidad', 'noticias', 'tendencia', 'precio',
            'market', 'competitor', 'compare', 'best insurance', 'regulation', 'regulations',
            'new law', 'news', 'trend', 'latest', 'current'
        ]
        
        # Check if any web keyword is in the query
        return any(keyword in query_lower for keyword in web_keywords)
    
    test_queries = [
        ("¿Qué gastos médicos están cubiertos?", False),
        ("¿Cuáles son las nuevas regulaciones de seguros?", True),
        ("¿Cuál es el mejor seguro médico del mercado?", True),
        ("¿Hay cobertura para COVID-19?", False),
        ("¿Qué dice la nueva ley de seguros?", True),
        ("¿Cómo funciona el deducible?", False),
    ]
    
    for query, expected in test_queries:
        result = _simple_heuristic_decision(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}' → {result} (expected: {expected})")

def test_hybrid_search_engine():
    """Test the full HybridSearchEngine."""
    print("\n" + "="*80)
    print("🧪 Testing Full HybridSearchEngine")
    print("="*80)
    
    try:
        from hybrid_search_engine import HybridSearchEngine
        
        # Initialize engine
        engine = HybridSearchEngine()
        
        # Test queries
        test_queries = [
            "¿Qué gastos médicos están cubiertos?",
            "¿Cuáles son las nuevas regulaciones de seguros en España?",
            "¿Cuál es el mejor seguro médico del mercado?",
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            decision = engine.should_use_web_search(query)
            print(f"   📊 Decision: {'WEB SEARCH' if decision else 'INTERNAL RAG'}")
            
    except Exception as e:
        print(f"❌ Error testing HybridSearchEngine: {e}")

def main():
    """Main test function."""
    print("🔍 Diagnostic Script for Web Search Decision Logic")
    print("="*60)
    
    # Test environment
    print("🔧 Environment Check:")
    google_key = os.getenv('GOOGLE_API_KEY')
    brave_key = os.getenv('BRAVE_API_KEY')
    print(f"   GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Missing'}")
    print(f"   BRAVE_API_KEY: {'✅ Set' if brave_key else '❌ Missing'}")
    
    # Test simple heuristic first
    test_simple_heuristic()
    
    # Test LangChain agent
    if test_langchain_agent():
        print("\n✅ LangChain Agent test completed")
    else:
        print("\n❌ LangChain Agent test failed")
    
    # Test full engine
    test_hybrid_search_engine()
    
    print("\n" + "="*60)
    print("🏁 Diagnostic completed!")

if __name__ == "__main__":
    main()