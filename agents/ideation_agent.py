from swarm import Agent
from utils.embedding_utils import generate_embedding
from supabase import create_client
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_idea_to_db(context_variables):
    """
    Save the idea to the Supabase 'ideation' table.
    """
    idea_title = context_variables.get("idea_title")
    description = context_variables.get("description")

    if not idea_title or not description:
        logger.error("Idea title or description is missing.")
        return "Failed to save idea: Missing title or description."

    # Generate embeddings
    logger.info("Generating embeddings for idea title and description...")
    try:
        embedding = generate_embedding(description)

        # Insert into the database
        data = {
            "idea_title": idea_title,
            "description": description,
            "embedding": embedding,
            "date_created": datetime.utcnow().isoformat()
        }

        response = supabase.table("ideation").insert(data).execute()
        if response.get("error"):
            raise Exception(response["error"]["message"])
        logger.info("Idea successfully saved to the database.")
        return "Idea successfully saved to the database."
    except Exception as e:
        logger.error(f"Error saving idea to the database: {str(e)}")
        return f"Failed to save idea: {str(e)}"

# Define the agent
ideation_agent = Agent(
    name="Ideation Agent",
    instructions="You are an ideation agent. Generate a single article idea and respond with a JSON object in the following format:\n"
                 "{ 'idea_title': '<title>', 'description': '<description>' }. "
                 "Ensure the response is clear and concise.",
    functions=[save_idea_to_db]
)
