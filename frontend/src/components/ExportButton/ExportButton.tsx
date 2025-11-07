import Papa from 'papaparse';
import type { ArticleAnalysis } from '../../types';

interface ExportButtonProps {
  results: ArticleAnalysis[];
  disabled?: boolean;
}

const ExportButton = ({ results, disabled = false }: ExportButtonProps) => {
  const handleExport = () => {
    // Prepare data for CSV
    const csvData = results.map(result => ({
      URL: result.url,
      Title: result.title || '',
      'FK Grade': result.metrics?.flesch_kincaid_grade || '',
      'SMOG': result.metrics?.smog || '',
      'Coleman-Liau': result.metrics?.coleman_liau || '',
      'ARI': result.metrics?.ari || '',
      'Consensus': result.metrics?.consensus || '',
      'Word Count': result.metrics?.word_count || '',
      'Sentence Count': result.metrics?.sentence_count || '',
      'Status': result.extraction_success ? 'Success' : 'Failed',
      'Error': result.error || ''
    }));

    // Convert to CSV
    const csv = Papa.unparse(csvData);

    // Create filename with timestamp
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `ngpf-readability-analysis-${timestamp}.csv`;

    // Create blob and download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  if (results.length === 0) {
    return null;
  }

  return (
    <button
      onClick={handleExport}
      disabled={disabled}
      className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <svg
        className="w-5 h-5 mr-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      Export to CSV
    </button>
  );
};

export default ExportButton;
