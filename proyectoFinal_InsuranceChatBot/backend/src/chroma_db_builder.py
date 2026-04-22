import os
import pandas as pd
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from data_ingestion import process_pdfs_from_directory
from sentence_transformers import SentenceTransformer

class ChromaDBBuilder:
    """
    A class to build and manage a ChromaDB vector database for insurance policy documents.
    """
    
    def __init__(self, 
                 db_path: str = "./chroma_db", 
                 collection_name: str = "insurance_policies",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize ChromaDB builder.
        
        Args:
            db_path: Path where ChromaDB will be persisted
            collection_name: Name of the collection to store documents
            embedding_model: Sentence transformer model for embeddings
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Initialize sentence transformer model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Insurance policy documents and articles"}
        )
        
    def process_and_store_pdfs(self, pdf_directory: str) -> None:
        """
        Process PDFs from directory and store them in ChromaDB.
        
        Args:
            pdf_directory: Directory containing PDF files to process
        """
        print(f"Processing PDFs from directory: {pdf_directory}")
        
        # Process PDFs to extract articles
        articles_df = process_pdfs_from_directory(pdf_directory)
        
        if articles_df.empty:
            print("No articles were extracted from PDFs.")
            return
            
        print(f"Extracted {len(articles_df)} articles from PDFs.")
        
        # Store articles in ChromaDB
        self._store_articles_in_chroma(articles_df)
        
    def store_structured_data(self, csv_path: str) -> None:
        """
        Store structured data from CSV file in ChromaDB.
        
        Args:
            csv_path: Path to the structured CSV file
        """
        print(f"Loading structured data from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} records from structured data.")
            
            # Store structured data in ChromaDB
            self._store_structured_data_in_chroma(df)
            
        except Exception as e:
            print(f"Error loading structured data: {e}")
            
    def _store_articles_in_chroma(self, articles_df: pd.DataFrame) -> None:
        """
        Store extracted articles in ChromaDB.
        
        Args:
            articles_df: DataFrame containing article data
        """
        print("Storing articles in ChromaDB...")
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in articles_df.iterrows():
            # Combine title and content for better context
            document_text = f"Article {row['article_number']}: {row['article_title']}\n\n{row['article_content']}"
            
            documents.append(document_text)
            metadatas.append({
                "source": "pdf_extraction",
                "file_name": row['file_name'],
                "article_number": str(row['article_number']),
                "article_title": row['article_title'],
                "document_type": "policy_article"
            })
            # Use index to ensure unique IDs
            ids.append(f"article_{row['file_name']}_{row['article_number']}_{idx}")
            
        # Generate embeddings
        print("Generating embeddings for articles...")
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"Successfully stored {len(documents)} articles in ChromaDB.")
        
    def _store_structured_data_in_chroma(self, df: pd.DataFrame) -> None:
        """
        Store structured data from CSV in ChromaDB.
        
        Args:
            df: DataFrame containing structured policy data
        """
        print("Storing structured data in ChromaDB...")
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df.iterrows():
            # Use the coverage text as the document
            document_text = row['texto_cobertura']
            
            documents.append(document_text)
            metadatas.append({
                "source": "structured_data",
                "file_name": row['nombre_archivo'],
                "policy_number": str(row['numero_poliza']),
                "policy_type": row['tipo_poliza'],
                "text_length": int(row['longitud_texto']),
                "processing_date": row['fecha_procesamiento'],
                "document_type": "policy_coverage"
            })
            ids.append(f"structured_{row['nombre_archivo']}_{idx}")
            
        # Generate embeddings
        print("Generating embeddings for structured data...")
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"Successfully stored {len(documents)} structured records in ChromaDB.")
        
    def build_complete_database(self, data_directory: str) -> None:
        """
        Build complete ChromaDB database from all available data.
        
        Args:
            data_directory: Path to the data directory containing PDFs and structured data
        """
        print("Building complete ChromaDB database...")
        
        # Process PDFs
        pdf_directory = data_directory
        if os.path.exists(pdf_directory):
            self.process_and_store_pdfs(pdf_directory)
        
        # Skip structured data to avoid duplication (commenting out)
        # structured_data_path = os.path.join(data_directory, "structure_data", "polizas_estructuradas.csv")
        # if os.path.exists(structured_data_path):
        #     self.store_structured_data(structured_data_path)
            
        # Print collection stats
        self.print_collection_stats()
        
    def print_collection_stats(self) -> None:
        """Print statistics about the ChromaDB collection."""
        count = self.collection.count()
        print(f"\nChromaDB Collection Stats:")
        print(f"Collection Name: {self.collection_name}")
        print(f"Total Documents: {count}")
        print(f"Database Path: {self.db_path}")
        
    def search(self, query: str, n_results: int = 5, filter_criteria: Optional[Dict] = None) -> Dict:
        """
        Search the ChromaDB collection.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_criteria: Optional filter criteria for metadata
            
        Returns:
            Dictionary containing search results
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_criteria
        )
        
        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0],
            "ids": results["ids"][0]
        }


def main():
    """Main function to build the ChromaDB database."""
    
    # Define paths
    #data_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
    #db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

    data_directory = "data/queplan_insurance"
    db_path = "backend/chroma_db"

    print(f"Data directory: {data_directory}")
    print(f"ChromaDB path: {db_path}")
    
    # Create ChromaDB builder
    builder = ChromaDBBuilder(db_path=db_path)
    
    # Build complete database
    builder.build_complete_database(data_directory)
    
    print("\nChromaDB database creation completed!")
    
    # Test search functionality
    print("\n" + "="*50)
    print("Testing search functionality...")
    
    test_queries = [
        "gastos médicos hospitalización",
        "prótesis quirúrgicas",
        "ambulancia emergencia"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = builder.search(query, n_results=3)
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"], 
            results["metadatas"], 
            results["distances"]
        )):
            print(f"  Result {i+1} (distance: {distance:.4f}):")
            print(f"    Source: {metadata['source']}")
            print(f"    File: {metadata['file_name']}")
            print(f"    Document: {doc[:200]}...")
            print()


if __name__ == "__main__":
    main()