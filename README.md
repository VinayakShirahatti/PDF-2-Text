📘 PDF → Markdown → Rule Extraction Pipeline

A two-module system for converting PDFs into markdown using Vision Models and extracting structured rules, guidelines, constraints, and cross-page relationships.

This project contains:

Module 1: PDF → Images → Markdown (parallel extraction)

Module 2: Markdown → Rule Extraction (single-pass or sliding-window)

🚀 Features
✅ Module 1 (PDF → Markdown)

Converts each PDF page into JPEG images

Sends pages to gpt-4o Vision for extraction

Parallel processing using ThreadPoolExecutor

Outputs a clean Markdown file with:

Page-wise extracted text

Page numbering

Metadata header

✅ Module 2 (Markdown → Rules)

Reads Markdown generated from Module 1

Extracts rules, guidelines, constraints, instructions

Two intelligent strategies:

Single-pass for small documents (≤ 10 pages)

Sliding window for long documents (> 10 pages)

Supports:

Cross-page rule detection

De-duplication and consolidation

Clean final output with page references

📂 Project Structure
├── Module1.py             # PDF → Markdown conversion
├── Module2.py             # Rule extraction from Markdown
├── extracted_content.md   # Output from Module 1
├── extracted_rules.txt    # Output from Module 2
├── .env                   # Stores OPENAI_API_KEY
└── README.md              # Documentation

🛠️ Installation & Setup
1️⃣ Install required dependencies
pip install pdf2image pillow openai python-dotenv

2️⃣ Install Poppler (for PDF-to-image conversion)

Windows: Download from
https://github.com/oschwartz10612/poppler-windows/releases

Add the extracted folder's /bin path to your system PATH.

3️⃣ Add your OpenAI API Key

Create a .env file:

OPENAI_API_KEY=your_key_here

📑 MODULE 1 – PDF → Markdown
▶️ Running Module 1

Modify PDF (input) and OUTPUT (output) inside Module1.py, then run:

python Module1.py

What Module 1 Does

Loads your API key

Converts PDF pages → JPEG

Sends each page to OpenAI's Vision model

Extracts the textual content

Saves a structured extracted_content.md like:

# sample.pdf
**Pages:** 12 | **Date:** 2025-12-07 10:30:22

---

## Page 1
<markdown text>

---

## Page 2
<markdown text>

---

Output

extracted_content.md

📘 MODULE 2 – Markdown → Rules Extraction
▶️ Running Module 2

Simply run:

python Module2.py


Make sure extracted_content.md exists (generated from Module 1).

What Module 2 Does

Loads the Markdown file

Detects number of pages

Chooses extraction strategy:

Single-pass (≤ 10 pages)

Sliding-window (> 10 pages)

Extracts:

Rules

Guidelines

Constraints

Instructions

Cross-page rule connections

Produces a final consolidated rule set.

Output Format Example
DOCUMENT SUMMARY:
<High-level overview>

EXTRACTED RULES:
[Page 1] Rule: Must follow XYZ
[Page 3-4] Rule: This rule spans multiple pages
[Page 7] Rule: Ensure ABC

CROSS-PAGE OBSERVATIONS:
<Notable connections>

NOTES:
<Additional context>

Final output file:

extracted_rules.txt

🔗 End-to-End Workflow
PDF → (Module 1) → Markdown → (Module 2) → Structured Rules

🧪 Example Usage
Step 1 — Convert a PDF to Markdown
pdf_to_markdown("MyPDF.pdf", "extracted_content.md", dpi=150, workers=8)

Step 2 — Extract rules
extract_rules_from_markdown("extracted_content.md", "extracted_rules.txt")

📌 Notes & Tips

DPI affects quality vs. speed

Increase workers (5–10) for faster extraction

Use sliding window for large PDFs to reduce token usage

Handles cross-page rule continuity using windowing + consolidation

Designed for scalable, production-grade PDF rule extraction

🏁 Conclusion

This system converts complex PDFs into clean Markdown and automatically extracts structured rules using intelligent single-pass or sliding-window methods
