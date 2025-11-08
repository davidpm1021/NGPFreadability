/**
 * API service for communicating with the backend
 */
import axios from 'axios';
import type { BatchAnalysisResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const analyzeUrls = async (urls: string[]): Promise<BatchAnalysisResponse> => {
  // Calculate timeout: 15 seconds per URL + 30 second buffer
  // Minimum 60 seconds, maximum 30 minutes for large batches
  const timeoutMs = Math.min(
    Math.max(urls.length * 15000 + 30000, 60000),
    1800000 // 30 minutes max
  );

  const response = await axios.post<BatchAnalysisResponse>(
    `${API_BASE_URL}/api/analyze-urls`,
    { urls },
    {
      timeout: timeoutMs,
    }
  );
  return response.data;
};
