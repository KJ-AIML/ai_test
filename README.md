# AI Assistant for Internal Document Analysis

An intelligent AI assistant that leverages Large Language Models (LLMs) and agentic AI to extract insights from internal documents and team reports. This system helps product and engineering teams answer questions, summarize issues, and route queries intelligently.

## 📋 Overview

This project implements an AI assistant system capable of:
- Internal Q&A: Search and retrieve information from internal documents
- Issue Summarization: Analyze and summarize reported issues with severity and affected components
- Intelligent Routing: Use LLM-powered decision-making to route queries to appropriate tools
- Modular Architecture: Clean, scalable design with containerized deployment

## 🎯 Features

### Tools

#### 1. Internal Q&A Tool
Retrieves relevant information from internal documents to answer questions such as:
- "What are the issues reported on email notification?"
- "What did users say about the search bar?"

**Input Documents:**
- `ai_test_bug_report`
- `ai_test_user_feedback`

#### 2. Issue Summary Tool
Provides structured analysis of issue text, including:
- Reported issues
- Affected features/components
- Severity levels
- Requirements

### AI Agent
- Receives and processes user queries
- Decides which tool to use based on query intent
- Explains reasoning for tool selection
- Returns structured output (JSON/dict format)

## 🏗️ Architecture

```
ai_test/
├── src/
│   ├── api/
│   │   └── main.py           # FastAPI application
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py          # AI Agent implementation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── qa_tool.py        # Internal Q&A functionality
│   │   └── summarizer_tool.py # Issue summarization
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── indexing.py       # Document indexing and retrieval
│   └── config.py             # Configuration management
├── data/
│   ├── ai_test_bug_report/   # Bug report documents
│   └── ai_test_user_feedback/ # User feedback documents
├── tests/
├── Dockerfile                 # Container configuration
├── docker-compose.dev.yaml   # Development environment setup
├── pyproject.toml            # Project dependencies
├── .env.example              # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose (optional)
- OpenAI API Key
- Qdrant instance (local or cloud)

### Installation

#### Local Development

1. Clone the repository:
```bash
git clone https://github.com/KJ-AIML/ai_test.git
cd ai_test
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration:
```env
OPENAI_API_KEY=your_api_key_here
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

#### Start with Docker Compose (recommended)
Use the provided docker-compose.dev.yaml to bootstrap services (API, and any linked services you configure such as qdrant/redis if included):

```bash
docker compose -f docker-compose.dev.yaml up --build
```

#### Docker Deployment

```bash
docker-compose -f docker-compose.dev.yaml up
```

The API will be available at `http://localhost:3000`

## 📡 API Endpoints

### Query Agent
```
POST /api/v1/internal_agent/query
```
**Request:**
```json
{
  "query": "What are the issues reported on email notification?"
}
```

**Response:**
```json
{
  "query": "What did users say about the search bar?",
  "tools_used": [
    "search_internal_qa_tool"
  ],
  "tool_executions": [
    {
      "step": 1,
      "tool_call": {
        "tool_name": "search_internal_qa_tool",
        "arguments": {
          "query": "search bar"
        }
      },
      "tool_result": {
        "tool_name": "search_internal_qa_tool",
        "tool_type": "internal_qna",
        "answer": "Found search-related feedback",
        "hits": [
          {
            "text": "Feedback #48: ...",
            "score": 0.89
          }
        ]
      }
    }
  ],
  "final_answer": "**Summary:**\nFound 2 issues...\n\n**References:**\n- Feedback #48: ...",
  "metadata": {
    "total_tokens": 1500
  }
}
```

## 🔧 Configuration

Environment variables are managed through `.env` file. Key configurations:

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVER_PORT` | API server port | 3000 |
| `SERVER_HOST` | API server host | 0.0.0.0 |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `QDRANT_URL` | Qdrant vector database URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |
| `VECTOR_STORE_COLLECTION_NAME` | Qdrant collection name | test |
| `RETRIEVAL_TOP_K` | Number of documents to retrieve | 5 |
| `SIMILARITY_THRESHOLD` | Similarity threshold for retrieval | 0.7 |
| `LOG_LEVEL` | Logging level | info |

## 📚 Technology Stack

- **Framework**: FastAPI
- **LLM Integration**: LangChain, LangGraph, OpenAI
- **Vector Store**: Qdrant
- **Embeddings**: OpenAI Text Embedding 3 Small
- **Caching**: Redis
- **Configuration**: Pydantic Settings
- **Server**: Uvicorn
- **Container**: Docker

## 📖 Usage Examples

### Example 1: Query Internal Documents
```bash
curl -X POST "http://localhost:3000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did users say about the search bar?"
  }'
```

## 📦 Development

### Adding New Tools

1. Create a new tool file in `src/agents/tools/tools.py`
2. Implement the tool with structured output
3. Register the tool in the agent
4. Update documentation

Example tool structure:
```python
from typing import Any, Dict

class MyTool:
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given input.
        
        Args:
            input_data: Input parameters
            
        Returns:
            Structured output as dictionary
        """
        # Implementation
        return {"result": "..."}
```

## 🚢 Deployment

### Production Deployment

1. Build Docker image:
```bash
docker build -t ai-test:latest .
```

2. Push to registry:
```bash
docker push your-registry/ai-test:latest
```

### Environment Variables for Production

Update `.env` with production values:
- Use secure OpenAI and Qdrant credentials
- Set `DEBUG=False`
- Configure appropriate `LOG_LEVEL`
- Set up Redis for caching

## 📝 Logging

Logs are stored in `logs/app.log`. Configure logging in `.env`:
```env
LOG_LEVEL=info
LOG_SAVE_TO_FILE=true
LOG_FILE=logs/app.log
```

## 📄 License

This is an internal project for job evaluation purposes.

## 🆘 Troubleshooting

### Vector Store Connection Issues
- Verify Qdrant URL and API key in `.env`
- Ensure Qdrant service is running
- Check network connectivity

### OpenAI API Errors
- Verify API key is correct and has sufficient quota
- Check rate limiting
- Review API usage at https://platform.openai.com/usage
