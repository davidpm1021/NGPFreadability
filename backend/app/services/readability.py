"""Readability analysis service using textstat"""
import logging
from typing import Dict

import textstat

from app.models.schemas import ReadabilityMetrics

logger = logging.getLogger(__name__)


def calculate_flesch_kincaid(text: str) -> float:
    """
    Calculate Flesch-Kincaid Grade Level.

    The Flesch-Kincaid Grade Level indicates the U.S. school grade level
    required to understand the text. It's based on sentence length and
    syllables per word.

    Args:
        text: Text to analyze

    Returns:
        Grade level (0.0 for empty text)
    """
    if not text or not text.strip():
        return 0.0

    try:
        grade = textstat.flesch_kincaid_grade(text)
        return round(float(grade), 1)
    except Exception as e:
        logger.error(f"Error calculating Flesch-Kincaid: {e}")
        return 0.0


def calculate_smog(text: str) -> float:
    """
    Calculate SMOG Index (Simple Measure of Gobbledygook).

    SMOG is designed for health education materials and focuses on
    polysyllabic words. It's particularly good for education-focused content.

    Args:
        text: Text to analyze

    Returns:
        Grade level (0.0 for empty text)
    """
    if not text or not text.strip():
        return 0.0

    try:
        grade = textstat.smog_index(text)
        return round(float(grade), 1)
    except Exception as e:
        logger.error(f"Error calculating SMOG: {e}")
        return 0.0


def calculate_coleman_liau(text: str) -> float:
    """
    Calculate Coleman-Liau Index.

    Coleman-Liau is based on characters per word and words per sentence,
    making it suitable for texts where syllable counting is unreliable.

    Args:
        text: Text to analyze

    Returns:
        Grade level (0.0 for empty text)
    """
    if not text or not text.strip():
        return 0.0

    try:
        grade = textstat.coleman_liau_index(text)
        return round(float(grade), 1)
    except Exception as e:
        logger.error(f"Error calculating Coleman-Liau: {e}")
        return 0.0


def calculate_ari(text: str) -> float:
    """
    Calculate Automated Readability Index (ARI).

    ARI uses characters per word and words per sentence to estimate
    the grade level needed to comprehend the text.

    Args:
        text: Text to analyze

    Returns:
        Grade level (0.0 for empty text)
    """
    if not text or not text.strip():
        return 0.0

    try:
        grade = textstat.automated_readability_index(text)
        return round(float(grade), 1)
    except Exception as e:
        logger.error(f"Error calculating ARI: {e}")
        return 0.0


def calculate_consensus(metrics: Dict[str, float]) -> float:
    """
    Calculate consensus grade level as average of all metrics.

    Args:
        metrics: Dictionary of metric names to values

    Returns:
        Average grade level (0.0 if no metrics)
    """
    if not metrics:
        return 0.0

    # Filter out non-numeric values
    values = [v for v in metrics.values() if isinstance(v, (int, float))]

    if not values:
        return 0.0

    consensus = sum(values) / len(values)
    return round(consensus, 1)


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Text to analyze

    Returns:
        Word count
    """
    if not text or not text.strip():
        return 0

    try:
        count = textstat.lexicon_count(text, removepunct=True)
        return int(count)
    except Exception as e:
        logger.error(f"Error counting words: {e}")
        return 0


def count_sentences(text: str) -> int:
    """
    Count sentences in text.

    Args:
        text: Text to analyze

    Returns:
        Sentence count
    """
    if not text or not text.strip():
        return 0

    try:
        count = textstat.sentence_count(text)
        return int(count)
    except Exception as e:
        logger.error(f"Error counting sentences: {e}")
        return 0


def analyze_text(text: str) -> ReadabilityMetrics:
    """
    Perform complete readability analysis on text.

    Calculates all readability metrics:
    - Flesch-Kincaid Grade Level (primary metric)
    - SMOG Index (education-focused)
    - Coleman-Liau Index
    - Automated Readability Index (ARI)
    - Consensus (average of all four)

    Also provides text statistics:
    - Word count
    - Sentence count

    Args:
        text: Text to analyze

    Returns:
        ReadabilityMetrics object with all calculated metrics
    """
    if not text or not text.strip():
        return ReadabilityMetrics(
            flesch_kincaid_grade=0.0,
            smog=0.0,
            coleman_liau=0.0,
            ari=0.0,
            consensus=0.0,
            word_count=0,
            sentence_count=0,
        )

    # Calculate all readability metrics
    fk_grade = calculate_flesch_kincaid(text)
    smog_grade = calculate_smog(text)
    cl_grade = calculate_coleman_liau(text)
    ari_grade = calculate_ari(text)

    # Calculate consensus
    metrics_dict = {
        'flesch_kincaid_grade': fk_grade,
        'smog': smog_grade,
        'coleman_liau': cl_grade,
        'ari': ari_grade,
    }
    consensus_grade = calculate_consensus(metrics_dict)

    # Count words and sentences
    words = count_words(text)
    sentences = count_sentences(text)

    logger.info(
        f"Analysis complete: FK={fk_grade}, SMOG={smog_grade}, "
        f"CL={cl_grade}, ARI={ari_grade}, Consensus={consensus_grade}, "
        f"Words={words}, Sentences={sentences}"
    )

    return ReadabilityMetrics(
        flesch_kincaid_grade=fk_grade,
        smog=smog_grade,
        coleman_liau=cl_grade,
        ari=ari_grade,
        consensus=consensus_grade,
        word_count=words,
        sentence_count=sentences,
    )


def get_grade_level_description(grade: float) -> str:
    """
    Get human-readable description of grade level.

    Args:
        grade: Numeric grade level

    Returns:
        Description string (e.g., "High School", "College")
    """
    if grade <= 5:
        return "Elementary School"
    elif grade <= 8:
        return "Middle School"
    elif grade <= 12:
        return "High School"
    elif grade <= 16:
        return "College"
    else:
        return "Graduate School"


def analyze_text_with_description(text: str) -> Dict:
    """
    Analyze text and include grade level descriptions.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with metrics and descriptions
    """
    metrics = analyze_text(text)

    return {
        'metrics': metrics,
        'grade_description': get_grade_level_description(metrics.consensus),
        'reading_ease': _get_reading_ease_description(metrics.flesch_kincaid_grade),
    }


def _get_reading_ease_description(grade: float) -> str:
    """Get reading ease description from grade level"""
    if grade <= 5:
        return "Very Easy"
    elif grade <= 8:
        return "Easy"
    elif grade <= 10:
        return "Fairly Easy"
    elif grade <= 12:
        return "Standard"
    elif grade <= 14:
        return "Fairly Difficult"
    elif grade <= 16:
        return "Difficult"
    else:
        return "Very Difficult"
