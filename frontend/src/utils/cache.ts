/**
 * Client-side caching utility for analysis results
 * Stores results in localStorage to survive timeouts and page refreshes
 */
import type { ArticleAnalysis } from '../types';

const CACHE_KEY = 'ngpf-readability-cache';
const CACHE_VERSION = '1.0';
const CACHE_EXPIRY_DAYS = 7; // Cache expires after 7 days

interface CacheEntry {
  url: string;
  result: ArticleAnalysis;
  timestamp: number;
}

interface Cache {
  version: string;
  entries: Record<string, CacheEntry>;
}

/**
 * Get the cache from localStorage
 */
function getCache(): Cache {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) {
      return { version: CACHE_VERSION, entries: {} };
    }

    const cache = JSON.parse(cached) as Cache;

    // Check version compatibility
    if (cache.version !== CACHE_VERSION) {
      console.log('Cache version mismatch, clearing cache');
      return { version: CACHE_VERSION, entries: {} };
    }

    return cache;
  } catch (error) {
    console.error('Error reading cache:', error);
    return { version: CACHE_VERSION, entries: {} };
  }
}

/**
 * Save the cache to localStorage
 */
function saveCache(cache: Cache): void {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
  } catch (error) {
    console.error('Error saving cache:', error);
  }
}

/**
 * Check if a cache entry is expired
 */
function isExpired(timestamp: number): boolean {
  const expiryMs = CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000;
  return Date.now() - timestamp > expiryMs;
}

/**
 * Get cached result for a URL
 */
export function getCachedResult(url: string): ArticleAnalysis | null {
  const cache = getCache();
  const entry = cache.entries[url];

  if (!entry) {
    return null;
  }

  // Check if expired
  if (isExpired(entry.timestamp)) {
    // Remove expired entry
    delete cache.entries[url];
    saveCache(cache);
    return null;
  }

  return entry.result;
}

/**
 * Cache a result for a URL
 */
export function cacheResult(url: string, result: ArticleAnalysis): void {
  const cache = getCache();

  cache.entries[url] = {
    url,
    result,
    timestamp: Date.now(),
  };

  saveCache(cache);
}

/**
 * Cache multiple results
 */
export function cacheResults(results: ArticleAnalysis[]): void {
  const cache = getCache();

  results.forEach((result) => {
    cache.entries[result.url] = {
      url: result.url,
      result,
      timestamp: Date.now(),
    };
  });

  saveCache(cache);
}

/**
 * Get cached results for multiple URLs
 * Returns { cached: ArticleAnalysis[], missing: string[] }
 */
export function getCachedResults(urls: string[]): {
  cached: ArticleAnalysis[];
  missing: string[];
} {
  const cache = getCache();
  const cached: ArticleAnalysis[] = [];
  const missing: string[] = [];

  urls.forEach((url) => {
    const entry = cache.entries[url];

    if (entry && !isExpired(entry.timestamp)) {
      cached.push(entry.result);
    } else {
      missing.push(url);
      // Clean up expired entry
      if (entry && isExpired(entry.timestamp)) {
        delete cache.entries[url];
      }
    }
  });

  // Save cache if we cleaned up any expired entries
  if (cached.length + missing.length !== urls.length) {
    saveCache(cache);
  }

  return { cached, missing };
}

/**
 * Clear all cached results
 */
export function clearCache(): void {
  localStorage.removeItem(CACHE_KEY);
}

/**
 * Get cache statistics
 */
export function getCacheStats(): {
  totalEntries: number;
  expiredEntries: number;
  cacheSize: string;
} {
  const cache = getCache();
  const entries = Object.values(cache.entries);
  const expiredCount = entries.filter((entry) => isExpired(entry.timestamp)).length;

  // Estimate cache size
  const cacheString = JSON.stringify(cache);
  const sizeKB = (cacheString.length / 1024).toFixed(2);

  return {
    totalEntries: entries.length,
    expiredEntries: expiredCount,
    cacheSize: `${sizeKB} KB`,
  };
}

/**
 * Clean up expired entries
 */
export function cleanupCache(): number {
  const cache = getCache();
  const entries = Object.entries(cache.entries);
  let removedCount = 0;

  entries.forEach(([url, entry]) => {
    if (isExpired(entry.timestamp)) {
      delete cache.entries[url];
      removedCount++;
    }
  });

  if (removedCount > 0) {
    saveCache(cache);
  }

  return removedCount;
}
