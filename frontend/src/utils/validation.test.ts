import { describe, it, expect } from 'vitest';
import { isValidUrl, parseUrls, validateUrls } from './validation';

describe('validation utilities', () => {
  describe('isValidUrl', () => {
    it('should accept valid HTTP URLs', () => {
      expect(isValidUrl('http://example.com')).toBe(true);
    });

    it('should accept valid HTTPS URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
    });

    it('should reject invalid URLs', () => {
      expect(isValidUrl('not a url')).toBe(false);
      expect(isValidUrl('ftp://example.com')).toBe(false);
      expect(isValidUrl('')).toBe(false);
    });
  });

  describe('parseUrls', () => {
    it('should parse URLs from multi-line text', () => {
      const text = 'https://example.com\nhttps://test.com';
      expect(parseUrls(text)).toEqual(['https://example.com', 'https://test.com']);
    });

    it('should trim whitespace', () => {
      const text = '  https://example.com  \n  https://test.com  ';
      expect(parseUrls(text)).toEqual(['https://example.com', 'https://test.com']);
    });

    it('should filter empty lines', () => {
      const text = 'https://example.com\n\n\nhttps://test.com';
      expect(parseUrls(text)).toEqual(['https://example.com', 'https://test.com']);
    });
  });

  describe('validateUrls', () => {
    it('should separate valid and invalid URLs', () => {
      const urls = ['https://example.com', 'invalid', 'http://test.com'];
      const result = validateUrls(urls);
      expect(result.valid).toEqual(['https://example.com', 'http://test.com']);
      expect(result.invalid).toEqual(['invalid']);
    });
  });
});
