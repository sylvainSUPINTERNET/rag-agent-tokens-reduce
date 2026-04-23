from dotenv import load_dotenv
from langchain.messages import AIMessage
load_dotenv()

import json
import base64
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from numpy import dot
from numpy.linalg import norm

def main():
    with open('generative_response_step1.json', 'r', encoding='utf-8') as f:
        content = f.read()
    data = json.loads(content)
    

    # gemini-embedding-2 => 3072 ! ( is not working with indexing hnsw / ivfflat ...)
    model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")
    vector = model.embed_query(json.dumps(data))
    print(vector)



# no is too long
def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

if __name__ == "__main__":
    main()