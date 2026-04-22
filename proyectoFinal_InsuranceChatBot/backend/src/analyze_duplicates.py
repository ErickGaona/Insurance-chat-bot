"""
Script to analyze ChromaDB for duplicate content and metadata patterns.
"""

import chromadb
from collections import defaultdict, Counter
import hashlib
import pandas as pd

def analyze_duplicates():
    """Analyze the ChromaDB collection for duplicate content."""
    
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="../chroma_db")
    collection = client.get_collection("insurance_policies")
    
    print("🔍 Analyzing ChromaDB for duplicates...")
    print(f"Total documents in collection: {collection.count()}")
    print("=" * 60)
    
    # Get all documents
    results = collection.get(
        include=['documents', 'metadatas']
    )
    
    documents = results['documents']
    metadatas = results['metadatas']
    ids = results['ids']
    
    print(f"Retrieved {len(documents)} documents for analysis")
    
    # 1. Check for exact content duplicates
    print("\n1. EXACT CONTENT DUPLICATES:")
    content_hashes = defaultdict(list)
    
    for i, doc in enumerate(documents):
        content_hash = hashlib.md5(doc.encode()).hexdigest()
        content_hashes[content_hash].append({
            'id': ids[i],
            'content_preview': doc[:100],
            'metadata': metadatas[i]
        })
    
    exact_duplicates = {k: v for k, v in content_hashes.items() if len(v) > 1}
    
    if exact_duplicates:
        print(f"Found {len(exact_duplicates)} sets of exact duplicates:")
        for i, (hash_val, docs) in enumerate(exact_duplicates.items()):
            print(f"\nDuplicate set {i+1} ({len(docs)} copies):")
            for doc in docs:
                print(f"  ID: {doc['id']}")
                print(f"  File: {doc['metadata'].get('file_name', 'Unknown')}")
                print(f"  Article: {doc['metadata'].get('article_number', 'Unknown')}")
                print(f"  Preview: {doc['content_preview']}...")
                print()
    else:
        print("✅ No exact content duplicates found")
    
    # 2. Check for similar content (first 200 chars)
    print("\n2. SIMILAR CONTENT (first 200 chars):")
    content_prefixes = defaultdict(list)
    
    for i, doc in enumerate(documents):
        prefix = doc[:200].strip()
        content_prefixes[prefix].append({
            'id': ids[i],
            'full_content_length': len(doc),
            'metadata': metadatas[i]
        })
    
    similar_content = {k: v for k, v in content_prefixes.items() if len(v) > 1}
    
    if similar_content:
        print(f"Found {len(similar_content)} sets of similar content:")
        for i, (prefix, docs) in enumerate(list(similar_content.items())[:5]):  # Show first 5
            print(f"\nSimilar set {i+1} ({len(docs)} documents):")
            print(f"Common prefix: {prefix[:100]}...")
            for doc in docs:
                print(f"  ID: {doc['id']} (length: {doc['full_content_length']})")
                print(f"  File: {doc['metadata'].get('file_name', 'Unknown')}")
        if len(similar_content) > 5:
            print(f"... and {len(similar_content) - 5} more similar sets")
    else:
        print("✅ No similar content patterns found")
    
    # 3. Analyze metadata patterns
    print("\n3. METADATA ANALYSIS:")
    
    # Count by file
    file_counts = Counter()
    article_counts = defaultdict(list)
    
    for i, metadata in enumerate(metadatas):
        file_name = metadata.get('file_name', 'Unknown')
        article_num = metadata.get('article_number', 'Unknown')
        
        file_counts[file_name] += 1
        article_counts[file_name].append(article_num)
    
    print("\nDocuments per file:")
    for file_name, count in file_counts.most_common():
        print(f"  {file_name}: {count} documents")
    
    # Check for duplicate article numbers within files
    print("\nPotential duplicate articles within files:")
    for file_name, articles in article_counts.items():
        article_counter = Counter(articles)
        duplicates = {k: v for k, v in article_counter.items() if v > 1}
        if duplicates:
            print(f"  {file_name}:")
            for article, count in duplicates.items():
                print(f"    Article {article}: {count} copies")
    
    # 4. Check ID patterns
    print("\n4. ID PATTERN ANALYSIS:")
    id_prefixes = defaultdict(int)
    
    for doc_id in ids:
        # Extract pattern before the last underscore and number
        if '_' in doc_id:
            prefix = '_'.join(doc_id.split('_')[:-1])
            id_prefixes[prefix] += 1
    
    print("ID prefix patterns (top 10):")
    for prefix, count in Counter(id_prefixes).most_common(10):
        print(f"  {prefix}: {count} documents")
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Total documents: {len(documents)}")
    print(f"Exact duplicates: {sum(len(v) for v in exact_duplicates.values()) if exact_duplicates else 0}")
    print(f"Similar content groups: {len(similar_content)}")
    print(f"Unique files: {len(file_counts)}")
    print(f"Average documents per file: {len(documents) / len(file_counts):.1f}")

if __name__ == "__main__":
    analyze_duplicates()