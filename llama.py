import replicate
import os
import pickle

#Set the REPLICATE_API_TOKEN environment variable
os.environ["REPLICATE_API_TOKEN"] = "r8_VF2oXFHNXFEdtzsEIExr7HvdqtI6HYh44vWiz"

def load_db(filename):
        with open(filename, 'rb') as f:
            db = pickle.load(f)
        print(">>> Database loaded successfully <<<")

        return db

user_query = input("Enter your question: ")
loaded_db = load_db('/Users/mahaalhathloul/Desktop/Pwc/vector_db.pkl')
retriever = loaded_db.as_retriever(search_type='similarity', search_kwargs={'k': 3})
context = retriever.get_relevant_documents(user_query)


input = {
    "top_p": 0.95,
    "prompt": user_query,
    "temperature": 0.0001,
    "system_prompt": f"""
    You are a helpful assistant in question answering. 
    Your job is to answer user query based on a given context. 
    If the answer is NOT in the context say the question is not related to the information in the context.
    Context: {context}
    """
    ,
    "max_new_tokens": 500
}

for event in replicate.stream(
    "meta/llama-2-70b-chat",
    input=input
):
    print(event, end="")