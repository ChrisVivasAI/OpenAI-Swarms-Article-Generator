from swarm import Agent
from utils.embedding_utils import generate_embedding
from database.db_utils import insert_research_with_embedding
import requests
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
SERPAPI_URL = "https://serpapi.com/search"

def perform_research(context_variables, idea_title):
    """Perform research using SerpAPI based on the idea title."""
    query = idea_title
    params = {
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_API_KEY,
        "num": 5,  # Limit the number of results to avoid excessive data
    }
    try:
        logger.info("Performing search on SerpAPI...")
        response = requests.get(SERPAPI_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract titles and snippets of the search results
        results = data.get("organic_results", [])
        summaries = [
            f"{result.get('title')}: {result.get('snippet')}"
            for result in results
            if result.get("title") and result.get("snippet")
        ]

        research_text = "\n".join(summaries)
        references_urls = ", ".join(
            [result.get("link") for result in results if result.get("link")]
        )

        logger.info("Search completed successfully.")
        return research_text, references_urls

    except Exception as e:
        logger.error(f"Error during SerpAPI research: {str(e)}", exc_info=True)
        return None, None

def save_research_to_db(idea_id, title, research_text, references):
    """Save research data to the database."""
    try:
        logger.info("Generating embedding for research data...")
        embedding = generate_embedding(f"{title} {research_text}")

        if embedding:
            logger.info("Embedding generated successfully. Saving to database...")
            response = insert_research_with_embedding(title, research_text, references, embedding, idea_id)
            if response:
                logger.info(f"Research data saved successfully: {response}")
            else:
                logger.error("Failed to save research data to the database.")
        else:
            logger.error("Failed to generate embedding.")

    except Exception as e:
        logger.error(f"Error saving research data: {str(e)}", exc_info=True)

# Updated instructions in research_agent.py
research_agent = Agent(
    name="Research Agent",
    instructions="You are a research assistant. Based on the idea title provided, conduct research using SerpAPI. "
    "Summarize the findings and respond strictly in this JSON format:\n"
    "{ 'research_title': '<researc_title>', 'research_description': '<research_text>', 'references': '<comma-separated-links>' }."
    "Ensure the response is valid JSON, concise, and accurate.",
    functions=[perform_research],
)
