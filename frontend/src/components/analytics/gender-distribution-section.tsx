import React, { forwardRef } from 'react';
import { Card } from '../ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useTheme } from '@/contexts/theme-context';

interface GenderDistributionSectionProps {
  male: number;
  female: number;
}

const GenderDistributionSection = forwardRef<HTMLDivElement, GenderDistributionSectionProps>(
  ({ male, female }, ref) => {
    const { actualTheme } = useTheme();
    const isDark = actualTheme === 'dark';

    // Get CSS custom properties for consistent theming
    const getCustomProperty = (property: string) => {
      if (typeof window !== 'undefined') {
        return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
      }
      return '';
    };

    // Use consistent colors across all charts
    const colors = {
      male: getCustomProperty('--chart-1') || '#3b82f6',
      female: getCustomProperty('--chart-2') || '#ec4899',
      text: getCustomProperty('--foreground') || (isDark ? '#e5e7eb' : '#374151'),
    };

    const total = male + female;
    
    const data = [
      { name: 'Male', value: male, color: colors.male },
      { name: 'Female', value: female, color: colors.female },
    ];

    // Check if we're on mobile
    const isMobile = React.useMemo(() => {
      if (typeof window !== 'undefined') {
        return window.innerWidth < 640; // sm breakpoint
      }
      return false;
    }, []);

    const CustomTooltip = ({ active, payload }: any) => {
      if (active && payload && payload.length) {
        const data = payload[0];
        const percentage = total > 0 ? Math.round((data.value / total) * 100) : 0;
        return (
          <div className="bg-background border border-border rounded-lg p-2 sm:p-3 shadow-lg text-xs sm:text-sm">
            <p className="font-medium text-foreground">{data.name}</p>
            <p className="text-muted-foreground">Count: {data.value}</p>
            <p className="text-muted-foreground">Percentage: {percentage}%</p>
          </div>
        );
      }
      return null;
    };

    const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
      const RADIAN = Math.PI / 180;
      const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
      const x = cx + radius * Math.cos(-midAngle * RADIAN);
      const y = cy + radius * Math.sin(-midAngle * RADIAN);

      if (percent < 0.05) return null; // Don't show label if slice is too small

      return (
        <text 
          x={x} 
          y={y} 
          fill="white" 
          textAnchor="middle" 
          dominantBaseline="central"
          fontSize={isMobile ? 10 : 12}
          fontWeight="bold"
        >
          {`${(percent * 100).toFixed(1)}%`}
        </text>
      );
    };

    if (total === 0) {
      return (
        <div ref={ref} className="h-full min-h-[300px] sm:min-h-[400px]">
          <Card className="p-4 sm:p-6 h-full flex flex-col">
            <h3 className="text-base sm:text-lg font-medium mb-4 text-foreground">Gender Distribution</h3>
            <div className="flex-grow flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <p className="text-base sm:text-lg mb-2">No Data Available</p>
                <p className="text-xs sm:text-sm">No people detected in the selected time range</p>
              </div>
            </div>
          </Card>
        </div>
      );
    }

    return (
      <div ref={ref} className="h-full min-h-[300px] sm:min-h-[400px]">
        <Card className="p-4 sm:p-6 h-full flex flex-col">
          <h3 className="text-base sm:text-lg font-medium mb-4 text-foreground">Gender Distribution</h3>
          {/* Fixed chart height so summary never overlaps bottom padding */}
          <div className="h-[200px] sm:h-[260px] xl:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={CustomLabel}
                  outerRadius={isMobile ? 60 : 80}
                  fill={getCustomProperty('--chart-1') || '#8884d8'}
                  dataKey="value"
                  stroke="none"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  verticalAlign="bottom" 
                  height={isMobile ? 24 : 36}
                  wrapperStyle={{ 
                    color: colors.text, 
                    fontSize: isMobile ? '12px' : '14px' 
                  }}
                  formatter={(value, entry: any) => (
                    <span style={{ 
                      color: colors.text, 
                      fontWeight: 'medium',
                      fontSize: isMobile ? '12px' : '14px'
                    }}>
                      {value}: {entry.payload.value} ({total > 0 ? Math.round((entry.payload.value / total) * 100) : 0}%)
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Summary Stats Below Chart */}
          <div className="mt-3 sm:mt-4 grid grid-cols-2 gap-2 sm:gap-4">
            <div className="text-center p-2 sm:p-3 bg-muted/30 rounded-lg border border-border">
              <p className="text-xs sm:text-sm text-muted-foreground mb-1">Male</p>
              <p className="text-lg sm:text-2xl font-bold" style={{ color: colors.male }}>{male}</p>
              <p className="text-xs" style={{ color: colors.male }}>
                {total > 0 ? Math.round((male / total) * 100) : 0}%
              </p>
            </div>
            <div className="text-center p-2 sm:p-3 bg-muted/30 rounded-lg border border-border">
              <p className="text-xs sm:text-sm text-muted-foreground mb-1">Female</p>
              <p className="text-lg sm:text-2xl font-bold" style={{ color: colors.female }}>{female}</p>
              <p className="text-xs" style={{ color: colors.female }}>
                {total > 0 ? Math.round((female / total) * 100) : 0}%
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }
);

GenderDistributionSection.displayName = 'GenderDistributionSection';

export default GenderDistributionSection;
