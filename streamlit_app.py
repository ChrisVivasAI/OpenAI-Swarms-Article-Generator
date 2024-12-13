import streamlit as st
import sys
import io
from contextlib import redirect_stdout
import json
import time
import main
import logging
from datetime import datetime

# Configure custom logger for capturing output
class StreamlitHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.log_text = ""
        self.stages = {
            "ideation": {"started": False, "completed": False},
            "research": {"started": False, "completed": False},
            "writing": {"started": False, "completed": False}
        }

    def emit(self, record):
        log_entry = self.format(record)
        self.log_text += log_entry + "\n"
        
        # Update stages based on log messages
        if "Starting conversation with Ideation Agent" in log_entry:
            self.stages["ideation"]["started"] = True
            st.session_state["ideation_status"].info("🤔 Generating Ideas...")
        elif "Idea saved with ID" in log_entry:
            self.stages["ideation"]["completed"] = True
            self.stages["research"]["started"] = True
            st.session_state["ideation_status"].success("✅ Ideation Complete")
            st.session_state["research_status"].info("🔍 Conducting Research...")
        elif "Research saved with ID" in log_entry:
            self.stages["research"]["completed"] = True
            self.stages["writing"]["started"] = True
            st.session_state["research_status"].success("✅ Research Complete")
            st.session_state["writing_status"].info("✍️ Writing Article...")
        elif "Article saved successfully" in log_entry:
            self.stages["writing"]["completed"] = True
            st.session_state["writing_status"].success("✅ Writing Complete")

        # Update the placeholder with the full log text
        self.placeholder.code(self.log_text)

def initialize_page():
    st.set_page_config(
        page_title="AI Article Generator",
        page_icon="📝",
        layout="wide"
    )
    st.title("AI Article Generation Pipeline")
    st.markdown("""
    This application generates articles using OpenAI's Swarm Framework. It utilizes a three-stage AI pipeline with advanced capabilities:

    1. **Ideation Agent**: 
        - Generates creative article ideas
        - Creates embeddings for semantic search and storage
    
    2. **Research Agent**: 
        - Conducts web research using SERPAPI for real-time data
        - Summarizes findings with citations
        - Generates embeddings for research content
    
    3. **Writing Agent**: 
        - Creates comprehensive articles
        - Maintains semantic context through embeddings
        - Formats content with proper citations
    
    Each stage utilizes embedding technology to maintain semantic understanding and enable future content retrieval.
    """)
    
    # Add topic input field
    topic = st.text_input("🎯 Enter your article topic:", 
                         placeholder="e.g., Artificial Intelligence in Healthcare",
                         help="Enter a topic for your article. Be as specific as you'd like.")
    
    return topic

def create_status_containers():
    # Create three columns for the stages
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state["ideation_status"] = st.empty()
        st.session_state["ideation_status"].error("⏳ Waiting to Start")
        
    with col2:
        st.session_state["research_status"] = st.empty()
        st.session_state["research_status"].error("⏳ Waiting to Start")
        
    with col3:
        st.session_state["writing_status"] = st.empty()
        st.session_state["writing_status"].error("⏳ Waiting to Start")

def display_article(article_data):
    """Display the generated article in a formatted way"""
    if not article_data:
        st.error("No article data available to display")
        return

    # Create a container for the article
    article_container = st.container()
    
    with article_container:
        # Article Header
        st.header("📝 Generated Article", divider="rainbow")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📖 Article View", "🔍 Article Details", "📝 Raw Markdown"])
        
        with tab1:
            # Main article view
            st.markdown(f"# {article_data['article_title']}")
            st.markdown(article_data['article_text'])
        
        with tab2:
            # Article metadata and details
            st.subheader("Article Information")
            st.write(f"**Original Idea:** {article_data['idea_title']}")
            st.write(f"**Research Topic:** {article_data['research_title']}")
            
            # Display references if available
            if article_data.get('references'):
                st.subheader("References")
                st.markdown(article_data['references'])
        
        with tab3:
            # Raw markdown view
            st.text_area(
                "Markdown Content",
                value=f"# {article_data['article_title']}\n\n{article_data['article_text']}",
                height=400
            )
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as Markdown",
                data=f"# {article_data['article_title']}\n\n{article_data['article_text']}",
                file_name=f"{article_data['article_title'].lower().replace(' ', '_')}.md",
                mime="text/markdown"
            )
        
        with col2:
            # Create HTML version for download
            html_content = f"""
            <html>
            <head>
                <title>{article_data['article_title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    .references {{ margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <h1>{article_data['article_title']}</h1>
                {article_data['article_text']}
                <div class="references">
                    <h2>References</h2>
                    {article_data.get('references', '')}
                </div>
            </body>
            </html>
            """
            st.download_button(
                label="📥 Download as HTML",
                data=html_content,
                file_name=f"{article_data['article_title'].lower().replace(' ', '_')}.html",
                mime="text/html"
            )

def run_generation_pipeline(topic):
    # Create expandable section for logs, initially expanded
    logs_expander = st.expander("View Detailed Logs", expanded=True)
    
    with logs_expander:
        log_placeholder = st.empty()
    
    # Create and configure the custom handler
    handler = StreamlitHandler(log_placeholder)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Get the root logger and add our custom handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)
    logger.addHandler(handler)
    
    try:
        # Capture stdout and run the main process
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            article_data = main.main(topic)  # Now captures the returned article data
        
        # Get the captured output
        output = buffer.getvalue()
        
        if article_data:
            # Show success message
            st.success("✨ Article generation completed successfully!")
            # Collapse the logs expander
            logs_expander.expanded = False
            # Display the article
            display_article(article_data)
        else:
            st.error("Article generation failed or returned no content")
        
    except Exception as e:
        st.error(f"An error occurred during generation: {str(e)}")
        st.exception(e)
    finally:
        # Remove our custom handler
        logger.removeHandler(handler)

def main_ui():
    topic = initialize_page()
    create_status_containers()
    
    # Add start button
    if st.button("🚀 Start Generation", use_container_width=True):
        if not topic:
            st.error("Please enter a topic before starting generation.")
            return
            
        with st.spinner("Initializing AI Pipeline..."):
            run_generation_pipeline(topic)

if __name__ == "__main__":
    main_ui()