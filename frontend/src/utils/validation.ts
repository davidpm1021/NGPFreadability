/**
 * URL validation utilities
 */

export const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

export const shouldSkipUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    const path = urlObj.pathname.toLowerCase();

    // Skip YouTube URLs
    if (hostname.includes('youtube.com') || hostname.includes('youtu.be')) {
      return true;
    }

    // Skip EdPuzzle URLs
    if (hostname.includes('edpuzzle.com')) {
      return true;
    }

    // Skip Instagram posts
    if (hostname.includes('instagram.com')) {
      return true;
    }

    // Skip direct image files
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'];
    if (imageExtensions.some(ext => path.endsWith(ext))) {
      return true;
    }

    // Skip infographic/data viz platforms
    const infographicDomains = ['infogram.com', 'datawrapper.de', 'tableau.com'];
    if (infographicDomains.some(domain => hostname.includes(domain))) {
      return true;
    }

    return false;
  } catch {
    return false;
  }
};

export const cleanUrl = (url: string): string => {
  // Remove trailing punctuation from URLs
  url = url.trim();
  while (url && '()[].,;'.includes(url[url.length - 1])) {
    url = url.slice(0, -1);
  }
  return url;
};

export const parseUrls = (text: string): string[] => {
  return text
    .split('\n')
    .map(line => cleanUrl(line))
    .filter(line => line.length > 0);
};

export const validateUrls = (urls: string[]): { valid: string[]; invalid: string[] } => {
  const valid: string[] = [];
  const invalid: string[] = [];

  urls.forEach(url => {
    // Skip YouTube and EdPuzzle URLs silently
    if (shouldSkipUrl(url)) {
      return;
    }

    if (isValidUrl(url)) {
      valid.push(url);
    } else {
      invalid.push(url);
    }
  });

  return { valid, invalid };
};
