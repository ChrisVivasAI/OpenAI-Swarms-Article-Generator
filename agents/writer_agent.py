from swarm import Agent
from utils.embedding_utils import generate_embedding
from supabase import create_client
from datetime import datetime
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_article_to_db(context_variables):
    """Save the article to the Supabase 'writer' table."""
    article_title = context_variables.get("article_title")
    article_text = context_variables.get("article_text")
    ideation_id = context_variables.get("ideation_id")
    research_id = context_variables.get("research_id")

    if not all([article_title, article_text, ideation_id, research_id]):
        logger.error("Missing required article information.")
        return "Failed to save article: Missing required information."

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

        embedding = generate_embedding(article_text)
        data = {
            "ideation_id": ideation_id,
            "research_id": research_id,
            "article_text": article_text,
            "embedding": embedding,
            "date_created": datetime.utcnow().isoformat()
        }

        response = supabase.table("writer").insert(data).execute()
        logger.info("Article successfully saved to the database.")
        return "Article successfully saved to the database."
    except ValueError as e:
        logger.error(f"Error converting IDs to integers: {str(e)}")
        return f"Failed to save article: Invalid ID format"
    except Exception as e:
        logger.error(f"Error saving article to database: {str(e)}")
        return f"Failed to save article: {str(e)}"

writer_agent = Agent(
    name="Writer Agent",
    instructions="""You are a professional article writer. Using the provided research data, create a well-structured article.
    Your response MUST be in the following JSON format without any special characters or line breaks within the text values:

    {
        "article_title": "Title of the article",
        "article_text": "# [Article Title]\\n\\n[Main article content structured in sections]\\n\\n## Practical Exercise\\n[Detailed exercise for readers]\\n\\n## References\\n[References in APA format]"
    }

    Guidelines:
    1. Use \\n for line breaks in article_text
    2. Escape any quotes within the text using \\"
    3. Do not use any control characters
    4. Keep JSON structure clean and valid
    5. Use markdown formatting for article structure
    6. Keep content professional and well-organized""",
    functions=[save_article_to_db]
)
