import { parseUrls, validateUrls } from '../../utils/validation';

interface UrlInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const UrlInput = ({ value, onChange, disabled = false }: UrlInputProps) => {
  const urls = parseUrls(value);
  const { valid, invalid } = validateUrls(urls);

  const handleClear = () => {
    onChange('');
  };

  return (
    <div className="w-full">
      <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Paste Article URLs (one per line):
      </label>

      <textarea
        id="url-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="https://www.example.com/article1
https://www.example.com/article2
https://www.example.com/article3"
        className="w-full h-48 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed font-mono text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
        rows={10}
      />

      <div className="mt-2 flex items-center justify-between">
        <div className="text-sm">
          {valid.length > 0 && (
            <span className="text-green-600 dark:text-green-400 font-medium">
              {valid.length} valid URL{valid.length !== 1 ? 's' : ''} detected
            </span>
          )}
          {invalid.length > 0 && (
            <span className="text-red-600 dark:text-red-400 ml-3">
              {invalid.length} invalid URL{invalid.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {value && (
          <button
            onClick={handleClear}
            disabled={disabled}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
};

export default UrlInput;
