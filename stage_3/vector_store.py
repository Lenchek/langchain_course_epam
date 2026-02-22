"""Activeloop Deep Lake vector store (same as stage_2)."""
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv

from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document

from config import ACTIVELOOP_DATASET_PATH, OPENAI_EMBEDDING_MODEL
from data_gen import STATIC_DOCS
load_dotenv(override=True)

def build_vector_store(overwrite: bool = True) -> DeepLake:
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    db = DeepLake(
        dataset_path=ACTIVELOOP_DATASET_PATH,
        embedding_function=embeddings,
        overwrite=overwrite,
    )
    docs = [Document(page_content=d["content"], metadata={"source": d["source"]}) for d in STATIC_DOCS]
    db.add_documents(docs)
    return db


def get_vector_store(read_only: bool = True) -> DeepLake:
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    return DeepLake(
        dataset_path=ACTIVELOOP_DATASET_PATH,
        embedding_function=embeddings,
        read_only=read_only,
    )
