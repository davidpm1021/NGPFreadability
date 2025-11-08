"""
Extract text from URL and save to markdown for manual comparison
Usage: python extract_to_markdown.py <URL> [output_file.md]
"""
import sys
from datetime import datetime
from app.services.extraction import extract_text
from app.services.readability import analyze_text


def extract_to_markdown(url: str, output_file: str = None):
    """Extract text from URL and save to markdown file"""

    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"extracted_text_{timestamp}.md"

    print(f"\nExtracting text from: {url}")
    print(f"Output file: {output_file}\n")

    # Extract text
    result = extract_text(url)

    if not result.success:
        print(f"[FAILED] Extraction failed: {result.error}")
        return

    # Analyze readability
    metrics = analyze_text(result.text)

    # Create markdown content
    markdown_content = f"""# Extracted Text Analysis

**URL:** {url}
**Extraction Method:** {result.extraction_method}
**Title:** {result.title or 'N/A'}
**Extraction Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Readability Metrics

"""

    if metrics:
        markdown_content += f"""| Metric | Value |
|--------|-------|
| **Flesch-Kincaid Grade** | {metrics.flesch_kincaid_grade:.1f} |
| **SMOG Index** | {metrics.smog:.1f} |
| **Coleman-Liau Index** | {metrics.coleman_liau:.1f} |
| **ARI** | {metrics.ari:.1f} |
| **CONSENSUS** | **{metrics.consensus:.1f}** |
| Word Count | {metrics.word_count:,} |
| Sentence Count | {metrics.sentence_count} |
| Avg Words/Sentence | {metrics.word_count / max(metrics.sentence_count, 1):.1f} |

"""
        # Interpret consensus
        grade = metrics.consensus
        if grade <= 5:
            level = "Elementary School (Grades K-5)"
        elif grade <= 8:
            level = "Middle School (Grades 6-8)"
        elif grade <= 12:
            level = "High School (Grades 9-12)"
        elif grade <= 16:
            level = "College (Undergraduate)"
        else:
            level = "Graduate School"

        markdown_content += f"**Reading Level:** {level}\n\n"
    else:
        markdown_content += "_Failed to analyze readability_\n\n"

    markdown_content += f"""---

## Extracted Text

{result.text}

---

## Notes for Manual Comparison

Please review the extracted text above and compare it with the original article at:
{url}

**Check for:**
- [ ] Is the main article content included?
- [ ] Are photo captions excluded?
- [ ] Are navigation menus excluded?
- [ ] Are ads/sponsored content excluded?
- [ ] Are author bylines/credits excluded?
- [ ] Is the text clean and readable?
- [ ] Are there any encoding issues (weird characters)?
- [ ] Are headings and structure preserved?

**Your Notes:**
```
[Add your observations here]
```

**Recommended Changes:**
```
[Add any improvements needed]
```
"""

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"[SUCCESS] Extracted text saved to: {output_file}")
    print(f"\nQuick Stats:")
    if metrics:
        print(f"  - Words: {metrics.word_count:,}")
        print(f"  - Sentences: {metrics.sentence_count}")
        print(f"  - Reading Level: {metrics.consensus:.1f} ({level})")
    print(f"\nOpen the markdown file to review the extracted text.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_to_markdown.py <URL> [output_file.md]")
        print("\nExample:")
        print("  python extract_to_markdown.py https://apnews.com/article/...")
        print("  python extract_to_markdown.py https://apnews.com/article/... my_extraction.md")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    extract_to_markdown(url, output_file)
