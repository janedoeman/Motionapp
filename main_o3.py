import os
import re
import json
import uuid
import zipfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from openai import OpenAI
import httpx
import uvicorn

app = FastAPI(title="FSA Deep-Research Builder with O3")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyA_J-pRD_8vJhrA7llb6DYC589H3hH6XHs")
GOOGLE_CX = os.getenv("GOOGLE_CX", "45633632255954aae")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# File storage
temp_dir = Path("/tmp/fsa_motion_builder")
temp_dir.mkdir(exist_ok=True)

# Global session storage for SSE
active_sessions: Dict[str, Dict] = {}

class DefendantInfo:
    """Data class for defendant information"""
    def __init__(self):
        self.name = "UNKNOWN"
        self.case_number = "UNKNOWN"
        self.district = "UNKNOWN"
        self.sentence_months = "UNKNOWN"
        self.months_served = "UNKNOWN"
        self.credits_lost = "UNKNOWN"
        self.original_release_date = "UNKNOWN"
        self.new_release_date = "UNKNOWN"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def parse_defendant_info(text: str) -> DefendantInfo:
    """Parse defendant information from Exhibit A text"""
    info = DefendantInfo()
    
    patterns = {
        'name': [
            r'(?:defendant|respondent)[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:United States v\.)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:USA v\.)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ],
        'case_number': [
            r'(?:case\s+(?:no|number)[\.\:]?\s*)([0-9]{1,2}:[0-9]{2}[-cr]+[0-9]+)',
            r'([0-9]{1,2}:[0-9]{2}[-cr]+[0-9]+)'
        ],
        'district': [
            r'(?:(?:United States )?District Court for the\s+)([^,\n]+)',
            r'(?:District of\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
    }
    
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                setattr(info, field, match.group(1).strip())
                break
    
    return info

async def web_search(query: str, k: int = 5) -> List[Dict[str, str]]:
    """Perform web search using Google Custom Search JSON API"""
    search_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": k
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
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
    except Exception as e:
        return [{"title": f"Search Error: {str(e)}", "link": "", "snippet": ""}]

async def generate_with_o3_research(defendant_info: DefendantInfo, session_id: str):
    """Generate legal documents with live research using O3 reasoning model and streaming"""
    
    if session_id not in active_sessions:
        active_sessions[session_id] = {"events": [], "status": "active"}
    
    session = active_sessions[session_id]
    
    # Define function calling tools for web search
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for legal cases, precedents, and current information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    # System prompt for comprehensive legal analysis
    system_prompt = f"""You are an expert federal defense attorney specializing in First Step Act compassionate release motions. You have access to web search to find current case law and precedents.

    Defendant Information:
    - Name: {defendant_info.name}
    - Case: {defendant_info.case_number}
    - District: {defendant_info.district}
    - Sentence: {defendant_info.sentence_months} months
    - Served: {defendant_info.months_served} months

    Your task is to:
    1. Research current legal precedents and case law relevant to this defendant's situation
    2. Search for recent First Step Act decisions in the {defendant_info.district}
    3. Generate comprehensive legal documents incorporating your research

    Generate three documents with these exact delimiters:

    ===MOTION START===
    [Complete Motion for Compassionate Release]
    ===MOTION END===

    ===MEMO START===
    [Complete Memorandum of Law with case citations]
    ===MEMO END===

    ===DECL START===
    [Complete Declaration with factual support]
    ===DECL END===

    Use web search extensively to find relevant cases, statistics, and current legal developments."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please research and generate a comprehensive FSA motion packet for {defendant_info.name}."}
    ]
    
    try:
        # Use o3 reasoning model with streaming
        while True:
            response = openai_client.chat.completions.create(
                model="o3",
                stream=True,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4000,
                temperature=0.3
            )
            
            # Collect streaming response and forward thinking tokens
            full_content = ""
            tool_calls = []
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    
                    if delta.content:
                        # Forward thinking tokens to client via SSE
                        thinking_event = {
                            "type": "thinking", 
                            "payload": {
                                "content": delta.content
                            }
                        }
                        session["events"].append(thinking_event)
                        full_content += delta.content
                    
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tc in delta.tool_calls:
                            tool_calls.append(tc)
                    
                    if chunk.choices[0].finish_reason:
                        break
            
            # Add assistant message to conversation
            assistant_msg = {"role": "assistant"}
            if full_content:
                assistant_msg["content"] = full_content
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            messages.append(assistant_msg)
            
            # Handle tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    if hasattr(tool_call, 'function') and tool_call.function.name == "web_search":
                        function_args = json.loads(tool_call.function.arguments)
                        query = function_args["query"]
                        k = function_args.get("k", 5)
                        
                        # Perform actual web search
                        search_results = await web_search(query, k)
                        
                        # Add search event to session
                        search_event = {
                            "type": "search",
                            "payload": {
                                "query": query,
                                "results": search_results
                            }
                        }
                        session["events"].append(search_event)
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(search_results)
                        })
                continue
            
            # Check if we have final documents
            if full_content and "===MOTION START===" in full_content and "===DECL END===" in full_content:
                break
            
            # Prevent infinite loops
            if len(messages) > 25:
                break
    
    except Exception as e:
        error_event = {
            "type": "error",
            "payload": f"Error during O3 reasoning and generation: {str(e)}"
        }
        session["events"].append(error_event)
        return
    
    # Parse final documents from the last assistant message
    final_content = ""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            final_content = msg["content"]
            break
    
    motion_match = re.search(r'===MOTION START===(.*?)===MOTION END===', final_content, re.DOTALL)
    memo_match = re.search(r'===MEMO START===(.*?)===MEMO END===', final_content, re.DOTALL)
    decl_match = re.search(r'===DECL START===(.*?)===DECL END===', final_content, re.DOTALL)
    
    documents = {
        'motion': motion_match.group(1).strip() if motion_match else "Motion could not be generated with O3 reasoning",
        'memo': memo_match.group(1).strip() if memo_match else "Memo could not be generated with O3 reasoning", 
        'declaration': decl_match.group(1).strip() if decl_match else "Declaration could not be generated with O3 reasoning"
    }
    
    # Create PDFs
    session_dir = temp_dir / session_id
    session_dir.mkdir(exist_ok=True)
    
    pdf_paths = {}
    for doc_type, content in documents.items():
        filename = f"{doc_type.title()}.pdf"
        pdf_path = create_pdf_document(content, session_dir / filename)
        pdf_paths[filename] = pdf_path
    
    # Create ZIP package
    zip_path = create_zip_package(pdf_paths, session_dir)
    
    # Add completion event
    completion_event = {
        "type": "done",
        "payload": {
            "motion_url": f"/download/{session_id}/Motion.pdf",
            "memo_url": f"/download/{session_id}/Memo.pdf", 
            "decl_url": f"/download/{session_id}/Declaration.pdf",
            "zip_url": f"/download/{session_id}/motion_packet.zip"
        }
    }
    session["events"].append(completion_event)
    session["status"] = "completed"

def create_pdf_document(content: str, file_path: Path) -> str:
    """Create PDF document using ReportLab"""
    doc = SimpleDocTemplate(str(file_path), pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), styles['Normal']))
            story.append(Spacer(1, 12))
    
    doc.build(story)
    return str(file_path)

def create_zip_package(pdf_paths: Dict[str, str], session_dir: Path) -> str:
    """Create ZIP package containing all PDFs"""
    zip_path = session_dir / "motion_packet.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename, file_path in pdf_paths.items():
            zipf.write(file_path, filename)
    
    return str(zip_path)

@app.post("/api/generate")
async def generate_motion_packet(
    exhibit_a: UploadFile = File(...),
    exhibit_b: UploadFile = File(...),
    exhibit_c: UploadFile = File(...)
):
    """Generate FSA motion packet with O3 reasoning and live research"""
    session_id = str(uuid.uuid4())
    
    # Save uploaded files
    session_dir = temp_dir / session_id
    session_dir.mkdir(exist_ok=True)
    
    exhibit_a_path = session_dir / "exhibit_a.pdf"
    with open(exhibit_a_path, "wb") as f:
        f.write(await exhibit_a.read())
    
    # Extract defendant information
    exhibit_a_text = extract_text_from_pdf(str(exhibit_a_path))
    defendant_info = parse_defendant_info(exhibit_a_text)
    
    # Start background generation task
    asyncio.create_task(generate_with_o3_research(defendant_info, session_id))
    
    return {"session_id": session_id}

@app.get("/api/events/{session_id}")
async def stream_events(session_id: str):
    """Server-Sent Events endpoint for live progress with O3 thinking"""
    
    async def event_generator():
        last_event_index = 0
        
        while True:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                events = session["events"]
                
                # Send new events
                for i in range(last_event_index, len(events)):
                    event = events[i]
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["payload"])
                    }
                
                last_event_index = len(events)
                
                # Check if generation is complete
                if session["status"] == "completed":
                    break
            
            await asyncio.sleep(0.5)
    
    return EventSourceResponse(event_generator())

@app.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    """Download generated files"""
    file_path = temp_dir / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model": "o3"}

# Serve static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)