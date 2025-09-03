import React, { forwardRef } from 'react';
import { Card } from '../ui/card';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { format, parseISO, addDays, differenceInDays, addMonths, startOfMonth, isAfter } from 'date-fns';
import { useTheme } from '@/contexts/theme-context';
import { formatNumber } from '@/lib/utils';
import { getChartColors } from '@/lib/chart-colors';
 
// Local error boundary to catch chart render errors and show a friendly fallback.
// This prevents an entire page crash when Recharts encounters unexpected input.
class ChartErrorBoundary extends React.Component<any, { hasError: boolean }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, info: any) {
    // Log to console for diagnostics
    console.error('Chart render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-full min-h-[300px] sm:min-h-[400px] flex items-center justify-center">
          <Card className="p-4 sm:p-6 h-full flex flex-col">
            <h3 className="text-base sm:text-lg font-semibold mb-4">People Count Over Time</h3>
            <div className="flex-grow flex items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground text-sm">Unable to render chart for the selected period</p>
              </div>
            </div>
          </Card>
        </div>
      );
    }
    // @ts-ignore - children are valid
    return this.props.children;
  }
}

interface PeopleCountSectionProps {
  data: Record<string, { male: number; female: number; total: number }>;
  type: 'hourly' | 'daily' | 'weekly' | 'monthly';
  startDate?: Date;
  endDate?: Date;
}

const PeopleCountSection = forwardRef<HTMLDivElement, PeopleCountSectionProps>(
  ({ data, type, startDate, endDate }, ref) => {
    const { actualTheme } = useTheme();
    const isDark = actualTheme === 'dark';
    const colors = getChartColors(isDark);

    // Determine if we should force hourly display based on data
    // Only treat the dataset as hourly when the data keys actually look like hour indices.
    // This avoids switching to 'hourly' view prematurely while the backend is still
    // returning the previous multi-day payload.
    const shouldShowHourly = React.useMemo(() => {
      // If no data, return false
      if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
        return false;
      }

      const keys = Object.keys(data);

      // Check if all keys are numeric (hours 0-23) which indicates hourly data
      const isHourlyData = keys.every(key => {
        const num = parseInt(key, 10);
        return !isNaN(num) && num >= 0 && num <= 23;
      });

      // Also require we have <= 24 points to be considered hourly
      const hasHourlyCount = keys.length <= 24;

      // Only treat as hourly when the data itself appears hourly.
      // Do not rely solely on the incoming `type` prop because the parent may
      // set type='hourly' before the hourly payload has arrived.
      return isHourlyData && hasHourlyCount;
    }, [data]);

    const actualType = React.useMemo(() => {
      // Prevent switching to hourly view unless the data actually looks hourly.
      // If the parent sets type='hourly' optimistically but the payload is still
      // the previous multi-day data, fall back to 'daily' to avoid chart errors.
      if (type === 'hourly' && !shouldShowHourly) {
        return 'daily';
      }
      return shouldShowHourly ? 'hourly' : type;
    }, [type, shouldShowHourly]);

    // Sort data by original key to ensure chronological order
    const sortedEntries = React.useMemo(() => {
      if (!data || typeof data !== 'object') {
        return [];
      }

      return Object.entries(data).sort(([a], [b]) => {
        try {
          // For hourly data, sort by hour number
          if (actualType === 'hourly') {
            const hourA = parseInt(a, 10);
            const hourB = parseInt(b, 10);
            if (!isNaN(hourA) && !isNaN(hourB)) {
              return hourA - hourB;
            }
          }
          // Try to parse as dates for proper sorting
          const dateA = new Date(a);
          const dateB = new Date(b);
          if (!isNaN(dateA.getTime()) && !isNaN(dateB.getTime())) {
            return dateA.getTime() - dateB.getTime();
          }
        } catch (error) {
          console.warn('Error sorting dates:', error);
        }
        // Fallback to string comparison
        return a.localeCompare(b);
      });
    }, [data, actualType]);

    const sortedChartData = React.useMemo(() => {
      return sortedEntries.map(([key, value]) => {
        let formattedKey = key;
        
        try {
          if (actualType === 'hourly') {
            // For hourly data, show hour like "09:00", "14:00"
            if (key.includes(':')) {
              if (key.includes('-')) {
                formattedKey = format(parseISO(key), 'HH:mm');
              } else {
                formattedKey = key;
              }
            } else {
              // If it's just a number (hour), format it
              const hour = parseInt(key, 10);
              if (!isNaN(hour)) {
                formattedKey = `${hour.toString().padStart(2, '0')}:00`;
              }
            }
          } else if (actualType === 'daily') {
            const parsedDate = parseISO(key);
            if (!isNaN(parsedDate.getTime())) {
              formattedKey = format(parsedDate, 'MMM dd');
            }
          } else if (actualType === 'weekly') {
            const parsedDate = parseISO(key);
            if (!isNaN(parsedDate.getTime())) {
              formattedKey = format(parsedDate, 'MMM dd');
            }
          } else if (actualType === 'monthly') {
            const parsedDate = parseISO(key);
            if (!isNaN(parsedDate.getTime())) {
              formattedKey = format(parsedDate, 'MMM yyyy');
            }
          }
        } catch (error) {
          console.warn('Error formatting date:', key, error);
          // Keep original key if formatting fails
        }

        // Ensure we have valid numbers
        const maleCount = typeof value.male === 'number' ? value.male : 0;
        const femaleCount = typeof value.female === 'number' ? value.female : 0;
        const totalCount = typeof value.total === 'number' ? value.total : maleCount + femaleCount;

        return {
          time: formattedKey,
          male: maleCount,
          female: femaleCount,
          total: totalCount,
        };
      });
    }, [sortedEntries, actualType]);

    const chartTitle = React.useMemo(() => {
      switch (actualType) {
        case 'hourly':
          return 'Hourly People Count';
        case 'daily':
          return 'Daily People Count';
        case 'weekly':
          return 'Weekly People Count';
        case 'monthly':
          return 'Monthly People Count';
        default:
          return 'People Count Over Time';
      }
    }, [actualType]);

    // Create a stable key for the chart to control animations
    const chartKey = React.useMemo(() => {
      const dataKeys = data ? Object.keys(data) : [];
      return `${actualType}-${dataKeys.length}-${JSON.stringify(dataKeys.slice(0, 3))}`;
    }, [actualType, data]);

    // Check if we're on mobile
    const isMobile = React.useMemo(() => {
      if (typeof window !== 'undefined') {
        return window.innerWidth < 640; // sm breakpoint
      }
      return false;
    }, []);

    // Build fallback chart data when input is empty or sums to zero
    const needsFallback = !data || typeof data !== 'object' || Object.keys(data).length === 0;
    const totalSum = needsFallback
      ? 0
      : Object.values(data).reduce((sum, v: any) => {
          const male = typeof v?.male === 'number' ? v.male : 0;
          const female = typeof v?.female === 'number' ? v.female : 0;
          const total = typeof v?.total === 'number' ? v.total : male + female;
          return sum + total;
        }, 0);

    const fallbackChartData: Array<{ time: string; male: number; female: number; total: number }> = React.useMemo(() => {
      // Generate minimal placeholder categories so the chart still renders
      if (actualType === 'hourly') {
        return Array.from({ length: 24 }, (_, h) => ({
          time: `${String(h).padStart(2, '0')}:00`, male: 0, female: 0, total: 0,
        }));
      }
      if (actualType === 'weekly') {
        return Array.from({ length: 4 }, (_, i) => ({ time: `Week ${i + 1}`, male: 0, female: 0, total: 0 }));
      }
      if (actualType === 'monthly') {
        // If we have a range, enumerate months inclusively
        if (startDate && endDate) {
          const months: Array<{ time: string; male: number; female: number; total: number }> = [];
          let cursor = startOfMonth(startDate);
          const endCursor = startOfMonth(endDate);
          let guard = 0;
          while (!isAfter(cursor, endCursor) && guard < 36) { // guard: max 3 years
            months.push({ time: format(cursor, 'MMM yyyy'), male: 0, female: 0, total: 0 });
            cursor = addMonths(cursor, 1);
            guard++;
          }
          if (months.length > 0) return months;
        }
        return Array.from({ length: 6 }, (_, i) => ({ time: `M${i + 1}`, male: 0, female: 0, total: 0 }));
      }
      // default daily: use date range if provided, otherwise 7 placeholder days
      if (startDate && endDate) {
        const days = Math.max(1, differenceInDays(endDate, startDate) + 1);
        const list: Array<{ time: string; male: number; female: number; total: number }> = [];
        for (let i = 0; i < Math.min(days, 62); i++) { // cap at ~2 months to avoid huge placeholders
          const d = addDays(startDate, i);
          list.push({ time: format(d, 'MMM dd'), male: 0, female: 0, total: 0 });
        }
        return list;
      }
      return Array.from({ length: 7 }, (_, i) => ({ time: `Day ${i + 1}`, male: 0, female: 0, total: 0 }));
    }, [actualType]);

    const CustomTooltip = ({ active, payload, label }: any) => {
      if (active && payload && payload.length) {
        return (
          <div 
            className="bg-background p-2 sm:p-3 border border-border rounded-lg shadow-lg text-xs sm:text-sm"
            style={{ 
              backgroundColor: colors.background,
              borderColor: colors.border,
              color: colors.text
            }}
          >
            <p className="font-medium text-foreground mb-1">
              {label}
            </p>
            {payload.map((entry: any, index: number) => (
              <p key={index} style={{ color: entry.color }}>
                {entry.name === 'male' ? 'Male' : 'Female'}: {formatNumber(entry.value)}
              </p>
            ))}
            <p className="text-xs text-muted-foreground mt-1">
              Total: {formatNumber(payload.reduce((sum: number, entry: any) => sum + entry.value, 0))}
            </p>
          </div>
        );
      }
      return null;
    };

    // Ensure chart data is safe: filter out malformed entries
    const filtered = sortedChartData.filter(d => d && typeof d.male === 'number' && typeof d.female === 'number' && typeof d.total === 'number');
    const safeChartData = (needsFallback || filtered.length === 0 || totalSum === 0) ? fallbackChartData : filtered;

    // Compute max value to avoid flat [0,0] Y domain
    const maxValue = safeChartData.reduce((m, d) => Math.max(m, (d.male + d.female)), 0);

    return (
      <div ref={ref} className="h-full min-h-[300px] sm:min-h-[400px]">
        <Card className="p-4 sm:p-6 h-full flex flex-col">
          <h3 className="text-base sm:text-lg font-semibold mb-4">{chartTitle}</h3>
          <div className="flex-grow min-h-[250px] sm:min-h-[300px] -mx-1 sm:-mx-2">
            <ChartErrorBoundary>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={safeChartData}
                  key={chartKey}
                  margin={{
                    top: 10,
                    right: isMobile ? 5 : 10,
                    left: isMobile ? 5 : 10,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
                  <XAxis 
                    dataKey="time" 
                    stroke={colors.text}
                    fontSize={isMobile ? 10 : 12}
                    tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                    tickLine={{ stroke: colors.text }}
                    axisLine={{ stroke: colors.text }}
                    angle={isMobile ? -45 : 0}
                    textAnchor={isMobile ? 'end' : 'middle'}
                    height={isMobile ? 60 : 40}
                  />
                <YAxis 
                  stroke={colors.text} 
                  fontSize={isMobile ? 10 : 12} 
                  tickFormatter={formatNumber}
                  tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                  tickLine={{ stroke: colors.text }}
                  axisLine={{ stroke: colors.text }}
                  width={isMobile ? 40 : 50}
                  domain={[0, Math.max(1, maxValue)]}
                />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend 
                    wrapperStyle={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}
                    formatter={(value) => (
                      <span style={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}>
                        {value === 'male' ? 'Male' : 'Female'}
                      </span>
                    )}
                  />
                  <Bar 
                    dataKey="male" 
                    stackId="stack" 
                    fill={colors.male} 
                    name="male"
                    radius={[0, 0, 0, 0]}
                    animationDuration={200}
                    animationBegin={0}
                  />
                  <Bar 
                    dataKey="female" 
                    stackId="stack" 
                    fill={colors.female} 
                    name="female"
                    radius={[4, 4, 0, 0]}
                    animationDuration={200}
                    animationBegin={50}
                  />
                </BarChart>
              </ResponsiveContainer>
            </ChartErrorBoundary>
          </div>
        </Card>
      </div>
    );
  }
);

PeopleCountSection.displayName = 'PeopleCountSection';

export default PeopleCountSection;
