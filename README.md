# AI Article Creation System with Swarm Framework

## Overview
This project is an intelligent article creation system built using OpenAI's Swarm Framework. It demonstrates the power of multi-agent collaboration in content creation, utilizing advanced AI capabilities including semantic search and embeddings.

## Current Features

### Multi-Agent Workflow

#### Ideation Agent
- Generates unique article ideas
- Creates structured idea proposals
- Stores ideas with semantic embeddings

#### Research Agent
- Performs web research using SerpAPI
- Summarizes findings
- References source materials
- Stores research with embeddings

#### Writer Agent
- Creates well-structured articles
- Includes practical exercises
- Formats references in APA style
- Maintains semantic context through embeddings

## Technical Implementation
- Built on OpenAI's Swarm Framework
- Utilizes embedding models for semantic understanding
- Integrates with Supabase for structured data storage
- Implements SerpAPI for research capabilities

## Database Schema
![Database](/database.png)

### Key Components
Referenced from codebase:
- **Ideation Agent:** Handles the generation and storage of article ideas, including embeddings.
- **Research Agent:** Conducts semantic web research and stores summaries and references with embeddings.
- **Writer Agent:** Produces articles, maintains semantic relationships, and formats output.

## Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key
- SerpAPI key
- Supabase account

### Environment Setup

1. Create and activate a virtual environment:

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
.\venv\Scripts\activate.bat

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

2. Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
SERPAPI_KEY=your_serpapi_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd article-swarm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install development dependencies (optional):
```bash
pip install -r requirements-dev.txt
```

### Project Structure
```
backend/
├── agents/
│   ├── __init__.py
│   ├── ideation_agent.py
│   ├── research_agent.py
│   └── writer_agent.py
├── database/
│   ├── __init__.py
│   └── supabase_client.py
├── utils/
│   ├── __init__.py
│   ├── embeddings.py
│   └── serpapi_client.py
├── main.py
├── requirements.txt
└── .env
```

### Basic Usage

1. Start the application:
```bash
python main.py
```

2. Example code for using the Ideation Agent:
```python
from agents.ideation_agent import IdeationAgent
from utils.embeddings import get_embedding

# Initialize the agent
ideation_agent = IdeationAgent()

# Generate article idea
idea = ideation_agent.generate_idea(topic="AI Technology")

# Get embedding for the idea
idea_embedding = get_embedding(idea.text)

# Store in database
idea.store(embedding=idea_embedding)
```

3. Example code for the Research Agent:
```python
from agents.research_agent import ResearchAgent
from utils.serpapi_client import SerpAPIClient

# Initialize agents
research_agent = ResearchAgent()
serp_client = SerpAPIClient()

# Conduct research
research_results = research_agent.research(
    topic="AI Technology",
    search_client=serp_client,
    num_sources=5
)

# Store research with embeddings
research_agent.store_research(research_results)
```

### Dependencies
Key packages and their versions:

```txt
# requirements.txt
openai>=1.0.0
python-dotenv>=1.0.0
supabase>=1.0.3
google-search-results>=2.4.2
numpy>=1.24.3
pandas>=2.0.3
pytest>=7.4.0  # for testing
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
We use Black for code formatting:
```bash
black .
```

## Roadmap

### Upcoming Features

#### Editor Agent
- Quality scoring system
- Revision suggestions
- Iterative improvement workflow

#### Orchestration Agent
- Workflow management
- Agent coordination
- Quality control

### Enhanced Embedding Integration
- Knowledge base development
- Semantic search capabilities
- Context-aware content creation

### Smart Knowledge System
The system will evolve to maintain a growing knowledge base through:
- Article embeddings
- Research context preservation
- Semantic relationships between content

## Future Development

### Quality Improvement Cycle
- **Editor agent** scores articles
- Feedback loop with **writer agent**
- Continuous improvement system

### Knowledge Management
- Semantic search integration
- Context-aware article generation
- Dynamic knowledge base growth

### Workflow Optimization
- Automated agent orchestration
- Quality metrics tracking
- Performance analytics

## Troubleshooting

### Common Issues

1. Virtual Environment Activation Issues:
```bash
# If you get execution policy errors on Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Package Installation Issues:
```bash
# If pip install fails, try upgrading pip first
python -m pip install --upgrade pip
```

3. API Key Issues:
```python
# Verify your API keys are loaded correctly
import os
from dotenv import load_dotenv

load_dotenv()
assert os.getenv('OPENAI_API_KEY') is not None, "OpenAI API key not found"
```

## Contributing
We welcome contributions! Please see our contributing guidelines for more information.

## License
MIT License

This project demonstrates the potential of AI-driven content creation while laying the groundwork for more sophisticated content generation systems through agent collaboration and semantic understanding.
