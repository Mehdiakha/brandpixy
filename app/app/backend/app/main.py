from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import httpx
import random
import html
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY) if API_KEY else None

MOONSHOT_API_KEY = os.getenv('MOONSHOT_AI_API_KEY')
MOONSHOT_BASE_URL = 'https://api.moonshot.cn/v1'

PALETTE = ["#9381ff", "#b8b8ff", "#f8f7ff"]

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="brandpixy API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "BrandPixy API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "gemini_enabled": bool(API_KEY), "moonshot_enabled": bool(MOONSHOT_API_KEY)}


class BrandRequest(BaseModel):
    industry: str
    vibe: str
    values: str


BRAND_PROMPT_TEMPLATE = """
Generate 24 unique, creative brand names and catchy one-line taglines for a brand with:
Industry: {industry}
Vibe: {vibe}
Values: {values}

Return a JSON object with a key "brands" containing an array of objects, each with "name" and "tagline" fields.
Output ONLY valid JSON, no markdown formatting.
"""


def generate_brand_names_moonshot(industry: str, vibe: str, values: str) -> list[dict]:
    """
    Generates brand names and taglines using MoonshotAI as a fallback.
    """
    if not MOONSHOT_API_KEY:
        print("MoonshotAI API key not configured. Skipping.")
        return []

    prompt = BRAND_PROMPT_TEMPLATE.format(industry=industry, vibe=vibe, values=values)

    try:
        print(f"Falling back to MoonshotAI for industry: {industry}")
        with httpx.Client(timeout=30) as http:
            resp = http.post(
                f"{MOONSHOT_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MOONSHOT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": "You are a creative branding expert. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.8,
                },
            )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        # Strip possible markdown fences
        content = content.strip().strip("```json").strip("```").strip()
        data = json.loads(content)
        items = data.get("brands", [])
        if not items and isinstance(data, list):
            items = data
        print(f"MoonshotAI returned {len(items)} items.")
        return items
    except Exception as e:
        print(f"MoonshotAI Generation Error: {e}")
        return []


def generate_brand_names(industry: str, vibe: str, values: str) -> list[dict]:
    """
    Generates creative brand names and taglines.
    Tries Google Gemini first, falls back to MoonshotAI.
    """
    prompt = BRAND_PROMPT_TEMPLATE.format(industry=industry, vibe=vibe, values=values)

    # --- Try Gemini ---
    if client:
        try:
            print(f"Sending request to Gemini for industry: {industry}")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    response_mime_type="application/json",
                ),
            )
            content = response.text
            print("Received response from Gemini")
            data = json.loads(content)
            items = data.get('brands', [])
            if not items and isinstance(data, list):
                items = data
            if items:
                return items
            print("Gemini returned empty list, trying MoonshotAI fallback...")
        except Exception as e:
            print(f"Gemini Text Generation Error: {e}. Trying MoonshotAI fallback...")
    else:
        print("Gemini client not initialized. Trying MoonshotAI fallback...")

    # --- Fallback: MoonshotAI ---
    return generate_brand_names_moonshot(industry, vibe, values)


def generate_logo_image(name: str, vibe: str) -> str:
    """
    Generates a logo image using Gemini's native image generation.
    Returns the image as a base64 data URL.
    """
    if not client:
        return ""

    # Use Gemini's native image generation capability
    prompt = f"Create a professional, high-quality logo design for a brand named '{name}'. Industry vibe: {vibe}. Vector style, flat design, minimal, clean white background, high resolution, no text in the image."
    
    try:
        print(f"Calling Gemini image generation for: {name}")
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        
        # Extract image from response parts
        if response.parts:
            for part in response.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    return f"data:{mime_type};base64,{base64_image}"
        
        print("Gemini returned no image in response")
        return ""
    except Exception as e:
        print(f"Gemini Image Generation Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return ""


def local_generate(request: BrandRequest, count: int = 20):
    industry = (request.industry or '').strip()
    vibe = (request.vibe or '').strip()
    values = (request.values or '').strip()

    parts = [p for p in (industry + ' ' + vibe).split() if p]
    if not parts:
        parts = ['Brand']

    suggestions = []
    for i in range(count):
        # Build a playful name mixing parts and random syllables
        take = random.randint(1, min(3, len(parts)))
        name_parts = [parts[(i + j) % len(parts)] for j in range(take)]
        suffix = random.choice(['ly', 'io', 'ix', 'ster', 'igo', 'ora', 'able', 'o'])
        name = ''.join([p.capitalize() for p in name_parts])
        if random.random() > 0.5:
            name = name + suffix.capitalize()

        if len(name) < 3:
            name = (industry[:3] + vibe[:2]).title() or 'Brandix'

        core_value = (values.split(',')[0].strip() if values else 'purpose')
        tagline = f"{vibe.capitalize() if vibe else 'Distinctive'} {industry or 'brand'} focused on {core_value}"

        svg = generate_svg(name, i)
        suggestions.append({"name": html.escape(name), "tagline": html.escape(tagline), "svg": svg})

    return suggestions


def generate_svg(name: str, idx: int = 0) -> str:
        # Create a slightly varied SVG logo per index using palette and shapes
        initials = ''.join([p[0] for p in name.split() if p])[:3].upper() or name[:2].upper()
        c1, c2, c3 = PALETTE
        # rotate palette by index for variety
        colors = [PALETTE[(idx + i) % len(PALETTE)] for i in range(3)]
        shape = ['circle', 'rect', 'polygon'][idx % 3]
        shape_svg = ''
        if shape == 'circle':
                shape_svg = f'<circle cx="100" cy="100" r="80" fill="{colors[0]}" opacity="0.95" />'
        elif shape == 'rect':
                shape_svg = f'<rect x="20" y="20" width="160" height="160" rx="30" fill="{colors[1]}" opacity="0.95" />'
        else:
                shape_svg = f'<polygon points="100,20 180,180 20,180" fill="{colors[2]}" opacity="0.95" />'

        # Increased viewBox for better resolution and scaling
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 200 200" shape-rendering="geometricPrecision">
    <rect width="100%" height="100%" rx="24" fill="#fff" />
    <g>
        {shape_svg}
        <text x="100" y="100" dominant-baseline="middle" text-anchor="middle" font-family="Inter, Arial, Helvetica, sans-serif" font-size="60" font-weight="bold" fill="#0f1720">{initials}</text>
    </g>
</svg>'''
        return svg


@app.post('/api/generate')
@limiter.limit("5/minute")
async def generate(request: Request, brand_request: BrandRequest):
    print(f"Received generation request: {brand_request}")
    try:
        suggestions = []

        # 1. Generate Brand Names (Gemini first, MoonshotAI fallback, then local)
        print("Attempting AI brand name generation...")
        items = generate_brand_names(brand_request.industry, brand_request.vibe, brand_request.values)
        print(f"AI generation returned {len(items)} items.")

        # 2. Generate Logos (local SVG for speed/bulk)
        for i, item in enumerate(items):
            name = item.get('name')
            tagline = item.get('tagline', '')
            if name:
                svg = generate_svg(name, i)
                suggestions.append({"name": name, "tagline": tagline, "svg": svg})

        # Fill with local generation if AI returned fewer than 20
        if len(suggestions) < 20:
            print(f"Filling remaining {20 - len(suggestions)} slots with local generation.")
            remaining = 20 - len(suggestions)
            suggestions.extend(local_generate(brand_request, count=remaining))

        print(f"Returning {len(suggestions)} suggestions.")
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"CRITICAL ERROR in /api/generate: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/generate-logo')
@limiter.limit("30/minute")
async def generate_logo_endpoint(request: Request, name: str, vibe: str):
    """
    Dedicated endpoint to generate a high-quality logo using Gemini Imagen.
    Frontend can call this on demand (e.g., when user clicks a specific result).
    """
    # Decode HTML entities (e.g., &amp; -> &)
    clean_name = html.unescape(name)
    clean_vibe = html.unescape(vibe)
    print(f"Received logo generation request for: {clean_name}, vibe: {clean_vibe}")
    try:
        url = ""
        if API_KEY:
            url = generate_logo_image(clean_name, clean_vibe)
            if not url:
                print("Gemini returned empty image, falling back to SVG.")
        else:
            print("No Gemini API Key found for logo generation, falling back to SVG.")

        if url:
            print(f"Generated logo successfully for: {clean_name}")
            return {"url": url, "type": "image"}

        # Fallback: return a local SVG logo
        print(f"Using SVG fallback logo for: {clean_name}")
        svg = generate_svg(clean_name, random.randint(0, 10))
        return {"url": f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}", "type": "svg"}
    except Exception as e:
        print(f"Error generating logo: {e}")
        import traceback
        traceback.print_exc()
        # Even on unexpected error, return SVG instead of crashing
        svg = generate_svg(clean_name, 0)
        return {"url": f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}", "type": "svg"}