import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useTheme } from '@/contexts/theme-context';
import { formatNumber } from '@/lib/utils';
import { getChartColors } from '@/lib/chart-colors';

interface ChartData {
  [key: string]: { male: number; female: number; total?: number };
}

interface PeopleCountChartProps {
  data: ChartData;
  title?: string;
  period?: 'hourly' | 'daily' | 'weekly' | 'monthly';
  height?: number;
}

interface ChartEntry {
  name: string;
  male: number;
  female: number;
  total: number;
  originalKey: string;
}

export function PeopleCountChart({ 
  data, 
  title, 
  period = 'daily',
  height = 400 
}: PeopleCountChartProps) {
  const { actualTheme } = useTheme();
  const isDark = actualTheme === 'dark';
  const colors = getChartColors(isDark);

  // Transform data for Recharts
  const chartData = React.useMemo((): ChartEntry[] => {
    const entries = Object.entries(data || {}).map(([key, value]): ChartEntry => {
      // Format the date/time based on period
      let formattedKey = key;
      
      try {
        if (period === 'hourly') {
          // For hourly data, show hour like "09:00", "14:00"
          const hour = parseInt(key, 10);
          formattedKey = `${hour.toString().padStart(2, '0')}:00`;
        } else if (period === 'daily') {
          // For daily data, format as "Mar 15"
          const date = new Date(key);
          if (!isNaN(date.getTime())) {
            formattedKey = date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            });
          }
        } else {
          // Keep original format for other periods
          formattedKey = key;
        }
      } catch (error) {
        console.warn('Error formatting chart key:', key, error);
      }

      return {
        name: formattedKey,
        male: value.male || 0,
        female: value.female || 0,
        total: value.total !== undefined ? value.total : (value.male || 0) + (value.female || 0),
        originalKey: key,
      };
    });

    // Sort entries based on period
    return entries.sort((a, b) => {
      if (period === 'hourly') {
        const hourA = parseInt(a.originalKey, 10);
        const hourB = parseInt(b.originalKey, 10);
        return hourA - hourB;
      } else {
        const dateA = new Date(a.originalKey);
        const dateB = new Date(b.originalKey);
        return dateA.getTime() - dateB.getTime();
      }
    });
  }, [data, period]);

  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded-lg border bg-muted/30">
        <p className="text-muted-foreground">No data available</p>
      </div>
    );
  }

  return (
    <div className="w-full -mx-2">
      {title && (
        <h3 className="mb-4 text-lg font-semibold px-2">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{
            top: 10,
            right: 10,
            left: 10,
            bottom: 10,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis 
            dataKey="name" 
            tick={{ fontSize: 12, fill: colors.text }}
            tickLine={{ stroke: colors.text }}
            axisLine={{ stroke: colors.text }}
          />
          <YAxis 
            tick={{ fontSize: 12, fill: colors.text }}
            tickLine={{ stroke: colors.text }}
            axisLine={{ stroke: colors.text }}
            tickFormatter={formatNumber}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: colors.background,
              border: `1px solid ${colors.grid}`,
              borderRadius: '6px',
              color: colors.text,
            }}
            formatter={(value: number, name: string) => [
              formatNumber(value),
              name === 'male' ? 'Male' : name === 'female' ? 'Female' : name
            ]}
            labelStyle={{ color: colors.text }}
          />
          <Legend 
            wrapperStyle={{ color: colors.text }}
            formatter={(value) => (
              <span style={{ color: colors.text }}>
                {value === 'male' ? 'Male' : value === 'female' ? 'Female' : value}
              </span>
            )}
          />
          <Bar 
            dataKey="male" 
            stackId="stack" 
            fill={colors.male}
            name="male"
            radius={[0, 0, 0, 0]}
          />
          <Bar 
            dataKey="female" 
            stackId="stack" 
            fill={colors.female}
            name="female"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
