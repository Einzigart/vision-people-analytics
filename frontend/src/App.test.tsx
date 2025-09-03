import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders Login page by default', () => {
    render(<App />);
    // The unauthenticated default route should render the Login page
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
  });
});
