"""
Module 2: Rule Extraction from Markdown
Reads Markdown content with page numbers and extracts rules using Vision LLM.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables!")
client = OpenAI(api_key=api_key)


def load_markdown_file(markdown_path: str) -> str:
    """
    Load markdown content from file.
    
    Args:
        markdown_path: Path to markdown file
    
    Returns:
        Markdown content as string
    """
    if not os.path.exists(markdown_path):
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
    
    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content


def parse_markdown_by_pages(markdown_content: str) -> dict[int, str]:
    """
    Parse markdown content and separate by page numbers.
    
    Args:
        markdown_content: Full markdown content
    
    Returns:
        Dictionary mapping page numbers to their content
    """
    pages = {}
    
    # Split by page headers (## Page X)
    page_pattern = r'## Page (\d+)\n\n(.*?)(?=\n\n---\n\n|\Z)'
    matches = re.findall(page_pattern, markdown_content, re.DOTALL)
    
    for page_num, content in matches:
        pages[int(page_num)] = content.strip()
    
    return pages


def extract_rules_from_markdown_single_pass(markdown_content: str) -> str:
    """
    Extract rules from complete markdown document in a single pass.
    Best for documents with <= 10 pages.
    
    Args:
        markdown_content: Full markdown content with page numbers
    
    Returns:
        Extracted rules with page references
    """
    system_prompt = """
You are an expert document analyst specializing in extracting rules, guidelines, and constraints.

Your task:
1. Analyze the complete markdown document provided
2. Identify ALL rules, guidelines, constraints, instructions, or requirements
3. Track which pages contain each rule
4. If a rule spans multiple pages, note the page range
5. Preserve the complete context of each rule

Output format:

DOCUMENT SUMMARY:
<2-4 sentence overview of the document>

EXTRACTED RULES:
[Page X] Rule 1: <complete rule description>
[Page Y-Z] Rule 2: <rule spanning pages Y to Z>
[Page Z] Rule 3: <another rule>

CROSS-PAGE OBSERVATIONS:
<Note any rules or content that continues across multiple pages>

NOTES:
<Additional context or observations>
""".strip()

    print("Sending markdown content to LLM for rule extraction...")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Analyze this document and extract all rules:\n\n{markdown_content}"
            }
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    
    return response.choices[0].message.content


def extract_rules_from_markdown_sliding_window(markdown_content: str, window_size: int = 3) -> str:
    """
    Extract rules using sliding window approach for long documents.
    Best for documents with > 10 pages.
    
    Args:
        markdown_content: Full markdown content
        window_size: Number of pages to include in each window
    
    Returns:
        Consolidated extracted rules
    """
    pages = parse_markdown_by_pages(markdown_content)
    total_pages = len(pages)
    
    if total_pages <= 3:
        print("Document has 3 or fewer pages. Using single-pass extraction.")
        return extract_rules_from_markdown_single_pass(markdown_content)
    
    print(f"\nProcessing {total_pages} pages with sliding window approach...")
    
    system_prompt = """
You are analyzing a section of a larger document.

Extract:
1. All rules, guidelines, and constraints in these pages
2. Note if any rule appears incomplete (continues from previous or to next pages)
3. Include page numbers for each rule

Format:
[Page X] Rule: <rule text>

If incomplete:
[Page X] INCOMPLETE: <description of what continues>
""".strip()

    all_extractions = []
    
    for i in range(1, total_pages + 1):
        # Define window
        start_page = max(1, i - 1)
        end_page = min(total_pages, i + 1)
        
        window_pages = range(start_page, end_page + 1)
        print(f"  Window {i}/{total_pages}: Pages {start_page}-{end_page} (focusing on page {i})")
        
        # Combine content from window pages
        window_content = []
        for page_num in window_pages:
            window_content.append(f"## Page {page_num}\n\n{pages[page_num]}\n")
        
        combined_content = "\n".join(window_content)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Analyzing pages {start_page}-{end_page}, focusing on page {i}:\n\n{combined_content}"
                }
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        
        all_extractions.append(response.choices[0].message.content)
    
    print("\n✓ All windows processed. Consolidating results...")
    
    # Consolidation step
    consolidation_prompt = f"""
You have received rule extractions from a {total_pages}-page document, processed in overlapping windows.

Your task:
1. Merge duplicate rules (same rule extracted multiple times)
2. Combine incomplete rules split across windows
3. Remove redundancy while keeping all unique rules
4. Create a final clean list with page references

Extractions:

{chr(10).join(f"=== WINDOW {i+1} ===\n{ext}\n" for i, ext in enumerate(all_extractions))}

Provide consolidated output:

DOCUMENT SUMMARY:
<brief summary>

CONSOLIDATED RULES:
[Page X] Rule 1: <complete rule>
[Page Y-Z] Rule 2: <rule spanning pages>

NOTES:
<Observations about cross-page rules>
"""
    
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": consolidation_prompt}
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    
    return final_response.choices[0].message.content


def extract_rules_from_markdown(
    markdown_path: str,
    output_file: str = "extracted_rules.txt",
    use_sliding_window: bool = None
) -> str:
    """
    Main function: Extract rules from markdown file.
    
    Args:
        markdown_path: Path to input markdown file
        output_file: Path to output file for rules
        use_sliding_window: Force sliding window (True) or single pass (False).
                           If None, automatically decides based on page count.
    
    Returns:
        Path to the generated rules file
    """
    print("=" * 70)
    print("MODULE 2: RULE EXTRACTION FROM MARKDOWN")
    print("=" * 70)
    
    # Load markdown content
    print(f"\n✓ Loading markdown file: {markdown_path}")
    markdown_content = load_markdown_file(markdown_path)
    
    # Count pages
    pages = parse_markdown_by_pages(markdown_content)
    total_pages = len(pages)
    print(f"✓ Detected {total_pages} pages in markdown\n")
    
    # Decide extraction strategy
    if use_sliding_window is None:
        use_sliding_window = total_pages > 10
    
    if use_sliding_window:
        print("Strategy: SLIDING-WINDOW approach (for long documents)\n")
        result = extract_rules_from_markdown_sliding_window(markdown_content)
    else:
        print("Strategy: SINGLE-PASS approach (for short documents)\n")
        result = extract_rules_from_markdown_single_pass(markdown_content)
    
    # Display results
    print("\n" + "=" * 70)
    print("EXTRACTION RESULTS")
    print("=" * 70)
    print(result)
    
    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("RULE EXTRACTION RESULTS\n")
        f.write(f"Source Markdown: {markdown_path}\n")
        f.write(f"Total Pages: {total_pages}\n")
        f.write("=" * 70 + "\n\n")
        f.write(result)
    
    print(f"\n✓ Rules saved to '{output_file}'")
    print("\n" + "=" * 70)
    print("MODULE 2 COMPLETE!")
    print("=" * 70)
    
    return output_file


def main():
    """Main execution for Module 2"""
    
    # Configuration
    markdown_file = "extracted_content.md"  # Output from Module 1
    output_file = "extracted_rules.txt"
    
    try:
        rules_file = extract_rules_from_markdown(markdown_file, output_file)
        print(f"\n✓ Success! Rules extracted to: {rules_file}")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\n⚠ Please run Module 1 first to generate the markdown file!")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure OPENAI_API_KEY is set in .env file")
        print("2. Verify markdown file exists from Module 1")
        print("3. Check markdown file format is correct")


if __name__ == "__main__":
    main()