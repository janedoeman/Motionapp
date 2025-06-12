# FSA Deep-Research Builder with O3 Reasoning

A specialized legal document generation web application for federal defenders to automate First Step Act compassionate release motions using OpenAI's O3 reasoning model with live AI thinking display.

## Features

- **O3 Reasoning Model**: Uses OpenAI's advanced reasoning model with streaming capabilities
- **Live AI Thinking**: Real-time display of the AI's intermediate thought process
- **Google Custom Search Integration**: Live legal research with case law and precedents
- **Professional Document Generation**: Motion, Memorandum, and Declaration with proper legal formatting
- **Server-Sent Events**: Real-time progress streaming and thinking display

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: React 18, Tailwind CSS
- **AI Model**: OpenAI O3 (with gpt-4o fallback)
- **Search**: Google Custom Search JSON API
- **Document Generation**: ReportLab PDF creation

## API Endpoints

### POST /api/generate
Upload three PDF exhibits to start generation process.

### GET /api/events/{session_id}
Server-Sent Events endpoint providing live updates:
- `thinking`: O3 reasoning tokens streamed in real-time
- `search`: Google Custom Search results
- `done`: Completion with download links
- `error`: Error messages

### GET /download/{session_id}/{filename}
Download generated documents.

## O3 Integration Details

The application uses OpenAI's O3 reasoning model with these key features:

1. **Streaming Enabled**: `stream=True` in chat completions
2. **Function Calling**: Web search tool for live legal research
3. **Thinking Tokens**: Real-time display of AI reasoning process
4. **Fallback Strategy**: Graceful fallback to gpt-4o if O3 unavailable

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for O3 model access
- `GOOGLE_API_KEY`: Google Custom Search API key
- `GOOGLE_CX`: Google Custom Search engine ID

## Usage

1. Upload three PDF exhibits (Sentencing Info, Medical Records, Release Plan)
2. Watch live O3 reasoning process in the thinking panel
3. Monitor real-time legal research queries and results
4. Download generated Motion, Memorandum, and Declaration PDFs

## Model Configuration

```python
response = openai_client.chat.completions.create(
    model="o3",
    stream=True,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    max_tokens=4000,
    temperature=0.3
)
```

## Live Thinking Display

The frontend subscribes to SSE events and displays O3 reasoning tokens in real-time:

```javascript
eventSourceRef.current.addEventListener('thinking', (event) => {
    const content = JSON.parse(event.data);
    setThinkingContent(prev => prev + content);
});
```