import os
import json
import httpx
from typing import List, Dict
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyA_J-pRD_8vJhrA7llb6DYC589H3hH6XHs")
GOOGLE_CX = os.getenv("GOOGLE_CX", "45633632255954aae")

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None
    print("Warning: OPENAI_API_KEY not found. AI features will be limited.")

async def web_search(query: str, k: int = 5) -> List[Dict[str, str]]:
    """Perform a Google Custom Search for legal case law"""
    search_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": min(k, 10)  # Google API max is 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
    except Exception as e:
        return [{"title": f"Search Error: {str(e)}", "url": "", "snippet": ""}]

def get_web_search_function_schema():
    """Get the function schema for web search tool calling"""
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a Google Custom Search for legal case law",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for legal cases and precedents"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of search results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }

async def stream_o3_completion(messages, tools, session_events):
    """Stream O3 reasoning model with thinking tokens and function calling"""
    if not openai_client:
        # Return fallback response when OpenAI is not available
        await session_events.put({
            "type": "error",
            "data": "OpenAI API key not configured. Please provide your OpenAI API key to enable AI document generation."
        })
        return {
            "content": "Error: OpenAI API key required for document generation.",
            "tool_calls": []
        }
    
    try:
        # Try o3 model first
        response = openai_client.chat.completions.create(
            model="o3",
            stream=True,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4000,
            temperature=0.3
        )
    except Exception as e:
        # Fallback to gpt-4o if o3 not available
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                stream=True,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4000,
                temperature=0.3
            )
        except Exception as fallback_e:
            await session_events.put({
                "type": "error", 
                "data": f"OpenAI API error: {str(fallback_e)}"
            })
            return {
                "content": f"Error: Unable to connect to OpenAI API - {str(fallback_e)}",
                "tool_calls": []
            }
    
    full_content = ""
    tool_calls = []
    
    for chunk in response:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            
            # Stream thinking tokens
            if delta.content:
                session_events.append({
                    "type": "thinking",
                    "data": delta.content
                })
                full_content += delta.content
            
            # Collect tool calls
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                tool_calls.extend(delta.tool_calls)
            
            # Check for completion
            if chunk.choices[0].finish_reason:
                break
    
    return full_content, tool_calls