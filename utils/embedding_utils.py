from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text):
    """
    Generate embeddings for the given text using text-embedding-ada-002.
    
    Args:
        text (str): The input text for which embeddings are needed.

    Returns:
        list: The embedding vector (1536-dimensional).
    """
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
