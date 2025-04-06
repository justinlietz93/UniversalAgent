# Universal Agent Use Case Integration Guide

This document provides specific guidance for implementing Universal Agent in common use cases like coding assistants, chatbots, and customer service applications.

## Coding Assistant / Copilot Integration

To create a coding assistant similar to GitHub Copilot:

### IDE Extension Integration

```javascript
// Example VS Code extension integration
const vscode = require('vscode');
const axios = require('axios');

// Assume you're running the Universal Agent as a local service
const AGENT_API_URL = 'http://localhost:8000/api/code';

// Register a completion provider for JavaScript files
vscode.languages.registerCompletionItemProvider('javascript', {
    async provideCompletionItems(document, position) {
        // Get current file contents and cursor position
        const text = document.getText();
        const cursorPosition = document.offsetAt(position);
        
        try {
            // Send context to your Universal Agent
            const response = await axios.post(AGENT_API_URL, {
                code: text,
                language: 'javascript',
                position: cursorPosition,
                // Include open files for additional context
                openFiles: vscode.workspace.textDocuments.map(doc => ({
                    filename: doc.fileName,
                    content: doc.getText()
                })).slice(0, 5) // Limit to 5 files
            });
            
            // Create completion items from the response
            const suggestions = response.data.suggestions || [];
            return suggestions.map(suggestion => {
                const item = new vscode.CompletionItem(suggestion.label);
                item.insertText = suggestion.code;
                item.detail = 'AI suggestion';
                item.documentation = suggestion.explanation;
                return item;
            });
        } catch (error) {
            console.error('Error getting code suggestions:', error);
            return [];
        }
    }
});
```

### Agent Backend for Coding Assistant

```python
# Universal Agent service for code completion
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from universal_agent import UniversalAgent
from universal_agent.tools.base_tool import BaseTool

app = FastAPI()

# Initialize the agent with a coding-focused model
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"},
    config={
        "model": "gpt-4",  # Using a model with strong coding capabilities
        "temperature": 0.2,  # Lower temperature for more precise code
        "system_prompt": """You are an expert programming assistant. 
        Provide concise, working code suggestions that match the style and
        context of the surrounding code. Focus on producing correct, 
        efficient, and idiomatic code."""
    }
)

# Custom tool for code analysis
class CodeAnalysisTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._name = "code_analyzer"
        self._description = "Analyze code structure and suggest improvements"
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to analyze"
                },
                "language": {
                    "type": "string",
                    "description": "The programming language"
                }
            },
            "required": ["code", "language"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "structure": {
                    "type": "object",
                    "description": "Analysis of code structure"
                },
                "suggestions": {
                    "type": "array",
                    "description": "Improvement suggestions"
                }
            }
        }
    
    async def run(self, **kwargs):
        # Simplified implementation
        code = kwargs.get("code", "")
        language = kwargs.get("language", "")
        
        # Real implementation would do actual code analysis
        # This is a placeholder
        return {
            "structure": {
                "imports": len(code.split("import ")),
                "functions": len(code.split("function ")),
                "classes": len(code.split("class "))
            },
            "suggestions": [
                "Consider error handling for edge cases",
                "Add type annotations for better IDE support",
                "Break down large functions into smaller ones"
            ]
        }

# Register the tool
agent.register_tool("code_analyzer", CodeAnalysisTool())

class CodeCompletionRequest(BaseModel):
    code: str
    language: str
    position: int
    openFiles: Optional[List[Dict[str, str]]] = None

class CompletionSuggestion(BaseModel):
    label: str
    code: str
    explanation: Optional[str] = None

class CodeCompletionResponse(BaseModel):
    suggestions: List[CompletionSuggestion]

@app.post("/api/code", response_model=CodeCompletionResponse)
async def generate_code_completion(request: CodeCompletionRequest):
    try:
        # Format the prompt with context
        prompt = f"""
        I'm writing code in {request.language}. Here's my current file:
        
        ```{request.language}
        {request.code}
        ```
        
        My cursor is at position {request.position}. 
        Please suggest code completions for this position.
        """
        
        # Add context from other open files if available
        if request.openFiles and len(request.openFiles) > 0:
            prompt += "\n\nHere are some related files for context:\n\n"
            for file in request.openFiles:
                filename = file.get("filename", "unknown")
                content = file.get("content", "")
                # Just include filename and first few lines for context
                shortened_content = "\n".join(content.split("\n")[:10])
                prompt += f"File: {filename}\n```\n{shortened_content}\n...\n```\n\n"
        
        # Get response from the agent
        response = await agent.generate_response(prompt, tools=["code_analyzer"])
        
        # Parse response to extract suggestions
        # This is a simplified version - in practice, you'd want more structure
        # from your LLM response
        
        # Basic parsing for demonstration
        suggestions = []
        for line in response.split("\n"):
            if line.strip().startswith("```") or line.strip() == "":
                continue
            # Simple heuristic to detect code snippets
            if ":" in line and len(line) < 100:
                label = line.split(":")[0].strip()
                code = line.split(":", 1)[1].strip()
                suggestions.append(CompletionSuggestion(
                    label=label,
                    code=code,
                    explanation="Suggested completion based on context"
                ))
        
        # If no suggestions were parsed, create one from the whole response
        if not suggestions:
            suggestions.append(CompletionSuggestion(
                label="Completion",
                code=response.strip(),
                explanation="AI suggested completion"
            ))
            
        return CodeCompletionResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Real-time Collaborative Coding

For real-time collaborative coding environments:

```python
# Using WebSockets for real-time code suggestions
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from universal_agent import UniversalAgent

app = FastAPI()
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"},
    config={"model": "gpt-4"}
)

# Map to track active sessions
active_sessions = {}

@app.websocket("/ws/code-collaboration/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Add to active sessions
    if session_id not in active_sessions:
        active_sessions[session_id] = []
    active_sessions[session_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("type") == "code_update":
                # Get contextual code suggestions
                code = payload.get("code", "")
                language = payload.get("language", "")
                cursor_position = payload.get("position", 0)
                
                # Get suggestions from the agent
                prompt = f"Provide code suggestions for this {language} code at position {cursor_position}:\n\n```{language}\n{code}\n```"
                
                # Process code suggestions
                suggestions = await agent.generate_response(prompt)
                
                # Broadcast to all clients in this session
                for client in active_sessions[session_id]:
                    await client.send_json({
                        "type": "code_suggestion",
                        "suggestions": suggestions
                    })
    
    except WebSocketDisconnect:
        # Remove from active sessions
        active_sessions[session_id].remove(websocket)
```

## Custom Chatbot Integration

### Multi-turn Conversation Bot

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from universal_agent import UniversalAgent

app = FastAPI()

# Initialize agent
agent = UniversalAgent(
    provider="anthropic",  # Using Claude for high-quality dialogue
    credentials={"api_key": "your-anthropic-api-key"},
    config={
        "model": "claude-2",
        "temperature": 0.7,
        "system_prompt": """You are a helpful, friendly, and engaging conversational
        assistant. Maintain context throughout the conversation and provide thoughtful,
        natural responses that build rapport with the user. Be concise but comprehensive."""
    }
)

# In-memory conversation store (replace with database in production)
conversations = {}

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ConversationRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, str]] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    conversation_history: List[Message]

@app.post("/api/chat", response_model=ConversationResponse)
async def chat_endpoint(request: ConversationRequest):
    # Create new conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Initialize conversation history if new
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Add user message to history
    conversations[conversation_id].append(Message(
        role="user",
        content=request.message,
        timestamp=datetime.datetime.now().isoformat()
    ))
    
    # Build conversation history for context
    conversation_context = ""
    for msg in conversations[conversation_id][-10:]:  # Last 10 messages
        conversation_context += f"{msg.role.capitalize()}: {msg.content}\n\n"
    
    # Add any additional context
    context_info = ""
    if request.context:
        context_info = "Additional context:\n"
        for key, value in request.context.items():
            context_info += f"- {key}: {value}\n"
    
    # Create prompt with history and context
    prompt = f"{context_info}\n\nConversation history:\n{conversation_context}\nUser: {request.message}\n\nAssistant:"
    
    # Get response from agent
    response = await agent.generate_response(prompt)
    
    # Add assistant message to history
    conversations[conversation_id].append(Message(
        role="assistant",
        content=response,
        timestamp=datetime.datetime.now().isoformat()
    ))
    
    return ConversationResponse(
        conversation_id=conversation_id,
        response=response,
        conversation_history=conversations[conversation_id]
    )
```

### Platform-specific Bot Integration

#### Slack Integration

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from universal_agent import UniversalAgent
import asyncio

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize Universal Agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": os.environ["OPENAI_API_KEY"]},
    config={
        "model": "gpt-4",
        "system_prompt": "You are a helpful assistant in a Slack workspace. Be concise and friendly."
    }
)

# Store conversation history
conversation_history = {}

@app.event("message")
def handle_message_events(body, logger):
    # Extract message information
    event = body["event"]
    channel_id = event["channel"]
    user_id = event["user"]
    text = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])
    
    # Skip messages from the bot itself
    if user_id == app.client.auth_test()["user_id"]:
        return
    
    # Initialize conversation history for thread if not exists
    if thread_ts not in conversation_history:
        conversation_history[thread_ts] = []
    
    # Add message to history
    conversation_history[thread_ts].append({
        "role": "user",
        "content": text,
    })
    
    # Format conversation history for context
    conversation_text = ""
    for message in conversation_history[thread_ts][-5:]:  # Last 5 messages
        conversation_text += f"{message['role'].capitalize()}: {message['content']}\n"
    
    # Create prompt with conversation history
    prompt = f"Slack conversation:\n{conversation_text}\n\nAssistant:"
    
    # Get response from agent
    loop = asyncio.new_event_loop()
    response = loop.run_until_complete(agent.generate_response(prompt))
    loop.close()
    
    # Add response to history
    conversation_history[thread_ts].append({
        "role": "assistant",
        "content": response,
    })
    
    # Send response to Slack
    app.client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text=response
    )

# Start the app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

#### Discord Bot Integration

```python
import discord
from discord.ext import commands
import os
import asyncio
from universal_agent import UniversalAgent

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Universal Agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": os.environ["OPENAI_API_KEY"]},
    config={
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful Discord bot. Be concise, friendly, and engaging."
    }
)

# Store conversation history by channel
conversation_history = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Skip messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)
    
    # Only respond to mentions or DMs
    if not (bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
        return
    
    channel_id = str(message.channel.id)
    
    # Initialize conversation history for channel if not exists
    if channel_id not in conversation_history:
        conversation_history[channel_id] = []
    
    # Add message to history
    conversation_history[channel_id].append({
        "role": "user",
        "name": message.author.display_name,
        "content": message.content,
    })
    
    # Format conversation history for context
    conversation_text = ""
    for msg in conversation_history[channel_id][-5:]:  # Last 5 messages
        conversation_text += f"{msg['name']} ({msg['role']}): {msg['content']}\n"
    
    # Remove bot mention from the prompt
    prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
    
    # Create prompt with conversation history
    full_prompt = f"Discord conversation:\n{conversation_text}\n\nRespond to: {prompt}\n\nAssistant:"
    
    # Show typing indicator
    async with message.channel.typing():
        # Get response from agent
        response = await agent.generate_response(full_prompt)
    
    # Add response to history
    conversation_history[channel_id].append({
        "role": "assistant",
        "name": bot.user.display_name,
        "content": response,
    })
    
    # Send response to Discord
    await message.reply(response)

# Run the bot
bot.run(os.environ["DISCORD_TOKEN"])
```

## Customer Service Agent

### Ticket System Integration

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import aiohttp
import json
import os
from universal_agent import UniversalAgent
from universal_agent.tools.base_tool import BaseTool

app = FastAPI()

# Initialize Universal Agent for customer service
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": os.environ["OPENAI_API_KEY"]},
    config={
        "model": "gpt-4",
        "temperature": 0.3,
        "system_prompt": """You are a professional customer service assistant. 
        Help customers by providing accurate, helpful information. Be empathetic 
        and solution-oriented. When you don't know something, use available 
        tools to find information rather than making up answers."""
    }
)

# Zendesk API integration tool
class ZendeskTool(BaseTool):
    def __init__(self, subdomain, api_token):
        super().__init__()
        self._name = "zendesk"
        self._description = "Interact with Zendesk for ticket management"
        self.subdomain = subdomain
        self.api_token = api_token
        self.api_url = f"https://{subdomain}.zendesk.com/api/v2"
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform (get_ticket, search_tickets, update_ticket)",
                    "enum": ["get_ticket", "search_tickets", "update_ticket"]
                },
                "ticket_id": {
                    "type": "integer",
                    "description": "Ticket ID for get_ticket and update_ticket actions"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for search_tickets action"
                },
                "update_data": {
                    "type": "object",
                    "description": "Data for updating a ticket"
                }
            },
            "required": ["action"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean"
                },
                "data": {
                    "type": "object"
                },
                "error": {
                    "type": "string"
                }
            }
        }
    
    async def run(self, **kwargs):
        action = kwargs.get("action")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            if action == "get_ticket":
                ticket_id = kwargs.get("ticket_id")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.api_url}/tickets/{ticket_id}.json",
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            return {"success": False, "error": f"API error: {response.status}"}
                        
                        data = await response.json()
                        return {"success": True, "data": data}
            
            elif action == "search_tickets":
                query = kwargs.get("query")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.api_url}/search.json",
                        params={"query": f"type:ticket {query}"},
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            return {"success": False, "error": f"API error: {response.status}"}
                        
                        data = await response.json()
                        return {"success": True, "data": data}
            
            elif action == "update_ticket":
                ticket_id = kwargs.get("ticket_id")
                update_data = kwargs.get("update_data", {})
                
                async with aiohttp.ClientSession() as session:
                    async with session.put(
                        f"{self.api_url}/tickets/{ticket_id}.json",
                        headers=headers,
                        json={"ticket": update_data}
                    ) as response:
                        if response.status not in [200, 201]:
                            return {"success": False, "error": f"API error: {response.status}"}
                        
                        data = await response.json()
                        return {"success": True, "data": data}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# Knowledge base tool
class KnowledgeBaseTool(BaseTool):
    def __init__(self, kb_url, api_key):
        super().__init__()
        self._name = "knowledge_base"
        self._description = "Search the company knowledge base for information"
        self.kb_url = kb_url
        self.api_key = api_key
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "articles": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        }
    
    async def run(self, **kwargs):
        query = kwargs.get("query")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.kb_url}/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                if response.status != 200:
                    return {"articles": [], "error": f"API error: {response.status}"}
                
                data = await response.json()
                return {"articles": data.get("results", [])}

# Register tools
agent.register_tool(
    "zendesk",
    ZendeskTool(
        subdomain=os.environ["ZENDESK_SUBDOMAIN"],
        api_token=os.environ["ZENDESK_API_TOKEN"]
    )
)

agent.register_tool(
    "knowledge_base",
    KnowledgeBaseTool(
        kb_url=os.environ["KNOWLEDGE_BASE_URL"],
        api_key=os.environ["KNOWLEDGE_BASE_API_KEY"]
    )
)

class TicketRequest(BaseModel):
    ticket_id: int
    query: str
    customer_info: Optional[Dict[str, str]] = None

class TicketResponse(BaseModel):
    response: str
    suggested_actions: List[str]
    knowledge_articles: List[Dict[str, str]]

@app.post("/api/ticket-assistant", response_model=TicketResponse)
async def ticket_assistant(request: TicketRequest, background_tasks: BackgroundTasks):
    try:
        # Get ticket information using the Zendesk tool
        ticket_info = await agent.execute_tool(
            "zendesk",
            action="get_ticket",
            ticket_id=request.ticket_id
        )
        
        if not ticket_info.get("success"):
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket_data = ticket_info["data"]["ticket"]
        
        # Format customer information
        customer_info = ""
        if request.customer_info:
            customer_info = "Customer information:\n"
            for key, value in request.customer_info.items():
                customer_info += f"- {key}: {value}\n"
        
        # Create prompt with ticket information
        prompt = f"""
        I need help with a customer support ticket:
        
        Ticket #{ticket_data['id']}: {ticket_data['subject']}
        Status: {ticket_data['status']}
        Priority: {ticket_data['priority']}
        
        {customer_info}
        
        Ticket description:
        {ticket_data['description']}
        
        Customer query:
        {request.query}
        
        Please help me respond to this customer, search the knowledge base if needed, and suggest actions.
        """
        
        # Get response from agent with tool access
        response = await agent.generate_response(
            prompt,
            tools=["zendesk", "knowledge_base"]
        )
        
        # Search knowledge base for relevant articles
        kb_results = await agent.execute_tool(
            "knowledge_base",
            query=request.query
        )
        
        # Extract suggested actions (simplified implementation)
        suggested_actions = []
        for line in response.split("\n"):
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                suggested_actions.append(line.strip()[2:])
        
        # In the background, update the ticket with the AI response
        background_tasks.add_task(
            agent.execute_tool,
            "zendesk",
            action="update_ticket",
            ticket_id=request.ticket_id,
            update_data={
                "comment": {
                    "body": f"AI Assistant suggested response:\n\n{response}",
                    "public": False
                }
            }
        )
        
        return TicketResponse(
            response=response,
            suggested_actions=suggested_actions[:5],  # Limit to 5 actions
            knowledge_articles=[
                {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "excerpt": article.get("excerpt", "")
                }
                for article in kb_results.get("articles", [])[:3]  # Limit to 3 articles
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Customer Support Portal

```python
# React front-end for customer support with Universal Agent
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Simplified React component for customer support chat
function CustomerSupportChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initial greeting from support agent
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I'm your customer support assistant. How can I help you today?'
      }
    ]);
  }, []);

  // Handle sending message
  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsTyping(true);
    
    try {
      // Call your Universal Agent API
      const response = await axios.post('/api/customer-support', {
        message: input,
        conversation_id: conversationId
      });
      
      // Save conversation ID for context
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }
      
      // Add response to chat
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response
      }]);
      
      // If there are KB articles, display them
      if (response.data.knowledge_articles && response.data.knowledge_articles.length > 0) {
        setMessages(prev => [...prev, { 
          role: 'system', 
          content: 'I found these helpful resources:',
          articles: response.data.knowledge_articles
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'Sorry, there was an error. Please try again later.'
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Customer Support</h2>
      </div>
      
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
            
            {/* Render KB articles if present */}
            {message.articles && (
              <div className="kb-articles">
                {message.articles.map((article, idx) => (
                  <div key={idx} className="kb-article">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                    <p>{article.excerpt}</p>
                  </div>
                ))}
