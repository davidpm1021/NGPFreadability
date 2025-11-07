import type { ArticleAnalysis } from '../../types';

interface ResultsTableProps {
  results: ArticleAnalysis[];
}

const ResultsTable = ({ results }: ResultsTableProps) => {
  if (results.length === 0) {
    return null;
  }

  const truncateUrl = (url: string, maxLength: number = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
  };

  return (
    <div className="mt-6 overflow-x-auto">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Results</h2>

      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              URL
            </th>
            <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              Title
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              FK
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              SMOG
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              CL
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              ARI
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              Consensus
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              Words
            </th>
            <th className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {results.map((result, index) => (
            <tr
              key={index}
              className={result.extraction_success ? '' : 'bg-red-50'}
            >
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                  title={result.url}
                >
                  {truncateUrl(result.url)}
                </a>
              </td>
              <td className="px-3 py-4 text-sm text-gray-900 max-w-xs truncate">
                {result.title || '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center text-gray-900">
                {result.metrics ? result.metrics.flesch_kincaid_grade : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center text-gray-900">
                {result.metrics ? result.metrics.smog : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center text-gray-900">
                {result.metrics ? result.metrics.coleman_liau : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center text-gray-900">
                {result.metrics ? result.metrics.ari : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center font-semibold text-gray-900">
                {result.metrics ? result.metrics.consensus : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center text-gray-900">
                {result.metrics ? result.metrics.word_count.toLocaleString() : '-'}
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-center">
                {result.extraction_success ? (
                  <span className="text-green-600 font-bold" title="Success">
                    ✓
                  </span>
                ) : (
                  <span className="text-red-600 font-bold" title={result.error || 'Failed'}>
                    ✗
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {results.some(r => !r.extraction_success) && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">
            Failed URLs:
          </h3>
          <ul className="text-sm text-yellow-800 space-y-1">
            {results
              .filter(r => !r.extraction_success)
              .map((result, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2">•</span>
                  <div>
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline break-all"
                    >
                      {result.url}
                    </a>
                    {result.error && (
                      <span className="text-xs text-gray-600 ml-2">
                        ({result.error})
                      </span>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResultsTable;
