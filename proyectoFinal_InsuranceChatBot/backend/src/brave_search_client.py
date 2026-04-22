import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BraveSearchClient:
    """
    Client for Brave Search API to perform web searches.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Brave Search client.
        
        Args:
            api_key: Brave Search API key
        """
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self.api_key:
            raise ValueError("Brave API key not provided. Set BRAVE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
    
    def search(self, 
               query: str, 
               count: int = 5,
               country: str = "ES",
               lang: str = "es",
               safesearch: str = "moderate",
               freshness: str = None) -> Dict:
        """
        Perform a web search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            country: Country code for localized results
            lang: Language code for results
            safesearch: Safe search setting (strict, moderate, off)
            freshness: Time-based filtering (pd, pw, pm, py for past day/week/month/year)
            
        Returns:
            Dictionary containing search results
        """
        params = {
            "q": query,
            "count": min(count, 20),  # API limit is 20
            "country": country,
            "lang": lang,
            "safesearch": safesearch
        }
        
        if freshness:
            params["freshness"] = freshness
        
        try:
            print(f"🔍 Searching Brave for: '{query}' (count: {count})")
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            results = response.json()
            
            print(f"✅ Found {len(results.get('web', {}).get('results', []))} web results")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Brave Search API error: {e}")
            return {"error": str(e), "web": {"results": []}}
        except Exception as e:
            print(f"❌ Unexpected error during search: {e}")
            return {"error": str(e), "web": {"results": []}}
    
    def format_results_for_rag(self, search_results: Dict, max_results: int = 5) -> List[Dict]:
        """
        Format Brave search results for RAG integration.
        
        Args:
            search_results: Raw results from Brave Search API
            max_results: Maximum number of results to format
            
        Returns:
            List of formatted result dictionaries
        """
        if "error" in search_results:
            return []
        
        web_results = search_results.get("web", {}).get("results", [])
        formatted_results = []
        
        for i, result in enumerate(web_results[:max_results]):
            formatted_result = {
                "content": self._create_content_summary(result),
                "metadata": {
                    "source": "brave_search",
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "published": result.get("age", ""),
                    "rank": i + 1,
                    "document_type": "web_search_result"
                },
                "distance": 0.5,  # Assign moderate relevance score
                "id": f"brave_search_{i}"
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _create_content_summary(self, result: Dict) -> str:
        """
        Create a content summary from a search result.
        
        Args:
            result: Individual search result from Brave API
            
        Returns:
            Formatted content string
        """
        title = result.get("title", "")
        description = result.get("description", "")
        url = result.get("url", "")
        
        content = f"Título: {title}\n"
        if description:
            content += f"Descripción: {description}\n"
        content += f"URL: {url}"
        
        return content
    
    def search_insurance_related(self, query: str, count: int = 3) -> List[Dict]:
        """
        Specialized search for insurance-related queries.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            List of formatted search results
        """
        # Enhance query with insurance-specific terms
        enhanced_query = f"{query} seguro póliza cobertura España"
        
        search_results = self.search(
            query=enhanced_query,
            count=count,
            country="ES",
            lang="es"
        )
        
        return self.format_results_for_rag(search_results, count)


def main():
    """Test the Brave Search client."""
    try:
        client = BraveSearchClient()
        
        # Test search
        test_queries = [
            "cobertura COVID-19 seguros médicos España",
            "póliza seguro médico exclusiones",
            "seguro dental cobertura"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Testing query: {query}")
            print('='*60)
            
            results = client.search_insurance_related(query, count=3)
            
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Title: {result['metadata']['title']}")
                print(f"URL: {result['metadata']['url']}")
                print(f"Description: {result['metadata']['description'][:100]}...")
                print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error testing Brave Search: {e}")


if __name__ == "__main__":
    main()