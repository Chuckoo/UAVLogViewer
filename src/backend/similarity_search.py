from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def load_vectorstore(path="rag_vector_store"):
    """Load FAISS vector store using free HuggingFace embeddings"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(path, embeddings)


def query_vectorstore(query_text, top_k=3):
    """Run similarity search against the vector store"""
    vectorstore = FAISS.load_local(
    "rag_vector_store",
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
)

    results = vectorstore.similarity_search(query_text, k=top_k)

    print(f"\n🔎 Top {top_k} results for: '{query_text}'")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(doc.page_content)
        print("🔖 Metadata:", doc.metadata)


if __name__ == "__main__":
    # Modify this line to test different queries
    query_vectorstore("Anomaly", top_k=3)


