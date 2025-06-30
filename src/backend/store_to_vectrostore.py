import json
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings



def load_log_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    documents = []
    for entry in logs:
        log_type = entry.get("log_type", "")
        description = entry.get("description", "")
        fields = entry.get("fields", [])

        # Format fields nicely
        field_lines = [f"- {f['name']} ({f['unit']}): {f['meaning']}" for f in fields]
        content = f"type:{log_type}\n\n{description}\n\nFields:\n" + "\n".join(field_lines)

        documents.append(Document(
            page_content=content,
            metadata={"log_type": log_type}
        ))

    return documents


def store_in_faiss(documents, output_dir="rag_vector_store"):
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(output_dir)
    print(f"✅ Saved {len(documents)} log messages to: {output_dir}")


def main():
    json_path = "log_definitions.json"
    docs = load_log_json(json_path)
    store_in_faiss(docs)


if __name__ == "__main__":
    main()
