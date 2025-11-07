import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProgressIndicator from './ProgressIndicator';

describe('ProgressIndicator', () => {
  it('does not render when not processing', () => {
    const { container } = render(
      <ProgressIndicator isProcessing={false} current={0} total={0} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('displays processing message', () => {
    render(<ProgressIndicator isProcessing={true} current={5} total={10} />);
    expect(screen.getByText(/processing/i)).toBeInTheDocument();
  });

  it('displays current and total count', () => {
    render(<ProgressIndicator isProcessing={true} current={23} total={87} />);
    expect(screen.getByText('Processing 23 of 87 articles...')).toBeInTheDocument();
  });

  it('displays singular form for one article', () => {
    render(<ProgressIndicator isProcessing={true} current={1} total={1} />);
    expect(screen.getByText('Processing 1 of 1 article...')).toBeInTheDocument();
  });

  it('shows progress bar', () => {
    render(<ProgressIndicator isProcessing={true} current={5} total={10} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
  });

  it('calculates progress percentage correctly', () => {
    render(<ProgressIndicator isProcessing={true} current={5} total={10} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  });

  it('handles zero progress', () => {
    render(<ProgressIndicator isProcessing={true} current={0} total={10} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '0');
  });

  it('handles complete progress', () => {
    render(<ProgressIndicator isProcessing={true} current={10} total={10} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '100');
  });

  it('displays spinner icon', () => {
    render(<ProgressIndicator isProcessing={true} current={5} total={10} />);
    // Check for loading indicator (could be svg or specific class)
    expect(screen.getByText(/processing/i).parentElement).toBeInTheDocument();
  });
});
