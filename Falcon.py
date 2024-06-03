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
    "prompt": user_query,
    "temperature": 1,
    "system_prompt": f"""
    You are a helpful assistant in question answering. 
    Your job is to answer user query based on a given context. 
    If the answer is NOT in the context say the question is not related to the information in the context.
    Context: {context}
    """
}

output = replicate.run(
    "joehoover/falcon-40b-instruct:7d58d6bddc53c23fa451c403b2b5373b1e0fa094e4e0d1b98c3d02931aa07173",
    input=input
)
print("".join(output))
#=> "Thy heart shall bloom like an open source flower,\nAnd l...

for event in replicate.stream(
    "meta/llama-2-70b-chat",
    input=input
):
    print(event, end="")