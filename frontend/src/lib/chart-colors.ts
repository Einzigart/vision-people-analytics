// Unified color scheme for charts across all components
export const getChartColors = (isDark: boolean) => {
  // Get CSS custom properties for consistent theming
  const getCustomProperty = (property: string) => {
    if (typeof window !== 'undefined') {
      return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    }
    return '';
  };

  return {
    // Primary brand colors for male/female using theme colors
    male: getCustomProperty('--chart-1') || '#3b82f6',
    female: getCustomProperty('--chart-2') || '#ec4899',

    // Chart colors using CSS custom properties
    chartColors: [
      getCustomProperty('--chart-1') || '#8884d8',
      getCustomProperty('--chart-2') || '#82ca9d',
      getCustomProperty('--chart-3') || '#ffc658',
      getCustomProperty('--chart-4') || '#ff7c7c',
      getCustomProperty('--chart-5') || '#8dd1e1',
      getCustomProperty('--chart-6') || '#e879f9',
      getCustomProperty('--chart-7') || '#c084fc',
    ],

    // Age group colors (matching analytics view exactly)
    ageColors: [
      getCustomProperty('--chart-1') || '#8884d8',  // Purple - 0-9
      getCustomProperty('--chart-2') || '#82ca9d',  // Green - 10-19
      getCustomProperty('--chart-3') || '#ffc658',  // Yellow - 20-29
      getCustomProperty('--chart-4') || '#ff7c7c',  // Red - 30-39
      getCustomProperty('--chart-5') || '#8dd1e1',  // Cyan - 40-49
      getCustomProperty('--chart-6') || '#e879f9',  // Bright purple/magenta - 50+
    ],

    // Theme-aware UI colors using CSS custom properties
    grid: getCustomProperty('--border') || (isDark ? '#374151' : '#e5e7eb'),
    text: getCustomProperty('--foreground') || (isDark ? '#e5e7eb' : '#374151'),
    background: getCustomProperty('--background') || (isDark ? '#1f2937' : '#ffffff'),
    border: getCustomProperty('--border') || (isDark ? '#4b5563' : '#d1d5db'),
    muted: getCustomProperty('--muted-foreground') || (isDark ? '#6b7280' : '#9ca3af'),

    // Background variants for cards using theme colors
    backgroundVariants: {
      primary: getCustomProperty('--primary') + (isDark ? '20' : '10'),
      secondary: getCustomProperty('--secondary') + (isDark ? '20' : '10'),
      accent: getCustomProperty('--accent') + (isDark ? '20' : '10'),
      muted: getCustomProperty('--muted') + (isDark ? '20' : '10'),
    }
  };
};

// Age group labels
export const ageGroups = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+'];

// Helper function to get age group color
export const getAgeGroupColor = (ageGroup: string, isDark: boolean) => {
  const colors = getChartColors(isDark);
  const index = ageGroups.indexOf(ageGroup);
  return index >= 0 ? colors.ageColors[index] : colors.male;
};
