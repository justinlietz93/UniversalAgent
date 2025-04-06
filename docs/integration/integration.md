# Universal Agent Integration Guide

This document explains how to integrate Universal Agent with existing systems and frameworks.

## API Integration Options

Universal Agent provides multiple integration points for existing systems:

### 1. Python Library Integration

The most direct way to integrate is through the Python library:

```python
from universal_agent import UniversalAgent

# Initialize the agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

# Use the agent in your application
async def get_ai_response(user_query):
    response = await agent.generate_response(user_query)
    return response
```

### 2. Web Framework Integration

#### Flask Integration

```python
from flask import Flask, request, jsonify
from universal_agent import UniversalAgent
import asyncio

app = Flask(__name__)

# Initialize the agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message', '')
    
    # Run async agent in sync context
    loop = asyncio.new_event_loop()
    response = loop.run_until_complete(agent.generate_response(user_message))
    loop.close()
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
```

#### FastAPI Integration (Recommended for Async)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from universal_agent import UniversalAgent

app = FastAPI()

# Initialize the agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await agent.generate_response(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Streaming API Integration

For applications that need to handle streaming responses:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from universal_agent import UniversalAgent

app = FastAPI()
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

class ChatRequest(BaseModel):
    message: str

async def stream_generator(message):
    async for chunk in agent.generate_streaming_response(message):
        yield f"data: {chunk}\n\n"

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    return StreamingResponse(
        stream_generator(request.message),
        media_type="text/event-stream"
    )
```

### 4. Microservice Architecture

Universal Agent can be deployed as a dedicated microservice:

```python
# agent_service.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from universal_agent import UniversalAgent
import uuid
import json
from typing import Dict, List, Optional

app = FastAPI()

# Initialize the agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

# Store for ongoing conversations
conversations = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    tools: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Create or get conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        response = await agent.generate_response(
            request.message,
            tools=request.tools
        )
        
        # Store conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": request.message
        })
        
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response
        })
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Webhook Integration

Universal Agent can be configured to call webhooks when tools are invoked or when responses are generated:

```python
from universal_agent import UniversalAgent
import aiohttp

async def tool_webhook(tool_name, tool_input, tool_output):
    """Send tool usage to webhook"""
    async with aiohttp.ClientSession() as session:
        await session.post(
            "https://your-webhook-url.com/tools",
            json={
                "tool": tool_name,
                "input": tool_input,
                "output": tool_output
            }
        )

# Initialize with webhook
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"},
    config={
        "tool_callback": tool_webhook
    }
)
```

## Custom Tool Integrations

You can integrate existing systems by creating custom tools that interface with those systems:

```python
from universal_agent import UniversalAgent
from universal_agent.tools.base_tool import BaseTool
import aiohttp

class DatabaseSearchTool(BaseTool):
    def __init__(self, db_url, api_key):
        super().__init__()
        self._name = "database_search"
        self._description = "Search the company database for information"
        self.db_url = db_url
        self.api_key = api_key
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    },
                    "description": "The search results"
                }
            }
        }
    
    async def run(self, **kwargs):
        query = kwargs.get("query")
        
        # Connect to existing database API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.db_url}/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                if response.status != 200:
                    return {"error": f"Database API error: {response.status}"}
                
                data = await response.json()
                
        return {"results": data.get("items", [])}

# Register the tool with your agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

# Connect to your existing database
db_tool = DatabaseSearchTool(
    db_url="https://your-database-api.com",
    api_key="your-db-api-key"
)

agent.register_tool("database_search", db_tool)
```

## Docker Deployment

Universal Agent can be containerized for easy deployment in various environments:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example docker-compose.yml for deployment with Redis for caching:

```yaml
version: '3'

services:
  agent-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: always

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: always

volumes:
  redis-data:
```

## Message Queue Integration

For scaling and asynchronous processing, you can integrate with message queues:

```python
# Example using Celery
from celery import Celery
from universal_agent import UniversalAgent

# Create Celery app
celery_app = Celery('agent_tasks', broker='redis://localhost:6379/0')

# Task to generate responses asynchronously
@celery_app.task
async def generate_response_task(message, callback_url):
    agent = UniversalAgent(
        provider="openai",
        credentials={"api_key": "your-api-key"}
    )
    
    response = await agent.generate_response(message)
    
    # Send result to callback URL
    async with aiohttp.ClientSession() as session:
        await session.post(
            callback_url,
            json={"response": response}
        )
    
    return response
```

## OAuth Integration

For applications that need to use user-specific credentials:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from universal_agent import UniversalAgent

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_agent_for_user(token: str = Depends(oauth2_scheme)):
    # Validate token and get user
    user = get_user_from_token(token)  # Your authentication logic
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # Get user-specific API keys
    api_key = get_user_api_key(user.id)  # Your API key retrieval logic
    
    # Create agent with user's credentials
    agent = UniversalAgent(
        provider="openai",
        credentials={"api_key": api_key}
    )
    
    return agent

@app.post("/api/chat")
async def chat(message: str, agent: UniversalAgent = Depends(get_agent_for_user)):
    response = await agent.generate_response(message)
    return {"response": response}
```

## Server-Sent Events (SSE) for Streaming

For web applications that need to display streaming responses:

```javascript
// Client-side JavaScript
const eventSource = new EventSource('/api/chat/stream?message=Tell me a story');

eventSource.onmessage = (event) => {
  const chunk = event.data;
  // Append chunk to UI
  document.getElementById('response').innerHTML += chunk;
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

## WebSocket Integration

For real-time, bidirectional communication:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from universal_agent import UniversalAgent

app = FastAPI()
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            
            # For streaming responses
            async for chunk in agent.generate_streaming_response(message):
                await websocket.send_text(chunk)
            
            # Or for regular responses
            # response = await agent.generate_response(message)
            # await websocket.send_text(response)
            
    except WebSocketDisconnect:
        print("Client disconnected")
```

## GraphQL API

For applications that use GraphQL:

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

@strawberry.type
class Query:
    @strawberry.field
    async def chat(self, message: str) -> str:
        return await agent.generate_response(message)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

## Conclusion

Universal Agent provides flexible integration options that can adapt to various system architectures and requirements. Whether you need simple library usage, REST API deployment, streaming functionality, or complex microservice integration, the agent can be configured to meet your needs.

For specific integration scenarios not covered here, consult the API reference or create custom integration tools using the BaseTool class.
