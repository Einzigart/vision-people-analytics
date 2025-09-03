import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { useTheme } from '@/contexts/theme-context';
import { getChartColors, ageGroups } from '@/lib/chart-colors';
import { Demographics, calculateDemographicsTotal } from '@/services/api';

interface AgeDistributionChartProps {
  demographics: Demographics;
  height?: number;
}

interface ChartData {
  name: string;
  value: number;
  percentage: number;
  color: string;
}

export function AgeDistributionChart({ 
  demographics, 
  height = 350 
}: AgeDistributionChartProps) {
  const { actualTheme } = useTheme();
  const isDark = actualTheme === 'dark';
  const colors = getChartColors(isDark);

  // Transform demographics data for chart
  const chartData: ChartData[] = React.useMemo(() => {
    const total = calculateDemographicsTotal(demographics);
    
    if (total === 0) {
      return [];
    }

    return ageGroups.map((ageGroup, index) => {
      const maleCount = demographics.male[ageGroup] || 0;
      const femaleCount = demographics.female[ageGroup] || 0;
      const ageGroupTotal = maleCount + femaleCount;
      const percentage = (ageGroupTotal / total) * 100;

      return {
        name: ageGroup,
        value: ageGroupTotal,
        percentage: percentage,
        color: colors.ageColors[index],
      };
    }).filter(item => item.value > 0); // Only show age groups with data
  }, [demographics, colors.ageColors]);

  const total = calculateDemographicsTotal(demographics);

  if (total === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded-lg border bg-muted/30">
        <p className="text-muted-foreground">No age distribution data available</p>
      </div>
    );
  }

  const PieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background p-3 border border-border rounded-lg shadow-lg">
          <p className="font-medium text-foreground">{`${data.name}: ${data.value}`}</p>
          <p className="text-sm text-muted-foreground">{`${data.percentage.toFixed(1)}%`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={Math.min(height * 0.35, 80)}
            fill="#8884d8"
            dataKey="value"
            stroke="none"
            labelLine={false}
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
              const labelRadius = innerRadius + (outerRadius - innerRadius) * 0.6;
              const x = cx + labelRadius * Math.cos(-midAngle * RADIAN);
              const y = cy + labelRadius * Math.sin(-midAngle * RADIAN);

              if (percent < 0.05) return null;

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
          <Tooltip content={<PieTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
