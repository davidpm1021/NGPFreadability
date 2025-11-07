/**
 * API service for communicating with the backend
 */
import axios from 'axios';
import type { BatchAnalysisResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const analyzeUrls = async (urls: string[]): Promise<BatchAnalysisResponse> => {
  const response = await axios.post<BatchAnalysisResponse>(
    `${API_BASE_URL}/api/analyze-urls`,
    { urls },
    {
      timeout: 60000, // 60 second timeout
    }
  );
  return response.data;
};
