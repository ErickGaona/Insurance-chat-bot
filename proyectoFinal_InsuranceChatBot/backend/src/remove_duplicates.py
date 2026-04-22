"""
Script to remove duplicate documents from ChromaDB.
"""

import chromadb
import hashlib
from collections import defaultdict

def remove_duplicates():
    """Remove exact duplicate documents from ChromaDB."""
    
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="../chroma_db")
    collection = client.get_collection("insurance_policies")
    
    print("🔍 Analyzing ChromaDB for exact duplicates to remove...")
    print(f"Total documents before cleanup: {collection.count()}")
    
    # Get all documents
    results = collection.get(include=['documents', 'metadatas'])
    documents = results['documents']
    metadatas = results['metadatas']
    ids = results['ids']
    
    # Find exact duplicates
    content_hashes = defaultdict(list)
    
    for i, doc in enumerate(documents):
        content_hash = hashlib.md5(doc.encode()).hexdigest()
        content_hashes[content_hash].append({
            'index': i,
            'id': ids[i],
            'metadata': metadatas[i]
        })
    
    # Identify duplicates to remove
    exact_duplicates = {k: v for k, v in content_hashes.items() if len(v) > 1}
    ids_to_remove = []
    
    print(f"Found {len(exact_duplicates)} sets of exact duplicates")
    
    for hash_val, docs in exact_duplicates.items():
        # Keep the first document, remove the rest
        docs_to_remove = docs[1:]  # Skip the first one
        
        print(f"Duplicate set ({len(docs)} copies):")
        print(f"  Keeping: {docs[0]['id']} from {docs[0]['metadata'].get('file_name')}")
        
        for doc in docs_to_remove:
            print(f"  Removing: {doc['id']} from {doc['metadata'].get('file_name')}")
            ids_to_remove.append(doc['id'])
    
    # Remove duplicates
    if ids_to_remove:
        print(f"\n🗑️  Removing {len(ids_to_remove)} duplicate documents...")
        collection.delete(ids=ids_to_remove)
        
        print(f"✅ Cleanup complete!")
        print(f"Documents after cleanup: {collection.count()}")
        print(f"Removed: {len(ids_to_remove)} duplicates")
    else:
        print("✅ No duplicates found to remove")

if __name__ == "__main__":
    remove_duplicates()