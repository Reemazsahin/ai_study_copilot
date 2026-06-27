print("VECTOR_STORE_LOADED")
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

print("Creating vector store..")
print("VECTOR_STORE_LOADED")
def split_text(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)


_embedding_model = None

class CustomEmbeddings:
    def __init__(self):
        global _embedding_model
        import os
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        if _embedding_model is None:
            print("Loading Embedding Model")
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("MODEL END")
        self.model = _embedding_model
    def __call__(self, text):          
        return self.embed_query(text)   

    def embed_documents(self, texts):
        print("Embedding documents...")
        return self.model.encode(texts,show_progress_bar=False).tolist()

    def embed_query(self, text):
        print("Embedding query...")
        return self.model.encode(text,show_progress_bar=False).tolist()


def create_vector_store(chunks):
    print("STEP 1")

    docs = [
        Document(page_content=chunk)
        for chunk in chunks
    ]
    print("STEP 2")

    embeddings = CustomEmbeddings()
    print("STEP 3")

    db=FAISS.from_documents(
        docs,
        embeddings
    )

    print("STEP 4")
    return db


def search_pdf(vector_store, query):

    return vector_store.similarity_search(
        query,
        k=2
    )