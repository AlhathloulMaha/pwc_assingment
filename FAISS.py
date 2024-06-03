import pickle
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

class ChunkAndEmbed:
    def __init__(self, directory='/Users/mahaalhathloul/Desktop/doccs', model_name='intfloat/multilingual-e5-base'):
        self.directory = directory
        self.model_name = model_name

    def chunk_and_embed(self):
        loader = DirectoryLoader(self.directory)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=20)
        docs = text_splitter.split_documents(documents)
        hf = HuggingFaceEmbeddings(model_name=self.model_name, encode_kwargs={"normalize_embeddings": True})
        db = FAISS.from_documents(documents=docs, embedding=hf)
        print(">>> Successfully completed the chunking and embedding <<<")
        return db

    def save_db(self, db, filename):
        with open(filename, 'wb') as f:
            pickle.dump(db, f)
        print(">>> Database saved successfully <<<")


if __name__ == "__main__":
    chunk_and_embedder = ChunkAndEmbed()
    db = chunk_and_embedder.chunk_and_embed()

    # Save the database
    chunk_and_embedder.save_db(db, 'vector_db.pkl')
