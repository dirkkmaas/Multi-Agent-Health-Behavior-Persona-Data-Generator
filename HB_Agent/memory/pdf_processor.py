import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from .chroma_memory import ChromaMemory

class PDFProcessor:    
    def __init__(self, pdf_dir: str, collection_name: str):
        """
        Initialize the PDF processor.
        
        """
        self.pdf_dir = pdf_dir
        self.collection_name = collection_name
        self.memory = ChromaMemory()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_pdf_to_chunks(self):
        """Process all PDFs in the directory and store chunks in semantic memory."""
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_dir}")
            return
        
        for pdf_file in pdf_files:
            try:
                pdf_path = os.path.join(self.pdf_dir, pdf_file)
                print(f"Processing {pdf_file}...")
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                chunks = self.text_splitter.split_documents(pages)
                
                # Store chunks in semantic memory
                for chunk in chunks:
                    self.memory.add_entry({
                        "content": chunk.page_content,
                        "metadata": {
                            "source": pdf_file,
                            "page": chunk.metadata.get("page", 0)
                        }
                    }, self.collection_name)
                
                print(f"Successfully processed {pdf_file}")
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                continue 