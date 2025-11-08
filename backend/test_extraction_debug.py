"""
Debug script to inspect text extraction and readability scoring
Usage: python test_extraction_debug.py <URL>
"""
import sys
from app.services.extraction import extract_text
from app.services.readability import analyze_text


def debug_extraction(url: str):
    """Extract and analyze text from a URL with detailed output"""
    print(f"\n{'='*80}")
    print(f"DEBUGGING EXTRACTION FOR: {url}")
    print(f"{'='*80}\n")

    # Extract text
    print("Step 1: Extracting text...")
    result = extract_text(url)

    if not result.success:
        print(f"[FAILED] EXTRACTION FAILED: {result.error}")
        return

    print(f"[SUCCESS] Extraction successful using: {result.extraction_method}")
    print(f"\nTitle: {result.title or 'N/A'}")
    print(f"\n{'='*80}")
    print("EXTRACTED TEXT:")
    print(f"{'='*80}")
    print(result.text[:2000])  # First 2000 chars
    if len(result.text) > 2000:
        print(f"\n... [truncated, total length: {len(result.text)} characters] ...\n")
        print(result.text[-500:])  # Last 500 chars
    print(f"\n{'='*80}\n")

    # Analyze readability
    print("Step 2: Analyzing readability...")
    metrics = analyze_text(result.text)

    if metrics:
        print(f"\n{'='*80}")
        print("READABILITY METRICS:")
        print(f"{'='*80}")
        print(f"Word Count:           {metrics.word_count:,}")
        print(f"Sentence Count:       {metrics.sentence_count}")
        print(f"Avg Words/Sentence:   {metrics.word_count / max(metrics.sentence_count, 1):.1f}")
        print(f"\nFlesch-Kincaid Grade: {metrics.flesch_kincaid_grade:.1f}")
        print(f"SMOG Index:           {metrics.smog:.1f}")
        print(f"Coleman-Liau Index:   {metrics.coleman_liau:.1f}")
        print(f"ARI:                  {metrics.ari:.1f}")
        print(f"\nCONSENSUS:            {metrics.consensus:.1f}")
        print(f"{'='*80}\n")

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

        print(f"Reading Level: {level}")
        print(f"{'='*80}\n")
    else:
        print("[FAILED] Failed to analyze text")

    # Show first few sentences for inspection
    print("\nFirst 5 sentences (for manual verification):")
    print(f"{'='*80}")
    sentences = result.text.split('.')[:5]
    for i, sent in enumerate(sentences, 1):
        clean_sent = sent.strip()
        if clean_sent:
            print(f"{i}. {clean_sent}.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_extraction_debug.py <URL>")
        print("\nExample:")
        print("  python test_extraction_debug.py https://www.ngpf.org/blog/question-of-the-day/question-of-the-day-what-does-it-mean-to-dispute-a-charge/")
        sys.exit(1)

    url = sys.argv[1]
    debug_extraction(url)
