from typing import AsyncIterable
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
import uvicorn
import os
from langchain_openai import ChatOpenAI
import numpy as np
import pandas as pd
from langchain_core.prompts import PromptTemplate
from fastapi.responses import StreamingResponse
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
import pickle

os.environ["OPENAI_API_KEY"] = "sk-proj-P1fr2jSQpx8JfDkbI03PT3BlbkFJiA1L0UrDQUsLCR04In82"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    content: str


def load_db(filename):
        with open(filename, 'rb') as f:
            db = pickle.load(f)
        print(">>> Database loaded successfully <<<")

        return db

async def send_message(content: str) -> AsyncIterable[str]:
    loaded_db = load_db('vector_db.pkl')
    retriever = loaded_db.as_retriever(search_type='similarity', search_kwargs={'k': 3})
    context = retriever.get_relevant_documents(content)

    prompt = """
    You are a helpful assistant in question answering. 
    Your job is to answer user query based on a given context. 
    If the answer is NOT in the context say the question is not related to the information in the context.

    Context: {context}
    User query: {input}
    """

    Rag_prompt = PromptTemplate(
        template=prompt, input_variables=["input", "context"])

    llm_rag = ChatOpenAI(streaming=True, model="gpt-3.5-turbo", temperature=0.000001,
                         callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

    chain = LLMChain(llm=llm_rag, prompt=Rag_prompt, verbose=False)

    async for chunk in chain.astream({
        "input": content,
        "context": context
    }):
        content = chunk["text"]
        yield  f" {content} \n\n"


@app.post("/stream_chat/")
async def stream_chat(message: Message):
    async def generate():
        async for chunk in send_message(message.content):
            yield chunk.encode()

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app)
