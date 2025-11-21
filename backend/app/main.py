from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import httpx
import random
import html
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

API_KEY = os.getenv('OPENAI_API_KEY')
client = AsyncOpenAI(api_key=API_KEY) if API_KEY else None

PALETTE = ["#9381ff", "#b8b8ff", "#f8f7ff"]

app = FastAPI(title="brandpixy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BrandRequest(BaseModel):
    industry: str
    vibe: str
    values: str


async def generate_brand_names(industry: str, vibe: str, values: str) -> list[dict]:
    """
    Generates creative brand names and taglines using OpenAI GPT-4o.
    """
    if not client:
        # Fallback if no key
        return []

    prompt = f"""
    Generate 24 unique, creative brand names and catchy one-line taglines for a brand with:
    Industry: {industry}
    Vibe: {vibe}
    Values: {values}
    
    Return a JSON object with a key "brands" containing an array of objects, each with "name" and "tagline" fields.
    """
    
    try:
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

    prompt = f"A modern, minimalist vector logo for a brand named '{name}'. Vibe: {vibe}. Simple, clean, professional, white background."
    
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


def local_generate(request: BrandRequest, count: int = 24):
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
async def generate(request: BrandRequest):
    try:
        suggestions = []
        
        # 1. Generate Brand Names (using OpenAI if available)
        if API_KEY:
            items = await generate_brand_names(request.industry, request.vibe, request.values)
            
            # 2. Generate Logos (Using local SVG for speed/bulk)
            # Note: We use local SVG generation for the list view because generating 
            # 24 DALL-E images would take ~2 minutes and cost significantly more.
            for i, item in enumerate(items):
                name = item.get('name')
                tagline = item.get('tagline', '')
                if name:
                    # Use local SVG generator for instant results in the grid
                    svg = generate_svg(name, i)
                    suggestions.append({"name": name, "tagline": tagline, "svg": svg})
            
            # Fill with local if OpenAI returned fewer than 24
            if len(suggestions) < 24:
                remaining = 24 - len(suggestions)
                suggestions.extend(local_generate(request, count=remaining))
        else:
            suggestions = local_generate(request, count=24)

        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/generate-logo')
async def generate_logo_endpoint(name: str, vibe: str):
    """
    Dedicated endpoint to generate a high-quality DALL-E logo for a specific brand.
    Frontend can call this on demand (e.g., when user clicks a specific result).
    """
    try:
        url = await generate_logo_image(name, vibe)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))