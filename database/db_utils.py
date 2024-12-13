from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)

def insert_idea_with_embedding(idea_title, description, embedding):
    """
    Insert an idea along with its embedding into the Supabase 'ideation' table.
    
    Args:
        idea_title (str): The title of the idea.
        description (str): The description of the idea.
        embedding (list): The embedding vector.
    
    Returns:
        dict: Response from Supabase.
    """
    try:
        response = supabase.table("ideation").insert({
            "idea_title": idea_title,
            "description": description,
            "embedding": embedding
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error inserting data into ideation table: {e}")
        return None

def insert_research_with_embedding(research_title, research_text, reference_urls, embedding, ideation_id):
    """
    Insert research data along with its embedding into the Supabase 'research' table.

    Args:
        research_title (str): Title of the research.
        research_text (str): Full text of the research.
        reference_urls (str): Comma-separated reference URLs.
        embedding (list): Embedding vector for the research.
        ideation_id: Ideation ID linked to this research (can be int, list, or dict).

    Returns:
        dict: Response from Supabase.
    """
    try:
        # Debug log ideation_id
        print(f"Debug: Received ideation_id: {ideation_id}")

        # Handle cases where ideation_id is a list of dicts
        if isinstance(ideation_id, list):
            # Assume list contains dicts with 'id' as key
            if len(ideation_id) == 1 and isinstance(ideation_id[0], dict) and "id" in ideation_id[0]:
                ideation_id = ideation_id[0]["id"]
            else:
                raise ValueError("ideation_id format is incorrect. Expected a single dictionary with an 'id' key.")

        # Ensure ideation_id is an integer
        ideation_id = int(ideation_id)

        # Check if embedding is a valid list of floats or integers
        if not isinstance(embedding, list) or not all(isinstance(val, (float, int)) for val in embedding):
            raise ValueError("Embedding must be a list of floats or integers.")

        # Insert data into the research table
        response = supabase.table("research").insert({
            "research_title": research_title,
            "research_text": research_text,
            "references_urls": reference_urls,
            "embedding": embedding,
            "ideation_id": ideation_id
        }).execute()
        
        # Return the ID of the inserted research
        if response.data and len(response.data) > 0:
            return response.data[0].get('id')
        return None
        
    except Exception as e:
        logger.error(f"Error inserting data into research table: {e}")
        return None

def insert_article_with_embedding(article_text, embedding, ideation_id, research_id):
    """
    Insert article data along with its embedding into the Supabase 'writer' table.
    """
    try:
        # Handle ideation_id formatting
        if isinstance(ideation_id, list):
            if len(ideation_id) == 1 and isinstance(ideation_id[0], dict) and "id" in ideation_id[0]:
                ideation_id = ideation_id[0]["id"]
        ideation_id = int(ideation_id)

        # Handle research_id formatting
        if isinstance(research_id, list):
            if len(research_id) == 1 and isinstance(research_id[0], dict) and "id" in research_id[0]:
                research_id = research_id[0]["id"]
        research_id = int(research_id)

        response = supabase.table("writer").insert({
            "article_text": article_text,
            "embedding": embedding,
            "ideation_id": ideation_id,
            "research_id": research_id,
            "date_created": datetime.utcnow().isoformat()
        }).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0].get('id')
        return None
        
    except Exception as e:
        logger.error(f"Error inserting data into writer table: {e}")
        return None

