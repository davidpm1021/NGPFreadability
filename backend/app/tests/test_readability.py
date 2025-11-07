"""Tests for readability analysis service"""
import pytest
from app.services.readability import (
    calculate_flesch_kincaid,
    calculate_smog,
    calculate_coleman_liau,
    calculate_ari,
    calculate_consensus,
    count_words,
    count_sentences,
    analyze_text,
)
from app.models.schemas import ReadabilityMetrics


# Sample texts with known grade levels for testing
ELEMENTARY_TEXT = """
The cat sat on the mat. The dog ran in the yard.
The sun is hot. The sky is blue. We play outside.
"""

HIGH_SCHOOL_TEXT = """
The Constitution of the United States established a federal system of government.
This system divides power between national and state governments, creating a balance
that has endured for over two centuries. The framers designed this structure to
prevent the concentration of power while ensuring effective governance.
"""

COLLEGE_TEXT = """
Phenomenological approaches to consciousness emphasize the subjective, first-person
perspective of lived experience. These methodologies challenge reductionist
explanations by highlighting the irreducible qualitative dimensions of mental states.
Contemporary neuroscience increasingly recognizes the limitations of purely
objective accounts, acknowledging the explanatory gap between neural correlates
and phenomenal experience.
"""


class TestFleschKincaidGradeLevel:
    """Test Flesch-Kincaid Grade Level calculation"""

    def test_calculates_elementary_text(self):
        """Test FK grade level for elementary text"""
        grade = calculate_flesch_kincaid(ELEMENTARY_TEXT)

        # Elementary text should be grade 1-5
        assert 0 <= grade <= 6, f"Expected elementary grade, got {grade}"

    def test_calculates_high_school_text(self):
        """Test FK grade level for high school text"""
        grade = calculate_flesch_kincaid(HIGH_SCHOOL_TEXT)

        # High school text should be grade 9-12
        assert 8 <= grade <= 13, f"Expected high school grade, got {grade}"

    def test_calculates_college_text(self):
        """Test FK grade level for college text"""
        grade = calculate_flesch_kincaid(COLLEGE_TEXT)

        # College text should be grade 13+
        assert grade >= 12, f"Expected college grade, got {grade}"

    def test_returns_float(self):
        """Test that FK returns a float"""
        grade = calculate_flesch_kincaid(HIGH_SCHOOL_TEXT)
        assert isinstance(grade, float)

    def test_handles_empty_text(self):
        """Test FK handles empty text gracefully"""
        grade = calculate_flesch_kincaid("")
        assert grade == 0.0

    def test_handles_single_word(self):
        """Test FK handles single word"""
        grade = calculate_flesch_kincaid("Hello")
        assert grade >= 0


class TestSMOGIndex:
    """Test SMOG Index calculation"""

    def test_calculates_elementary_text(self):
        """Test SMOG for elementary text"""
        smog = calculate_smog(ELEMENTARY_TEXT)

        # Should be low grade
        assert 0 <= smog <= 8, f"Expected low SMOG, got {smog}"

    def test_calculates_high_school_text(self):
        """Test SMOG for high school text"""
        smog = calculate_smog(HIGH_SCHOOL_TEXT)

        # Should be mid-range
        assert 8 <= smog <= 14, f"Expected mid SMOG, got {smog}"

    def test_calculates_college_text(self):
        """Test SMOG for college text"""
        smog = calculate_smog(COLLEGE_TEXT)

        # Should be high grade
        assert smog >= 12, f"Expected high SMOG, got {smog}"

    def test_returns_float(self):
        """Test that SMOG returns a float"""
        smog = calculate_smog(HIGH_SCHOOL_TEXT)
        assert isinstance(smog, float)

    def test_handles_empty_text(self):
        """Test SMOG handles empty text"""
        smog = calculate_smog("")
        assert smog == 0.0

    def test_handles_insufficient_sentences(self):
        """Test SMOG with less than 30 sentences (SMOG requirement)"""
        short_text = "This is a test. It has two sentences."
        smog = calculate_smog(short_text)
        # Should still return a value (textstat adjusts for short texts)
        assert smog >= 0


class TestColemanLiauIndex:
    """Test Coleman-Liau Index calculation"""

    def test_calculates_elementary_text(self):
        """Test Coleman-Liau for elementary text"""
        cl = calculate_coleman_liau(ELEMENTARY_TEXT)

        assert 0 <= cl <= 8, f"Expected low Coleman-Liau, got {cl}"

    def test_calculates_high_school_text(self):
        """Test Coleman-Liau for high school text"""
        cl = calculate_coleman_liau(HIGH_SCHOOL_TEXT)

        assert 8 <= cl <= 14, f"Expected mid Coleman-Liau, got {cl}"

    def test_calculates_college_text(self):
        """Test Coleman-Liau for college text"""
        cl = calculate_coleman_liau(COLLEGE_TEXT)

        assert cl >= 12, f"Expected high Coleman-Liau, got {cl}"

    def test_returns_float(self):
        """Test that Coleman-Liau returns a float"""
        cl = calculate_coleman_liau(HIGH_SCHOOL_TEXT)
        assert isinstance(cl, float)

    def test_handles_empty_text(self):
        """Test Coleman-Liau handles empty text"""
        cl = calculate_coleman_liau("")
        assert cl == 0.0


class TestAutomatedReadabilityIndex:
    """Test Automated Readability Index (ARI) calculation"""

    def test_calculates_elementary_text(self):
        """Test ARI for elementary text"""
        ari = calculate_ari(ELEMENTARY_TEXT)

        assert 0 <= ari <= 8, f"Expected low ARI, got {ari}"

    def test_calculates_high_school_text(self):
        """Test ARI for high school text"""
        ari = calculate_ari(HIGH_SCHOOL_TEXT)

        assert 8 <= ari <= 14, f"Expected mid ARI, got {ari}"

    def test_calculates_college_text(self):
        """Test ARI for college text"""
        ari = calculate_ari(COLLEGE_TEXT)

        assert ari >= 12, f"Expected high ARI, got {ari}"

    def test_returns_float(self):
        """Test that ARI returns a float"""
        ari = calculate_ari(HIGH_SCHOOL_TEXT)
        assert isinstance(ari, float)

    def test_handles_empty_text(self):
        """Test ARI handles empty text"""
        ari = calculate_ari("")
        assert ari == 0.0


class TestConsensusCalculation:
    """Test consensus grade level calculation"""

    def test_calculates_average_of_metrics(self):
        """Test that consensus is average of all metrics"""
        metrics = {
            'flesch_kincaid_grade': 10.0,
            'smog': 11.0,
            'coleman_liau': 9.0,
            'ari': 10.0,
        }

        consensus = calculate_consensus(metrics)

        expected = (10.0 + 11.0 + 9.0 + 10.0) / 4
        assert consensus == expected

    def test_rounds_to_one_decimal(self):
        """Test that consensus is rounded appropriately"""
        metrics = {
            'flesch_kincaid_grade': 10.5,
            'smog': 11.2,
            'coleman_liau': 9.8,
            'ari': 10.1,
        }

        consensus = calculate_consensus(metrics)

        # Should be rounded to 1 decimal place
        assert round(consensus, 1) == consensus

    def test_handles_empty_metrics(self):
        """Test consensus with no metrics"""
        consensus = calculate_consensus({})
        assert consensus == 0.0

    def test_handles_partial_metrics(self):
        """Test consensus with subset of metrics"""
        metrics = {
            'flesch_kincaid_grade': 10.0,
            'smog': 12.0,
        }

        consensus = calculate_consensus(metrics)
        assert consensus == 11.0


class TestTextStatistics:
    """Test word and sentence counting"""

    def test_counts_words_correctly(self):
        """Test accurate word counting"""
        text = "The quick brown fox jumps over the lazy dog."
        count = count_words(text)
        assert count == 9

    def test_counts_sentences_correctly(self):
        """Test accurate sentence counting"""
        text = "First sentence. Second sentence! Third sentence?"
        count = count_sentences(text)
        assert count == 3

    def test_handles_empty_text(self):
        """Test counting with empty text"""
        assert count_words("") == 0
        assert count_sentences("") == 0

    def test_handles_text_without_punctuation(self):
        """Test counting text without sentence terminators"""
        text = "This text has no punctuation marks at all"

        words = count_words(text)
        assert words == 8

        sentences = count_sentences(text)
        # textstat should count this as at least 1 sentence
        assert sentences >= 1

    def test_handles_multiple_spaces(self):
        """Test word counting with irregular spacing"""
        text = "Word1    word2     word3"
        count = count_words(text)
        assert count == 3

    def test_handles_hyphenated_words(self):
        """Test word counting with hyphenated words"""
        text = "This is a well-written test."
        count = count_words(text)
        # textstat behavior: typically counts hyphenated as one word
        assert count >= 5


class TestCompleteAnalysis:
    """Test complete text analysis pipeline"""

    def test_analyzes_high_school_text(self):
        """Test complete analysis of high school text"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        assert isinstance(metrics, ReadabilityMetrics)
        assert metrics.flesch_kincaid_grade >= 8
        assert metrics.smog >= 8
        assert metrics.coleman_liau >= 8
        assert metrics.ari >= 8
        assert metrics.consensus >= 8
        assert metrics.word_count > 0
        assert metrics.sentence_count > 0

    def test_analyzes_elementary_text(self):
        """Test complete analysis of elementary text"""
        metrics = analyze_text(ELEMENTARY_TEXT)

        assert metrics.flesch_kincaid_grade <= 6
        assert metrics.smog <= 8
        assert metrics.word_count > 0
        assert metrics.sentence_count > 0

    def test_analyzes_college_text(self):
        """Test complete analysis of college text"""
        metrics = analyze_text(COLLEGE_TEXT)

        assert metrics.flesch_kincaid_grade >= 12
        assert metrics.smog >= 12
        assert metrics.consensus >= 12

    def test_all_metrics_present(self):
        """Test that all metrics are calculated"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        assert hasattr(metrics, 'flesch_kincaid_grade')
        assert hasattr(metrics, 'smog')
        assert hasattr(metrics, 'coleman_liau')
        assert hasattr(metrics, 'ari')
        assert hasattr(metrics, 'consensus')
        assert hasattr(metrics, 'word_count')
        assert hasattr(metrics, 'sentence_count')

    def test_metrics_are_floats(self):
        """Test that all grade metrics are floats"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        assert isinstance(metrics.flesch_kincaid_grade, float)
        assert isinstance(metrics.smog, float)
        assert isinstance(metrics.coleman_liau, float)
        assert isinstance(metrics.ari, float)
        assert isinstance(metrics.consensus, float)

    def test_counts_are_integers(self):
        """Test that counts are integers"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        assert isinstance(metrics.word_count, int)
        assert isinstance(metrics.sentence_count, int)

    def test_handles_empty_text(self):
        """Test analysis of empty text"""
        metrics = analyze_text("")

        assert metrics.flesch_kincaid_grade == 0.0
        assert metrics.smog == 0.0
        assert metrics.coleman_liau == 0.0
        assert metrics.ari == 0.0
        assert metrics.consensus == 0.0
        assert metrics.word_count == 0
        assert metrics.sentence_count == 0


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_very_short_text(self):
        """Test analysis of very short text (< 100 words)"""
        short_text = "This is short. Very short."
        metrics = analyze_text(short_text)

        # Should still calculate metrics
        assert metrics.flesch_kincaid_grade >= 0
        assert metrics.word_count == 5
        assert metrics.sentence_count == 2

    def test_very_long_text(self):
        """Test analysis of very long text (> 10,000 words)"""
        # Create long text by repeating
        long_text = (HIGH_SCHOOL_TEXT + " ") * 200  # ~2000+ words

        metrics = analyze_text(long_text)

        # Should handle without issues
        assert metrics.word_count > 1000
        assert metrics.flesch_kincaid_grade > 0

    def test_text_with_no_punctuation(self):
        """Test text without sentence terminators"""
        text = "This text has no periods or other punctuation marks"

        metrics = analyze_text(text)

        # Should still analyze
        assert metrics.word_count == 9
        assert metrics.sentence_count >= 1  # Should count as at least 1

    def test_text_with_unusual_formatting(self):
        """Test text with unusual spacing and formatting"""
        text = """

        This    has    weird     spacing.


        And multiple   newlines.

        """

        metrics = analyze_text(text)

        # Should handle gracefully
        assert metrics.word_count > 0
        assert metrics.sentence_count >= 2

    def test_text_with_numbers(self):
        """Test text containing numbers"""
        text = "In 2024, the market grew by 15.5% over the previous year's performance."

        metrics = analyze_text(text)

        # Should handle numbers in text
        assert metrics.word_count > 0
        assert metrics.flesch_kincaid_grade > 0

    def test_text_with_special_characters(self):
        """Test text with special characters and symbols"""
        text = "The company's revenue ($1.2M) exceeded expectations—a 50% increase!"

        metrics = analyze_text(text)

        # Should handle special characters
        assert metrics.word_count > 0
        assert metrics.sentence_count >= 1


class TestPerformance:
    """Test performance requirements"""

    def test_analysis_speed(self):
        """Test that analysis completes within performance target"""
        import time

        # Medium-length article (~500 words)
        medium_text = (HIGH_SCHOOL_TEXT + " ") * 10

        start = time.time()
        metrics = analyze_text(medium_text)
        elapsed = time.time() - start

        # Should complete in < 100ms as per requirements
        assert elapsed < 0.1, f"Analysis took {elapsed*1000:.1f}ms (target: <100ms)"

    def test_batch_analysis_speed(self):
        """Test performance of analyzing multiple texts"""
        import time

        texts = [HIGH_SCHOOL_TEXT] * 10

        start = time.time()
        for text in texts:
            analyze_text(text)
        elapsed = time.time() - start

        # 10 texts should complete in reasonable time
        assert elapsed < 1.0, f"Batch analysis took {elapsed:.2f}s"


class TestMetricValidation:
    """Test that metrics fall within expected ranges"""

    def test_grade_levels_are_positive(self):
        """Test that all grade levels are positive"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        assert metrics.flesch_kincaid_grade >= 0
        assert metrics.smog >= 0
        assert metrics.coleman_liau >= 0
        assert metrics.ari >= 0
        assert metrics.consensus >= 0

    def test_grade_levels_are_reasonable(self):
        """Test that grade levels don't exceed reasonable bounds"""
        metrics = analyze_text(COLLEGE_TEXT)

        # Even difficult text shouldn't exceed grade 20
        assert metrics.flesch_kincaid_grade < 25
        assert metrics.smog < 25
        assert metrics.coleman_liau < 25
        assert metrics.ari < 25
        assert metrics.consensus < 25

    def test_consensus_within_range_of_metrics(self):
        """Test that consensus is within range of individual metrics"""
        metrics = analyze_text(HIGH_SCHOOL_TEXT)

        all_metrics = [
            metrics.flesch_kincaid_grade,
            metrics.smog,
            metrics.coleman_liau,
            metrics.ari,
        ]

        min_metric = min(all_metrics)
        max_metric = max(all_metrics)

        assert min_metric <= metrics.consensus <= max_metric

    def test_word_count_reasonable(self):
        """Test that word count matches approximate manual count"""
        text = "One two three four five six seven eight nine ten."
        metrics = analyze_text(text)

        # Should be exactly 10 words
        assert metrics.word_count == 10

    def test_sentence_count_reasonable(self):
        """Test that sentence count matches expected value"""
        text = "Sentence one. Sentence two! Sentence three?"
        metrics = analyze_text(text)

        # Should be exactly 3 sentences
        assert metrics.sentence_count == 3
