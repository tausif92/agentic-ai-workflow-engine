from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


class LongTermMemory:
    """
    Vector memory using LangChain + OpenAI Embeddings + FAISS
    """

    def __init__(self):

        # 🔹 Embedding model
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # cheaper & fast
        )

        # 🔹 Initialize empty DB
        self.db = None
        self.texts = []

    def store(self, text: str):
        """
        Store new knowledge
        """

        if not text:
            return

        self.texts.append(text)

        # Rebuild index (simple approach for now)
        self.db = FAISS.from_texts(self.texts, self.embeddings)

    def retrieve(self, query: str, k: int = 3):
        """
        Retrieve relevant knowledge
        """

        if not self.db:
            return []

        docs = self.db.similarity_search(query, k=k)

        return [doc.page_content for doc in docs]
