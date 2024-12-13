from swarm import Swarm
from agents.ideation_agent import ideation_agent
from agents.research_agent import research_agent
from agents.writer_agent import writer_agent
from utils.embedding_utils import generate_embedding
from database.db_utils import insert_idea_with_embedding, insert_research_with_embedding, insert_article_with_embedding
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_json_response(raw_response):
    """Clean and prepare JSON response from raw string."""
    if raw_response.startswith("```") and raw_response.endswith("```"):
        raw_response = raw_response.strip("`")  # Remove triple backticks
        if raw_response.startswith("json"):
            raw_response = raw_response[4:].strip()  # Remove 'json' label if present
    return raw_response

def main():
    try:
        # Step 1: Ideation Agent
        logger.info("Starting conversation with Ideation Agent...")
        client = Swarm()
        ideation_response = client.run(
            agent=ideation_agent,
            messages=[
                {"role": "user", "content": "I need help coming up with an idea for an article about AI."},
                {"role": "user", "content": "Let's focus on content creation using AI."},
                {"role": "user", "content": "Can you suggest one refined idea in JSON format?"}
            ]
        )

        # Parse ideation response
        logger.info("Processing Ideation Agent response...")
        ideation_message = ideation_response.messages[-1]["content"]
        try:
            idea_details = json.loads(ideation_message)
            idea_title = idea_details.get("idea_title")
            description = idea_details.get("description")

            if not (idea_title and description):
                logger.error("Failed to extract idea details from the Ideation Agent response.")
                return

            logger.info(f"Idea extracted: {idea_title}")
            logger.info(f"Description: {description}")

            # Generate embedding for the idea
            logger.info("Generating embedding for the idea description...")
            embedding = generate_embedding(description)

            if embedding:
                logger.info("Embedding generated successfully.")
                # Save idea to database
                logger.info("Saving idea to database...")
                idea_id = insert_idea_with_embedding(idea_title, description, embedding)
                if idea_id:
                    logger.info(f"Idea saved with ID: {idea_id}")
                else:
                    logger.error("Failed to save idea to the database.")
                    return
            else:
                logger.error("Failed to generate embedding for the idea.")
                return

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ideation Agent response: {str(e)}")
            return

        # Step 2: Research Agent
        logger.info("Starting conversation with Research Agent...")
        research_response = client.run(
            agent=research_agent,
            messages=[
                {"role": "system", "content": f"Research the following idea: {idea_title}"}
            ],
            context_variables={"idea_title": idea_title}
        )

        # Parse research response
        logger.info("Processing Research Agent response...")
        research_message = research_response.messages[-1]["content"]
        logger.info(f"Raw Research Agent response: {research_message}")  # Log the raw response
        try:
            # Clean and parse JSON response
            cleaned_response = clean_json_response(research_message)
            research_data = json.loads(cleaned_response)
            research_title = research_data.get("research_title")
            research_text = research_data.get("research_description")
            references = research_data.get("references")

            if not (research_title and research_text):
                logger.error("Failed to extract research details from the Research Agent response.")
                return

            logger.info(f"Research Title: {research_title}")
            logger.info(f"Research Text: {research_text}")
            logger.info(f"References: {references}")

            # Save research data to the database
            logger.info("Saving research data to database...")
            embedding = generate_embedding(f"{research_title} {research_text}")
            if embedding:
                research_id = insert_research_with_embedding(research_title, research_text, references, embedding, idea_id)
                if research_id:
                    logger.info(f"Research saved with ID: {research_id}")
                    
                    # Now we can proceed with the Writer Agent
                    logger.info("Starting conversation with Writer Agent...")
                    writer_response = client.run(
                        agent=writer_agent,
                        messages=[
                            {
                                "role": "system", 
                                "content": f"Using this research data:\nTitle: {research_title}\n\nContent: {research_text}\n\nReferences: {references}\n\nCreate a comprehensive article."
                            }
                        ],
                        context_variables={
                            "ideation_id": idea_id,
                            "research_id": research_id
                        }
                    )
                else:
                    logger.error("Failed to save research to the database.")
                    return
            else:
                logger.error("Failed to generate embedding for research data.")
                return

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Research Agent response: {str(e)}")

        # Step 3: Writer Agent
        logger.info("Starting conversation with Writer Agent...")
        writer_response = client.run(
            agent=writer_agent,
            messages=[
                {
                    "role": "system", 
                    "content": f"Using this research data:\nTitle: {research_title}\n\nContent: {research_text}\n\nReferences: {references}\n\nCreate a comprehensive article."
                }
            ],
            context_variables={
                "ideation_id": idea_id,
                "research_id": research_id
            }
        )

        # Parse writer response
        logger.info("Processing Writer Agent response...")
        writer_message = writer_response.messages[-1]["content"]
        logger.info("Raw Writer Agent response:")
        logger.info("----------------------------------------")
        logger.info(writer_message)
        logger.info("----------------------------------------")
        logger.info("Attempting to clean response...")
        try:
            cleaned_response = clean_json_response(writer_message)
            article_data = json.loads(cleaned_response)
            article_title = article_data.get("article_title")
            article_text = article_data.get("article_text")

            if not (article_title and article_text):
                logger.error("Failed to extract article details from Writer Agent response.")
                return None

            logger.info(f"Article created: {article_title}")
            
            # Save article to database
            logger.info("Saving article to database...")
            embedding = generate_embedding(article_text)
            if embedding:
                insert_article_with_embedding(article_text, embedding, idea_id, research_id)
                logger.info("Article saved successfully.")
                # Return the article data
                return {
                    "article_title": article_title,
                    "article_text": article_text,
                    "idea_title": idea_title,
                    "research_title": research_title,
                    "references": references
                }
            else:
                logger.error("Failed to generate embedding for article.")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Writer Agent response: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    main()
