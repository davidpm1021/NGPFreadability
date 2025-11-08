# Extraction Comparison Analysis

## Manual Extraction Stats
- Lines: 83
- Starts with: "Anxious travelers across the U.S. felt a bit of relief Friday..."
- Ends with: "...Have that information in your back pocket."
- Clean, focused article content only

## Automated Extraction Issues Found

### ❌ PROBLEMS TO FIX:

1. **Headline/Summary repetition at start (lines 29-32 in automated)**
   - Manual starts directly with main content (line 1)
   - Automated has title and repeated intro paragraphs before main content starts

2. **Photo captions included (lines 34-42 in automated)**
   ```
   Travellers head tdown an escalator after clearing through a security checkpoint...
   Planes are seen at Newark Liberty International Airport...
   Travelers stand in line at a security checkpoint...
   ```
   - Manual: ✅ NO photo captions
   - Automated: ❌ Multiple photo captions present

3. **Duplicate paragraphs (lines 30 and 39 in automated)**
   - Same FAA paragraph appears twice
   - Manual: ✅ Single instance only

4. **Video/image credit lines (lines 31-32 in automated)**
   ```
   Airports in Dallas... (AP Video: Kendria LaFleur)
   Airports in New York... (AP Production: Marissa Duhaney)
   ```
   - Manual: ✅ Clean text without credits
   - Automated: ❌ Still has some credits

### ✅ WHAT'S WORKING:

1. Main article body content is present (lines 43-86 match manual lines 1-83)
2. Headings preserved ("Long lines and, for some, long drives", etc.)
3. Quotes and dialogue intact
4. Paragraph structure maintained
5. Author attribution removed (was present in raw, now gone)
6. Most AP Photo credits removed

## Text Quality Comparison

### Manual Extraction (Your Version):
- Word count: ~1,200 (estimated)
- Clean start/end
- No artifacts
- Proper em-dashes (—)
- No photo captions
- No duplicate content

### Automated Extraction (Current):
- Word count: 1,601
- ~400 extra words from artifacts
- Photo captions (8-10 lines)
- Duplicate paragraphs
- Header/summary repetition
- Some encoding fixes applied (—)

## What Needs to be Filtered Out

Based on this comparison, the cleaning function should remove:

1. **Photo caption patterns:**
   - "Travellers/Travelers [action] in [location] on [date], in [city]"
   - Any sentence ending with just a date and location
   - Lines that describe visual scenes without news content

2. **Video/production credits that slipped through:**
   - "(AP Video: Name)"
   - "(AP Production: Name)"

3. **Repeated header/summary content:**
   - The title and first few paragraphs appear to repeat
   - Should start with main article body

4. **Duplicate detection:**
   - Same paragraph appearing multiple times
   - Already have deduplication logic, but may need strengthening

## Recommended Cleaning Improvements

```python
# Add to clean_extracted_text():

# 1. Remove photo caption sentences (action + location + date pattern)
text = re.sub(r'[^.]*(?:Traveler|Traveller)s?.*?(?:Airport|terminal).*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d{4}[^.]*\.', '', text)

# 2. Remove "Planes/Aircraft are seen at..." captions
text = re.sub(r'Planes?\s+(?:are\s+)?seen\s+at[^.]+\.', '', text)

# 3. Remove location-only description sentences
text = re.sub(r'^[A-Z][^.]*(?:Airport|International|terminal)[^.]*\d{4}[^.]*\.$', '', text, flags=re.MULTILINE)

# 4. Strengthen video/production credit removal
text = re.sub(r'\([^)]*(?:Video|Production)[^)]*\)', '', text)

# 5. Remove lead summary if it duplicates (check for repeated first paragraph)
```
