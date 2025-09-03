import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { useTheme } from '@/contexts/theme-context';
import { formatNumber, formatPercentage } from '@/lib/utils';

interface GenderData {
  male: number;
  female: number;
}

interface GenderDistributionChartProps {
  data: GenderData;
  title?: string;
  height?: number;
}

export function GenderDistributionChart({
  data,
  title,
  height = 300
}: GenderDistributionChartProps) {
  const { actualTheme } = useTheme();
  const isDark = actualTheme === 'dark';

  // Get CSS custom properties for consistent theming
  const getCustomProperty = (property: string) => {
    if (typeof window !== 'undefined') {
      return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    }
    return '';
  };

  const chartData = React.useMemo(() => {
    const total = (data?.male || 0) + (data?.female || 0);

    if (total === 0) {
      return [];
    }

    return [
      {
        name: 'Male',
        value: data.male || 0,
        percentage: formatPercentage(data.male || 0, total),
        color: getCustomProperty('--chart-1') || '#3b82f6',
      },
      {
        name: 'Female',
        value: data.female || 0,
        percentage: formatPercentage(data.female || 0, total),
        color: getCustomProperty('--chart-2') || '#ec4899',
      },
    ];
  }, [data]);

  const colors = {
    text: getCustomProperty('--foreground') || (isDark ? '#e5e7eb' : '#374151'),
  };

  if (!data || (data.male === 0 && data.female === 0)) {
    return (
      <div className="flex h-60 items-center justify-center rounded-lg border bg-muted/30">
        <p className="text-muted-foreground">No gender data available</p>
      </div>
    );
  }
  
  return (
    <div className="w-full">
      {title && (
        <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      )}
      <div style={{ width: '100%', height: height }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={0} // Removed hole in pie chart
              outerRadius={100}
              paddingAngle={0} // Removed padding angle for a cleaner look
              dataKey="value"
              labelLine={false}
              stroke="none"
              label={({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
                if (
                  percent === undefined ||
                  midAngle === undefined ||
                  cx === undefined ||
                  cy === undefined ||
                  innerRadius === undefined ||
                  outerRadius === undefined
                ) return null;

                const RADIAN = Math.PI / 180;
                // Increase label distance to prevent overlap with arrow lines
                const labelRadius = innerRadius + (outerRadius - innerRadius) * 0.6;
                const x = cx + labelRadius * Math.cos(-midAngle * RADIAN);
                const y = cy + labelRadius * Math.sin(-midAngle * RADIAN);

                if (percent < 0.05) return null; // Don't show label if slice is too small

                return (
                  <text 
                    x={x} 
                    y={y} 
                    fill="white" 
                    textAnchor="middle" 
                    dominantBaseline="central"
                    fontSize={12}
                    fontWeight="bold"
                  >
                    {`${(percent * 100).toFixed(1)}%`}
                  </text>
                );
              }}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0];
                  return (
                    <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                      <p className="font-medium text-foreground">{data.name}</p>
                      <p className="text-muted-foreground">Count: {data.value}</p>
                      <p className="text-muted-foreground">Percentage: {data.payload.percentage}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend 
              wrapperStyle={{ color: colors.text }}
              formatter={(value, entry: any) => (
                <span style={{ color: colors.text }}>
                  {value}: {formatNumber(entry.payload.value)} ({entry.payload.percentage})
                </span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      {/* Summary statistics */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
        <div className="rounded-lg bg-muted/30 p-3">
          <div className="text-lg font-semibold text-primary">
            {formatNumber(data.male || 0)}
          </div>
          <div className="text-sm text-muted-foreground">Male</div>
        </div>
        <div className="rounded-lg bg-muted/30 p-3">
          <div className="text-lg font-semibold text-secondary-foreground">
            {formatNumber(data.female || 0)}
          </div>
          <div className="text-sm text-muted-foreground">Female</div>
        </div>
      </div>
    </div>
  );
}
