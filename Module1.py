"""
Module 1: PDF to Markdown Converter 
Fast, parallel extraction with minimal code footprint.
"""

import base64
import os
import time
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def pdf_to_images(pdf_path, dpi=150, poppler_path=None):
    """Convert PDF pages to base64 JPEG images."""
    print(f"Converting PDF (DPI: {dpi})...")
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    
    result = []
    for i, img in enumerate(images, 1):
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        result.append(base64.b64encode(buffered.getvalue()).decode())
        print(f"  Page {i}/{len(images)}")
    
    return result


def extract_page(img_b64, page_num):
    """Extract content from a single page."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract all text from the image in Markdown format. Be concise but complete."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract content:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}", "detail": "high"}}
                ]}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        print(f"  ✓ Page {page_num}")
        return (page_num, response.choices[0].message.content)
    except Exception as e:
        print(f"  ✗ Page {page_num}: {e}")
        return (page_num, f"[Error: {e}]")


def extract_parallel(images, max_workers=5):
    """Extract all pages in parallel."""
    print(f"\nExtracting {len(images)} pages ({max_workers} workers)...")
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(extract_page, img, i) for i, img in enumerate(images, 1)]
        results = dict(f.result() for f in futures)
    
    print(f"✓ Done in {time.time() - start:.1f}s")
    return results


def pdf_to_markdown(pdf_path, output="extracted_content.md", dpi=150, workers=5, poppler_path=None):
    """Main function: PDF to Markdown."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    print("=" * 70)
    print("PDF TO MARKDOWN EXTRACTION")
    print("=" * 70)
    
    start = time.time()
    
    info = pdfinfo_from_path(pdf_path, poppler_path=poppler_path) if poppler_path else pdfinfo_from_path(pdf_path)
    total = info["Pages"]
    print(f"\n✓ {total} pages | DPI={dpi} | Workers={workers}\n")
    
    images = pdf_to_images(pdf_path, dpi, poppler_path)
    pages = extract_parallel(images, workers)
    
    md = [
        f"# {Path(pdf_path).name}\n",
        f"**Pages:** {total} | **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
    ]
    
    for i in range(1, total + 1):
        md.extend([f"## Page {i}\n\n", pages.get(i, "[Missing]"), "\n\n---\n\n"])
    
    with open(output, "w", encoding="utf-8") as f:
        f.write("".join(md))
    
    elapsed = time.time() - start
    print(f"\n✓ Saved: {output}")
    print(f"✓ Time: {elapsed:.1f}s ({elapsed/total:.1f}s/page)")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    PDF = "Testtt.pdf"
    OUTPUT = "extracted_content.md"
    
    # Speed settings
    CONFIG = {
        "dpi": 150,        # 100=faster, 200=quality
        "workers": 8,      # 1-10 concurrent requests
        "poppler_path": None
    }
    
    try:
        pdf_to_markdown(PDF, OUTPUT, **CONFIG)
        print(f"\n✓ Success! Ready for Module 2")
    except Exception as e:
        print(f"\n✗ Error: {e}")

        print("Check: API key, poppler, PDF path")
