/**
 * Type definitions for NGPF Readability Analyzer
 */

export interface ReadabilityMetrics {
  flesch_kincaid_grade: number;
  smog: number;
  coleman_liau: number;
  ari: number;
  consensus: number;
  word_count: number;
  sentence_count: number;
}

export interface ArticleAnalysis {
  url: string;
  title: string | null;
  extraction_success: boolean;
  metrics: ReadabilityMetrics | null;
  error: string | null;
}

export interface AnalysisSummary {
  total_urls: number;
  successful: number;
  failed: number;
  average_grade_level: number | null;
}

export interface BatchAnalysisResponse {
  results: ArticleAnalysis[];
  summary: AnalysisSummary;
}
