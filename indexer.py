import os
import chromadb
from pypdf import PdfReader

def index_ndt_documents():
    pdf_folder = "my_pdfs"
    db_folder = "chroma_db"
    
    # 1. Initialize the local ChromaDB database on your drive
    print("🔄 Connecting to local database storage...")
    chroma_client = chromadb.PersistentClient(path=db_folder)
    
    # Create or fetch a collection to store your NDT knowledge base
    collection = chroma_client.get_or_create_collection(name="ndt_level3_knowledge")
    
    # 2. Check for PDF files
    if not os.path.exists(pdf_folder):
        print(f"❌ Error: The folder '{pdf_folder}' does not exist. Please create it.")
        return
        
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"⚠️ No PDF files found in '{pdf_folder}'. Add your NDT PDFs and try again.")
        return

    print(f"📚 Found {len(pdf_files)} PDF(s) to process. Starting extraction...")
    
    doc_id_counter = 0
    
    # 3. Read and process each PDF
    for file_name in pdf_files:
        file_path = os.path.join(pdf_folder, file_name)
        print(f"📄 Processing: {file_name}...")
        
        try:
            reader = PdfReader(file_path)
            
            # Extract text page by page
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if not page_text or len(page_text.strip()) < 50:
                    continue  # Skip blank pages or pages with mostly images
                
                # Split page text into smaller paragraphs/chunks (approx 500 characters)
                # This ensures the AI gets highly specific context blocks
                chunks = [page_text[i:i+500] for i in range(0, len(page_text), 400)]
                
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id_counter += 1
                    
                    # Save the text slice into the local database
                    collection.add(
                        documents=[chunk],
                        metadatas=[{"source": file_name, "page": page_num + 1}],
                        ids=[f"doc_{doc_id_counter}"]
                    )
                    
        except Exception as e:
            print(f"❌ Failed to read {file_name}: {str(e)}")
            
    print(f"🏁 Success! Sliced and stored {doc_id_counter} NDT knowledge blocks in your local database.")

if __name__ == "__main__":
    index_ndt_documents()
