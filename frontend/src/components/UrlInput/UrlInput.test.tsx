import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UrlInput from './UrlInput';

describe('UrlInput', () => {
  it('renders textarea', () => {
    render(<UrlInput value="" onChange={vi.fn()} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeInTheDocument();
  });

  it('displays placeholder text', () => {
    render(<UrlInput value="" onChange={vi.fn()} />);
    const textarea = screen.getByPlaceholderText(/paste article urls/i);
    expect(textarea).toBeInTheDocument();
  });

  it('calls onChange when text is entered', async () => {
    const handleChange = vi.fn();
    const user = userEvent.setup();

    render(<UrlInput value="" onChange={handleChange} />);
    const textarea = screen.getByRole('textbox');

    await user.type(textarea, 'https://example.com');

    expect(handleChange).toHaveBeenCalled();
  });

  it('displays current value', () => {
    const value = 'https://example.com\nhttps://test.com';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
    expect(textarea.value).toBe(value);
  });

  it('displays URL count when URLs are present', () => {
    const value = 'https://example.com\nhttps://test.com';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.getByText('2 valid URLs detected')).toBeInTheDocument();
  });

  it('displays singular form for one URL', () => {
    const value = 'https://example.com';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.getByText('1 valid URL detected')).toBeInTheDocument();
  });

  it('does not display count when no valid URLs', () => {
    const value = 'invalid text';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.queryByText(/valid URLs? detected/i)).not.toBeInTheDocument();
  });

  it('displays invalid URL count', () => {
    const value = 'https://example.com\ninvalid-url\nhttps://test.com';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.getByText('2 valid URLs detected')).toBeInTheDocument();
    expect(screen.getByText('1 invalid URL')).toBeInTheDocument();
  });

  it('handles empty lines', () => {
    const value = 'https://example.com\n\n\nhttps://test.com';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.getByText('2 valid URLs detected')).toBeInTheDocument();
  });

  it('trims whitespace from URLs', () => {
    const value = '  https://example.com  \n  https://test.com  ';
    render(<UrlInput value={value} onChange={vi.fn()} />);

    expect(screen.getByText('2 valid URLs detected')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    render(<UrlInput value="" onChange={vi.fn()} disabled={true} />);

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeDisabled();
  });

  it('has clear button when value is not empty', () => {
    render(<UrlInput value="https://example.com" onChange={vi.fn()} />);

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('calls onChange with empty string when clear is clicked', async () => {
    const handleChange = vi.fn();
    const user = userEvent.setup();

    render(<UrlInput value="https://example.com" onChange={handleChange} />);

    const clearButton = screen.getByRole('button', { name: /clear/i });
    await user.click(clearButton);

    expect(handleChange).toHaveBeenCalledWith('');
  });

  it('does not show clear button when empty', () => {
    render(<UrlInput value="" onChange={vi.fn()} />);

    expect(screen.queryByRole('button', { name: /clear/i })).not.toBeInTheDocument();
  });
});
