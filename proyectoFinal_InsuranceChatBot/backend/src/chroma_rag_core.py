import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import os

class ChromaRAGCore:
    """
    RAG (Retrieval-Augmented Generation) core using ChromaDB for vector similarity search.
    """
    
    def __init__(self, 
                 db_path: str = "./chroma_db", 
                 collection_name: str = "insurance_policies"):
        """
        Initialize the ChromaRAG core.
        
        Args:
            db_path: Path to the ChromaDB database
            collection_name: Name of the collection to use
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"ChromaDB database not found at {db_path}. Please run chroma_db_builder.py first.")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get the collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Connected to ChromaDB collection '{collection_name}' with {self.collection.count()} documents.")
        except Exception as e:
            raise RuntimeError(f"Failed to load collection '{collection_name}': {e}")
    
    def search(self, 
               query: str, 
               k: int = 3, 
               filter_criteria: Optional[Dict] = None,
               include_metadata: bool = True) -> List[Dict]:
        """
        Search the ChromaDB collection for the most relevant documents.
        
        Args:
            query: The user's query string
            k: The number of relevant documents to retrieve
            filter_criteria: Optional filter criteria for metadata
            include_metadata: Whether to include metadata in results
            
        Returns:
            A list of dictionaries containing document content and metadata
        """
        print(f"Searching for top {k} relevant documents for query: '{query}'")
        
        try:
            # Perform the search
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter_criteria
            )
            
            # Format results
            relevant_docs = []
            for i in range(len(results["documents"][0])):
                doc_info = {
                    "content": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                }
                
                if include_metadata and results["metadatas"][0][i]:
                    doc_info["metadata"] = results["metadatas"][0][i]
                
                relevant_docs.append(doc_info)
            
            print(f"Found {len(relevant_docs)} relevant documents.")
            return relevant_docs
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def search_by_source(self, 
                        query: str, 
                        source_type: str, 
                        k: int = 3) -> List[Dict]:
        """
        Search for documents from a specific source type.
        
        Args:
            query: The user's query string
            source_type: The source type to filter by ("pdf_extraction" or "structured_data")
            k: The number of relevant documents to retrieve
            
        Returns:
            A list of dictionaries containing document content and metadata
        """
        filter_criteria = {"source": source_type}
        return self.search(query, k, filter_criteria)
    
    def search_by_file(self, 
                      query: str, 
                      file_name: str, 
                      k: int = 3) -> List[Dict]:
        """
        Search for documents from a specific file.
        
        Args:
            query: The user's query string
            file_name: The file name to filter by
            k: The number of relevant documents to retrieve
            
        Returns:
            A list of dictionaries containing document content and metadata
        """
        filter_criteria = {"file_name": file_name}
        return self.search(query, k, filter_criteria)
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the ChromaDB collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        total_docs = self.collection.count()
        
        # Get sample of documents to analyze sources
        sample_results = self.collection.get(limit=total_docs)
        
        source_counts = {}
        file_counts = {}
        
        for metadata in sample_results["metadatas"]:
            source = metadata.get("source", "unknown")
            file_name = metadata.get("file_name", "unknown")
            
            source_counts[source] = source_counts.get(source, 0) + 1
            file_counts[file_name] = file_counts.get(file_name, 0) + 1
        
        return {
            "total_documents": total_docs,
            "source_distribution": source_counts,
            "file_distribution": file_counts,
            "collection_name": self.collection_name,
            "database_path": self.db_path
        }
    
    def get_documents_by_article(self, article_number: str, file_name: Optional[str] = None) -> List[Dict]:
        """
        Get documents for a specific article number.
        
        Args:
            article_number: The article number to search for
            file_name: Optional file name to narrow down the search
            
        Returns:
            List of documents matching the article number
        """
        filter_criteria = {"article_number": article_number}
        if file_name:
            filter_criteria["file_name"] = file_name
        
        results = self.collection.get(where=filter_criteria)
        
        documents = []
        for i in range(len(results["documents"])):
            documents.append({
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
                "id": results["ids"][i]
            })
        
        return documents
    
    def semantic_search_with_context(self, 
                                   query: str, 
                                   k: int = 5, 
                                   context_window: int = 2) -> List[str]:
        """
        Perform semantic search and return formatted context for RAG.
        
        Args:
            query: The user's query string
            k: The number of relevant documents to retrieve
            context_window: Number of additional context documents to include
            
        Returns:
            List of formatted context strings ready for RAG
        """
        search_results = self.search(query, k)
        
        formatted_contexts = []
        for i, result in enumerate(search_results):
            metadata = result.get("metadata", {})
            content = result["content"]
            
            # Format context with metadata
            context_header = f"Document {i+1}"
            if metadata.get("file_name"):
                context_header += f" (from {metadata['file_name']}"
                if metadata.get("article_number"):
                    context_header += f", Article {metadata['article_number']}"
                context_header += ")"
            
            formatted_context = f"{context_header}:\n{content}"
            formatted_contexts.append(formatted_context)
        
        return formatted_contexts


def main():
    """Test function for ChromaRAGCore."""
    
    # Initialize the RAG core
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    try:
        rag_core = ChromaRAGCore(db_path=db_path)
        
        # Print collection stats
        stats = rag_core.get_collection_stats()
        print("Collection Statistics:")
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Source Distribution: {stats['source_distribution']}")
        print(f"Top 5 Files: {dict(list(stats['file_distribution'].items())[:5])}")
        
        # Test searches
        test_queries = [
            "cobertura hospitalización gastos médicos",
            "prótesis quirúrgicas",
            "ambulancia servicio emergencia",
            "exclusiones póliza seguro"
        ]
        
        print("\n" + "="*60)
        print("Testing RAG searches:")
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 40)
            
            results = rag_core.search(query, k=3)
            
            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                print(f"Result {i} (distance: {result['distance']:.4f}):")
                print(f"  File: {metadata.get('file_name', 'Unknown')}")
                print(f"  Source: {metadata.get('source', 'Unknown')}")
                if metadata.get("article_number"):
                    print(f"  Article: {metadata['article_number']}")
                print(f"  Content: {result['content'][:150]}...")
                print()
        
        # Test context generation for RAG
        print("\n" + "="*60)
        print("Testing context generation for RAG:")
        
        query = "gastos médicos hospitalización"
        contexts = rag_core.semantic_search_with_context(query, k=3)
        
        print(f"\nFormatted contexts for query: '{query}'")
        for i, context in enumerate(contexts, 1):
            print(f"\nContext {i}:")
            print(context[:300] + "..." if len(context) > 300 else context)
            
    except Exception as e:
        print(f"Error testing ChromaRAGCore: {e}")


if __name__ == "__main__":
    main()