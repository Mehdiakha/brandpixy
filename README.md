# BrandPixy

BrandPixy is an interactive brand identity generator powered by AI (Gemini) and SvelteKit.

## Features
- **Interactive 3-Phase Flow**: Industry, Vibe, Values.
- **AI-Powered Generation**: Uses Google Gemini API to generate unique names and taglines.
- **Visual Identity**: Generates SVG logo concepts based on your brand DNA.
- **Modern UI**: Sleek, responsive design with smooth animations.

## Tech Stack
- **Frontend**: SvelteKit, Vite
- **Backend**: FastAPI, Python
- **AI**: Google Gemini API

## Setup & Run

### Prerequisites
- Node.js & npm
- Python 3.10+
- `uv` package manager (optional, but recommended)

### 1. Backend
Create a `.env` file in the root with your API key:
```
GEMINI_API_KEY="your_api_key_here"
```

Install dependencies and run:
```bash
# Using uv
uv venv .venv
.venv\Scripts\activate
uv add fastapi uvicorn python-dotenv httpx pydantic
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev -- --host
```

Visit `http://localhost:5173` to use the app.
