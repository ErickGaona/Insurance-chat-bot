#!/usr/bin/env python3
"""
Quick script to analyze ChromaDB document distribution
"""
import chromadb
import os

def analyze_documents():
    try:
        # Connect directly to ChromaDB
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection("insurance_policies")
        
        # Get all documents
        total_count = collection.count()
        print(f"Total documents in ChromaDB: {total_count}")
        
        # Sample some documents
        sample_docs = collection.peek(limit=10)
        
        print("\nSample documents analysis:")
        print("="*50)
        
        for i, (doc_id, metadata, document) in enumerate(zip(
            sample_docs['ids'], 
            sample_docs['metadatas'], 
            sample_docs['documents']
        )):
            print(f"{i+1}. ID: {doc_id}")
            print(f"   Source: {metadata.get('source', 'N/A')}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Type: {metadata.get('chunk_type', metadata.get('document_type', 'N/A'))}")
            print(f"   Content length: {len(document)} characters")
            print(f"   Content preview: {document[:100]}...")
            print()
            
        # Analyze by source
        print("\nAnalyzing document sources...")
        source_counts = {}
        chunk_type_counts = {}
        
        # Get a larger sample to analyze patterns
        larger_sample = collection.get(limit=100)
        
        for metadata in larger_sample['metadatas']:
            source = metadata.get('source', 'Unknown')
            chunk_type = metadata.get('chunk_type', metadata.get('document_type', 'Unknown'))
            
            source_counts[source] = source_counts.get(source, 0) + 1
            chunk_type_counts[chunk_type] = chunk_type_counts.get(chunk_type, 0) + 1
            
        print("\nTop sources:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} documents")
            
        print("\nChunk types:")
        for chunk_type, count in sorted(chunk_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {chunk_type}: {count} documents")
            
    except Exception as e:
        print(f"Error analyzing documents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_documents()