#!/usr/bin/env python3
"""
Analyze document distribution per PDF file
"""
import chromadb
import os

def analyze_file_distribution():
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection("insurance_policies")
        
        # Get all documents
        all_docs = collection.get(limit=1000)  # Get all documents
        total_docs = len(all_docs['ids'])
        print(f"Total documents: {total_docs}")
        
        # Analyze distribution by file
        file_counts = {}
        for metadata in all_docs['metadatas']:
            filename = metadata.get('file_name', 'Unknown')
            file_counts[filename] = file_counts.get(filename, 0) + 1
        
        print('\nDocuments per file:')
        for filename, count in sorted(file_counts.items()):
            print(f'  {filename}: {count} documents')
        
        # Calculate statistics
        valid_files = [f for f in file_counts.keys() if f != 'Unknown' and f.endswith('.pdf')]
        if valid_files:
            total_files = len(valid_files)
            avg_docs_per_file = sum(file_counts[f] for f in valid_files) / total_files
            max_docs = max(file_counts[f] for f in valid_files)
            min_docs = min(file_counts[f] for f in valid_files)
            
            print(f'\nStatistics for {total_files} PDF files:')
            print(f'  Average documents per file: {avg_docs_per_file:.1f}')
            print(f'  Maximum documents in one file: {max_docs}')
            print(f'  Minimum documents in one file: {min_docs}')
            
            if avg_docs_per_file > 50:  # If more than 50 docs per file on average
                print(f'\n⚠️  WARNING: {avg_docs_per_file:.1f} docs per file seems high for ~22 pages per PDF')
                print('   This suggests over-chunking might be occurring.')
                
                # Sample one file to see the chunking pattern
                sample_file = valid_files[0]
                sample_docs = collection.get(where={'file_name': sample_file})
                print(f'\nSample from {sample_file} ({len(sample_docs["ids"])} documents):')
                
                for i in range(min(5, len(sample_docs['ids']))):
                    doc_id = sample_docs['ids'][i]
                    content = sample_docs['documents'][i]
                    metadata = sample_docs['metadatas'][i]
                    
                    article_num = metadata.get('article_number', 'N/A')
                    chunk_type = metadata.get('chunk_type', metadata.get('document_type', 'N/A'))
                    
                    print(f'  {i+1}. Article {article_num} ({chunk_type})')
                    print(f'      Length: {len(content)} chars')
                    print(f'      Preview: {content[:80]}...')
                    print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_file_distribution()