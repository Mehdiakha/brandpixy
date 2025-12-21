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
    return {"status": "ok", "gemini_enabled": bool(API_KEY)}


class BrandRequest(BaseModel):
    industry: str
    vibe: str
    values: str


def generate_brand_names(industry: str, vibe: str, values: str) -> list[dict]:
    """
    Generates creative brand names and taglines using Google Gemini.
    """
    if not client:
        print("Gemini Client not initialized. Skipping AI generation.")
        return []

    prompt = f"""
    Generate 24 unique, creative brand names and catchy one-line taglines for a brand with:
    Industry: {industry}
    Vibe: {vibe}
    Values: {values}
    
    Return a JSON object with a key "brands" containing an array of objects, each with "name" and "tagline" fields.
    Output ONLY valid JSON, no markdown formatting.
    """
    
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
            
        return items
    except Exception as e:
        print(f"Gemini Text Generation Error: {e}")
        return []


def generate_logo_image(name: str, vibe: str) -> str:
    """
    Generates a logo image using Google Gemini Imagen.
    Returns the image as a base64 data URL.
    """
    if not client:
        return ""

    # Enhanced prompt for better logo quality
    prompt = f"A professional, high-quality logo design for a brand named '{name}'. Industry vibe: {vibe}. Vector style, flat design, minimal, white background, high resolution, no text."
    
    try:
        print(f"Calling Imagen API with prompt: {prompt[:100]}...")
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            ),
        )
        
        if response.generated_images and len(response.generated_images) > 0:
            image_bytes = response.generated_images[0].image.image_bytes
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
        print("Imagen returned no images in response")
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
        
        # 1. Generate Brand Names (using Gemini if available)
        if API_KEY:
            print("Gemini API Key found. Attempting AI generation...")
            items = generate_brand_names(brand_request.industry, brand_request.vibe, brand_request.values)
            print(f"Gemini returned {len(items)} items.")
            
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
        if not API_KEY:
            print("No Gemini API Key found for logo generation.")
            raise HTTPException(status_code=500, detail="Gemini API Key not configured on server. Please set GEMINI_API_KEY environment variable.")

        url = generate_logo_image(clean_name, clean_vibe)
        if not url:
             print("Gemini returned empty image")
             raise HTTPException(status_code=500, detail="Gemini returned an empty image. Check API key quotas or permissions.")
             
        print(f"Generated logo successfully for: {clean_name}")
        return {"url": url}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error generating logo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")