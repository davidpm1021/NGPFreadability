import type { AnalysisSummary } from '../../types';

interface SummaryStatsProps {
  summary: AnalysisSummary | null;
}

const getGradeDescription = (grade: number): string => {
  if (grade <= 5) return 'Elementary School';
  if (grade <= 8) return 'Middle School';
  if (grade <= 12) return 'High School';
  if (grade <= 16) return 'College';
  return 'Graduate School';
};

const SummaryStats = ({ summary }: SummaryStatsProps) => {
  if (!summary) {
    return null;
  }

  const successRate = summary.total_urls > 0
    ? Math.round((summary.successful / summary.total_urls) * 100)
    : 0;

  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Average Grade Level */}
        {summary.average_grade_level !== null && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium mb-1">
              Average Grade Level
            </div>
            <div className="text-3xl font-bold text-blue-900">
              {summary.average_grade_level}
            </div>
            <div className="text-xs text-blue-700 mt-1">
              {getGradeDescription(summary.average_grade_level)}
            </div>
          </div>
        )}

        {/* Total URLs */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 font-medium mb-1">
            Total URLs
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {summary.total_urls}
          </div>
        </div>

        {/* Successful */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-sm text-green-600 font-medium mb-1">
            Successful
          </div>
          <div className="text-3xl font-bold text-green-900">
            {summary.successful}
          </div>
          <div className="text-xs text-green-700 mt-1">
            {successRate}% success rate
          </div>
        </div>

        {/* Failed */}
        {summary.failed > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="text-sm text-red-600 font-medium mb-1">
              Failed
            </div>
            <div className="text-3xl font-bold text-red-900">
              {summary.failed}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryStats;
