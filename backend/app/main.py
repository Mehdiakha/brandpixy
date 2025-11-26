from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import httpx
import random
import html
from dotenv import load_dotenv
from openai import AsyncOpenAI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

API_KEY = os.getenv('OPENAI_API_KEY')
client = AsyncOpenAI(api_key=API_KEY) if API_KEY else None

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
    return {"status": "ok", "openai_enabled": bool(API_KEY)}


class BrandRequest(BaseModel):
    industry: str
    vibe: str
    values: str


async def generate_brand_names(industry: str, vibe: str, values: str) -> list[dict]:
    """
    Generates creative brand names and taglines using OpenAI GPT-4o.
    """
    if not client:
        print("OpenAI Client not initialized. Skipping AI generation.")
        return []

    prompt = f"""
    Generate 24 unique, creative brand names and catchy one-line taglines for a brand with:
    Industry: {industry}
    Vibe: {vibe}
    Values: {values}
    
    Return a JSON object with a key "brands" containing an array of objects, each with "name" and "tagline" fields.
    """
    
    try:
        print(f"Sending request to OpenAI for industry: {industry}")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative brand strategist. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.8,
        )
        content = response.choices[0].message.content
        print("Received response from OpenAI")
        data = json.loads(content)
        
        items = data.get('brands', [])
        if not items and isinstance(data, list):
            items = data
            
        return items
    except Exception as e:
        print(f"OpenAI Text Generation Error: {e}")
        return []


async def generate_logo_image(name: str, vibe: str) -> str:
    """
    Generates a logo image URL using OpenAI DALL-E 3.
    Note: This is expensive and slow, so use sparingly (not for bulk generation).
    """
    if not client:
        return ""

    # Enhanced prompt for better logo quality
    prompt = f"A professional, high-quality logo design for a brand named '{name}'. Industry vibe: {vibe}. Vector style, flat design, minimal, white background, high resolution."
    
    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"OpenAI Image Generation Error: {e}")
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
        
        # 1. Generate Brand Names (using OpenAI if available)
        if API_KEY:
            print("OpenAI API Key found. Attempting AI generation...")
            items = await generate_brand_names(brand_request.industry, brand_request.vibe, brand_request.values)
            print(f"OpenAI returned {len(items)} items.")
            
            # 2. Generate Logos (Using local SVG for speed/bulk)
            for i, item in enumerate(items):
                name = item.get('name')
                tagline = item.get('tagline', '')
                if name:
                    svg = generate_svg(name, i)
                    suggestions.append({"name": name, "tagline": tagline, "svg": svg})
            
            # Fill with local if OpenAI returned fewer than 20
            if len(suggestions) < 20:
                print(f"Filling remaining {20 - len(suggestions)} slots with local generation.")
                remaining = 20 - len(suggestions)
                suggestions.extend(local_generate(brand_request, count=remaining))
        else:
            print("No OpenAI API Key found. Using local generation.")
            suggestions = local_generate(brand_request, count=20)

        print(f"Returning {len(suggestions)} suggestions.")
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"CRITICAL ERROR in /api/generate: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/generate-logo')
@limiter.limit("10/minute")
async def generate_logo_endpoint(request: Request, name: str, vibe: str):
    """
    Dedicated endpoint to generate a high-quality DALL-E logo for a specific brand.
    Frontend can call this on demand (e.g., when user clicks a specific result).
    """
    print(f"Received logo generation request for: {name}, vibe: {vibe}")
    try:
        if not API_KEY:
            print("No OpenAI API Key found for logo generation.")
            raise HTTPException(status_code=500, detail="OpenAI API Key not configured on server. Please set OPENAI_API_KEY environment variable.")

        url = await generate_logo_image(name, vibe)
        if not url:
             print("OpenAI returned empty URL")
             raise HTTPException(status_code=500, detail="OpenAI returned an empty image URL. Check API key quotas or permissions.")
             
        print(f"Generated logo URL: {url}")
        return {"url": url}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error generating logo: {e}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")