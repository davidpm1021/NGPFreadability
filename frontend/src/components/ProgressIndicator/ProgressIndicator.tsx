interface ProgressIndicatorProps {
  isProcessing: boolean;
  current: number;
  total: number;
}

const ProgressIndicator = ({ isProcessing, current, total }: ProgressIndicatorProps) => {
  if (!isProcessing) {
    return null;
  }

  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
  const articleText = total === 1 ? 'article' : 'articles';

  return (
    <div className="my-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center mb-2">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
        <span className="text-blue-900 font-medium">
          Processing {current} of {total} {articleText}...
        </span>
      </div>

      <div className="w-full bg-blue-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        ></div>
      </div>

      <div className="mt-1 text-sm text-blue-700 text-right">
        {percentage}%
      </div>
    </div>
  );
};

export default ProgressIndicator;
