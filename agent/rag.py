import os
import hashlib

import chromadb

from llama_index.core import (
    Document,
    Settings,
    VectorStoreIndex,
    StorageContext
)

from llama_index.core.node_parser import SentenceSplitter

from llama_index.embeddings.huggingface import (
    HuggingFaceEmbedding
)

from llama_index.vector_stores.chroma import (
    ChromaVectorStore
)


# =========================================================
# Configuration
# =========================================================

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "studymate"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


# Keep chunks reasonably small so retrieval can
# return focused pieces of the lecture.
CHUNK_SIZE = 100

CHUNK_OVERLAP = 20


# Retrieve more evidence for the Researcher.
TOP_K = 8


# =========================================================
# Embedding Model
# =========================================================

Settings.embed_model = HuggingFaceEmbedding(
    model_name=EMBEDDING_MODEL
)


# =========================================================
# Chroma Database
# =========================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = chroma_client.get_or_create_collection(
    COLLECTION_NAME
)


vector_store = ChromaVectorStore(
    chroma_collection=collection
)


storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


# =========================================================
# Read Document
# =========================================================

def get_file_text(file_path: str) -> list[Document]:
    """
    Read PDF, TXT, or Markdown files.

    For PDFs, every page becomes a separate Document
    so page numbers can be preserved in the metadata.
    """

    extension = os.path.splitext(
        file_path
    )[1].lower()


    documents = []


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if extension == ".pdf":

        import fitz

        pdf = fitz.open(
            file_path
        )


        for page_number, page in enumerate(
            pdf,
            start=1
        ):

            text = page.get_text(
                "text"
            ).strip()


            if not text:
                continue


            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": os.path.basename(
                            file_path
                        ),
                        "page": page_number
                    }
                )
            )


        pdf.close()


    # -----------------------------------------------------
    # TXT / Markdown
    # -----------------------------------------------------

    elif extension in [
        ".txt",
        ".md"
    ]:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read().strip()


        if text:

            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": os.path.basename(
                            file_path
                        ),
                        "page": 1
                    }
                )
            )


    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


    return documents


# =========================================================
# Stable Document ID
# =========================================================

def make_document_id(file_path: str) -> str:
    """
    Create a stable ID based on the FILE CONTENT.

    This is important because Streamlit stores uploaded
    files in temporary paths. The temporary filename can
    change every time the same document is uploaded.

    Hashing the content means the same document always
    gets the same document_id.
    """

    hasher = hashlib.sha256()


    with open(
        file_path,
        "rb"
    ) as f:

        while True:

            data = f.read(
                1024 * 1024
            )


            if not data:
                break


            hasher.update(
                data
            )


    return hasher.hexdigest()


# =========================================================
# Add Document
# =========================================================

def add_document(file_path: str) -> int:
    """
    Read, chunk, embed and store a document.

    If the exact same file already exists,
    its previous chunks are removed first.

    Returns the number of chunks stored.
    """

    documents = get_file_text(
        file_path
    )


    if not documents:

        return 0


    # -----------------------------------------------------
    # Stable ID based on content
    # -----------------------------------------------------

    document_id = make_document_id(
        file_path
    )


    # -----------------------------------------------------
    # Remove previous copy
    # -----------------------------------------------------

    try:

        collection.delete(
            where={
                "document_id": document_id
            }
        )

        print(
            "[RAG] Removed previous copy "
            "of the same document."
        )

    except Exception as e:

        print(
            f"[RAG] Could not remove old copy: {e}"
        )


    # -----------------------------------------------------
    # Split into chunks
    # -----------------------------------------------------

    splitter = SentenceSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP
    )


    nodes = splitter.get_nodes_from_documents(
        documents
    )


    # -----------------------------------------------------
    # Add metadata
    # -----------------------------------------------------

    for index, node in enumerate(
        nodes
    ):

        node.metadata["document_id"] = (
            document_id
        )


        node.metadata["chunk_id"] = (
            f"{document_id}_chunk_{index}"
        )


    # -----------------------------------------------------
    # Store vectors
    # -----------------------------------------------------

    if nodes:

        VectorStoreIndex(
            nodes,
            storage_context=storage_context
        )


    print(
        f"[RAG] Added {len(nodes)} chunks "
        f"from {os.path.basename(file_path)}"
    )


    print(
        f"[RAG] Document ID: {document_id[:12]}..."
    )


    print(
        f"[RAG] Collection size: "
        f"{collection.count()}"
    )


    return len(nodes)


# =========================================================
# Search Documents
# =========================================================

def search_documents(
    query: str,
    top_k: int = TOP_K
) -> list[dict]:
    """
    Search the persistent Chroma knowledge base.

    Returns the most relevant chunks with their
    source, page, score and chunk ID.
    """

    if collection.count() == 0:

        return []


    index = VectorStoreIndex.from_vector_store(
        vector_store
    )


    retriever = index.as_retriever(
        similarity_top_k=top_k
    )


    hits = retriever.retrieve(
        query
    )


    results = []


    for hit in hits:

        metadata = hit.node.metadata


        results.append(
            {
                "text": hit.node.text,

                "score": float(
                    hit.score or 0.0
                ),

                "source": metadata.get(
                    "source",
                    "unknown"
                ),

                "page": metadata.get(
                    "page",
                    0
                ),

                "chunk_id": metadata.get(
                    "chunk_id",
                    hit.node.node_id
                )
            }
        )


    return results


# =========================================================
# Research Helper
# =========================================================

def research_task(
    task: str,
    top_k: int = TOP_K
) -> str:
    """
    Retrieve relevant Knowledge Base evidence
    for one research task.
    """

    results = search_documents(
        task,
        top_k=top_k
    )


    if not results:

        return (
            "No relevant information was found "
            "in the uploaded documents."
        )


    parts = []


    for result in results:

        parts.append(
            f"""
[Source: {result['source']} |
Page: {result['page']} |
Chunk: {result['chunk_id']} |
Score: {result['score']:.3f}]

{result['text']}
"""
        )


    return "\n\n".join(
        parts
    )


# =========================================================
# Search With Multiple Queries
# =========================================================

def research_tasks(
    tasks: list[str],
    top_k: int = TOP_K
) -> str:
    """
    Retrieve Knowledge Base evidence for multiple
    research tasks.

    This is useful for the Planner retry because
    it gives the model a broader view of the
    available Knowledge Base.
    """

    if not tasks:

        return (
            "No research tasks were provided."
        )


    sections = []


    for task in tasks:

        context = research_task(
            task,
            top_k=top_k
        )


        sections.append(
            f"""
RESEARCH TASK:
{task}

KNOWLEDGE BASE EVIDENCE:
{context}

==================================================
"""
        )


    return "\n".join(
        sections
    )


# =========================================================
# Collection Count
# =========================================================

def get_collection_count() -> int:
    """
    Return the number of stored chunks.
    """

    return collection.count()


# =========================================================
# Clear Database
# =========================================================

def clear_database():
    """
    Delete all vectors from the Knowledge Base.
    """

    try:

        collection.delete(
            where={}
        )

    except Exception as e:

        print(
            f"[RAG] Error clearing database: {e}"
        )


    print(
        "[RAG] Knowledge base cleared."
    )


# =========================================================
# Database Information
# =========================================================

def print_database_info():

    print(
        "========================================"
    )

    print(
        "RAG DATABASE"
    )

    print(
        "========================================"
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Chunks: {collection.count()}"
    )

    print(
        f"Embedding: {EMBEDDING_MODEL}"
    )

    print(
        f"Top K: {TOP_K}"
    )

    print(
        "========================================"
    )


# =========================================================
# Simple Test
# =========================================================

if __name__ == "__main__":

    print(
        "RAG system loaded."
    )


    print_database_info()