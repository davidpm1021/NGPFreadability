import { useState } from 'react';
import UrlInput from './components/UrlInput';
import ProgressIndicator from './components/ProgressIndicator';
import SummaryStats from './components/SummaryStats';
import ResultsTable from './components/ResultsTable';
import ExportButton from './components/ExportButton';
import { analyzeUrls } from './services/api';
import { parseUrls, validateUrls } from './utils/validation';
import type { BatchAnalysisResponse } from './types';

function App() {
  const [urlText, setUrlText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [results, setResults] = useState<BatchAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    // Parse and validate URLs
    const urls = parseUrls(urlText);
    const { valid, invalid } = validateUrls(urls);

    if (valid.length === 0) {
      setError('Please enter at least one valid URL');
      return;
    }

    if (invalid.length > 0) {
      const proceed = window.confirm(
        `Found ${invalid.length} invalid URL(s). Proceed with ${valid.length} valid URLs?`
      );
      if (!proceed) return;
    }

    // Reset state
    setError(null);
    setResults(null);
    setIsProcessing(true);
    setProgress({ current: 0, total: valid.length });

    try {
      // Call API
      const response = await analyzeUrls(valid);

      // Update results
      setResults(response);
      setProgress({ current: valid.length, total: valid.length });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to analyze URLs. Please check your connection and try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const urls = parseUrls(urlText);
  const { valid } = validateUrls(urls);
  const canAnalyze = valid.length > 0 && !isProcessing;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            NGPF Article Readability Analyzer
          </h1>
          <p className="mt-2 text-gray-600">
            Analyze readability metrics for article URLs using Flesch-Kincaid, SMOG, Coleman-Liau, and ARI.
          </p>
        </div>

        {/* URL Input */}
        <div className="bg-white shadow rounded-lg p-6">
          <UrlInput
            value={urlText}
            onChange={setUrlText}
            disabled={isProcessing}
          />

          {/* Analyze Button */}
          <div className="mt-4 flex items-center justify-between">
            <button
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                'Analyze All Articles'
              )}
            </button>

            {results && (
              <ExportButton
                results={results.results}
                disabled={isProcessing}
              />
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Progress Indicator */}
        <ProgressIndicator
          isProcessing={isProcessing}
          current={progress.current}
          total={progress.total}
        />

        {/* Results */}
        {results && (
          <div className="bg-white shadow rounded-lg p-6 mt-6">
            <SummaryStats summary={results.summary} />
            <ResultsTable results={results.results} />
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Internal tool for NGPF · Processes {valid.length > 0 ? valid.length : 'multiple'} URLs
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
