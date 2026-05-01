import os 
from pathlib import Path 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_openai import OpenAIEmbeddings 
from langchain_chroma import Chroma 
from langchain_core.documents import Document 
 
print("Building vector store from support corpus...") 
 
documents = [] 
data_path = Path("data") 
 
for domain in ["hackerrank", "claude", "visa"]: 
    domain_path = data_path / domain 
    if not domain_path.exists(): 
        continue 
    for md_file in domain_path.glob("**/*.md"): 
        try: 
            with open(md_file, "r", encoding="utf-8") as f: 
                content = f.read() 
            if len(content)  and "index" not in md_file.name.lower(): 
                doc = Document( 
                    page_content=content[:5000], 
                    metadata={"source": str(md_file), "domain": domain} 
                ) 
                documents.append(doc) 
                print(f"Loaded: {md_file.name}") 
        except Exception as e: 
            pass 
 
print(f"\nLoaded {len(documents)} documents") 
 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) 
chunks = text_splitter.split_documents(documents) 
print(f"Created {len(chunks)} chunks") 
 
embeddings = OpenAIEmbeddings(model="text-embedding-3-small") 
vectorstore = Chroma.from_documents( 
    documents=chunks, 
    embedding=embeddings, 
    persist_directory="./code/chroma_db" 
) 
vectorstore.persist() 
print("\n? Vector store built successfully!") 
