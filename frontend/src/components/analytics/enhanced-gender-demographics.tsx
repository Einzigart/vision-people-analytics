import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Users, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  Area,
  AreaChart,
} from 'recharts';
import { useTheme } from '@/contexts/theme-context';

interface EnhancedGenderDemographicsProps {
  startDate: Date;
  endDate: Date;
  data: Record<string, { male: number; female: number; total: number }>;
  type: 'hourly' | 'daily' | 'weekly' | 'monthly';
}

interface GenderTrendData {
  period: string;
  male: number;
  female: number;
  total: number;
  malePercentage: number;
  femalePercentage: number;
  originalKey?: string;
}

const EnhancedGenderDemographics = ({ data, type }: EnhancedGenderDemographicsProps) => {
  const { actualTheme } = useTheme();
  const isDark = actualTheme === 'dark';
  const [loading] = useState(false);
  const [chartType, setChartType] = useState<'bar' | 'area' | 'pie'>('bar');
  const [showPercentages, setShowPercentages] = useState(false);

  // Check if we're on mobile
  const isMobile = useMemo(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < 640; // sm breakpoint
    }
    return false;
  }, []);

  // Get CSS custom properties for consistent theming
  const getCustomProperty = (property: string) => {
    if (typeof window !== 'undefined') {
      return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    }
    return '';
  };

  // Use consistent colors from theme
  const colors = {
    male: getCustomProperty('--chart-1') || '#3b82f6',
    female: getCustomProperty('--chart-2') || '#ec4899',
    grid: getCustomProperty('--border') || (isDark ? '#374151' : '#e5e7eb'),
    text: getCustomProperty('--foreground') || (isDark ? '#e5e7eb' : '#374151'),
  };

  // Process data for charts and sort by period
  const processedData: GenderTrendData[] = Object.entries(data)
    .map(([key, value]) => {
      const total = value.total || (value.male + value.female);
      return {
        period: formatPeriodLabel(key, type),
        originalKey: key, // Store original key for sorting
        male: value.male,
        female: value.female,
        total,
        malePercentage: total > 0 ? (value.male / total) * 100 : 0,
        femalePercentage: total > 0 ? (value.female / total) * 100 : 0,
      };
    })
    .sort((a, b) => {
      // For monthly data, sort by date
      if (type === 'monthly') {
        return new Date(a.originalKey).getTime() - new Date(b.originalKey).getTime();
      }
      return 0;
    });

  // Calculate overall statistics
  const totalStats = processedData.reduce(
    (acc, curr) => ({
      male: acc.male + curr.male,
      female: acc.female + curr.female,
      total: acc.total + curr.total,
    }),
    { male: 0, female: 0, total: 0 }
  );

  // Calculate averages based on the number of periods
  const periodCount = processedData.length || 1;
  const averageStats = {
    total: totalStats.total / periodCount,
    male: totalStats.male / periodCount,
    female: totalStats.female / periodCount,
  };

  const overallMalePercentage = totalStats.total > 0 ? (totalStats.male / totalStats.total) * 100 : 0;
  const overallFemalePercentage = totalStats.total > 0 ? (totalStats.female / totalStats.total) * 100 : 0;

  // Get time period label for display
  const getTimePeriodLabel = (type: string) => {
    switch (type) {
      case 'hourly': return 'per hour';
      case 'daily': return 'per day';
      case 'weekly': return 'per week';
      case 'monthly': return 'per month';
      default: return 'per period';
    }
  };

  // Calculate trends
  const firstHalf = processedData.slice(0, Math.floor(processedData.length / 2));
  const secondHalf = processedData.slice(Math.floor(processedData.length / 2));

  const firstHalfStats = firstHalf.reduce((acc, curr) => ({
    male: acc.male + curr.male,
    female: acc.female + curr.female,
    total: acc.total + curr.total,
  }), { male: 0, female: 0, total: 0 });

  const secondHalfStats = secondHalf.reduce((acc, curr) => ({
    male: acc.male + curr.male,
    female: acc.female + curr.female,
    total: acc.total + curr.total,
  }), { male: 0, female: 0, total: 0 });

  const maleTrend = firstHalfStats.total > 0 && secondHalfStats.total > 0 
    ? (secondHalfStats.male / secondHalfStats.total) - (firstHalfStats.male / firstHalfStats.total)
    : 0;

  const femaleTrend = firstHalfStats.total > 0 && secondHalfStats.total > 0 
    ? (secondHalfStats.female / secondHalfStats.total) - (firstHalfStats.female / firstHalfStats.total)
    : 0;

  // Pie chart data
  const pieData = [
    { name: 'Male', value: totalStats.male, color: colors.male },
    { name: 'Female', value: totalStats.female, color: colors.female },
  ];

  function formatPeriodLabel(key: string, type: string): string {
    switch (type) {
      case 'hourly':
        return `${key.padStart(2, '0')}:00`;
      case 'daily':
        return new Date(key).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      case 'weekly':
        return `Week ${key}`;
      case 'monthly':
        return new Date(key).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      default:
        return key;
    }
  }

  const getTrendIcon = (trend: number) => {
    if (trend > 0.02) return <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-green-500" />;
    if (trend < -0.02) return <TrendingDown className="h-3 w-3 sm:h-4 sm:w-4 text-red-500" />;
    return <Minus className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500" />;
  };

  const getTrendText = (trend: number) => {
    if (trend > 0.02) return `+${(trend * 100).toFixed(1)}%`;
    if (trend < -0.02) return `${(trend * 100).toFixed(1)}%`;
    return 'Stable';
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border border-border rounded-lg p-2 sm:p-3 shadow-lg text-xs sm:text-sm">
          <p className="font-medium text-foreground">{`Period: ${label}`}</p>
          <p style={{ color: colors.male }}>
            {`Male: ${data.male} (${data.malePercentage.toFixed(1)}%)`}
          </p>
          <p style={{ color: colors.female }}>
            {`Female: ${data.female} (${data.femalePercentage.toFixed(1)}%)`}
          </p>
          <p className="text-xs text-muted-foreground">
            {`Total: ${data.total}`}
          </p>
        </div>
      );
    }
    return null;
  };

  const PieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = totalStats.total > 0 ? (data.value / totalStats.total) * 100 : 0;
      return (
        <div className="bg-background border border-border rounded-lg p-2 sm:p-3 shadow-lg text-xs sm:text-sm">
          <p className="font-medium text-foreground">{`${data.name}: ${data.value}`}</p>
          <p className="text-xs text-muted-foreground">{`${percentage.toFixed(1)}%`}</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-48 sm:h-64">
          <Loader2 className="h-6 w-6 sm:h-8 sm:w-8 animate-spin" />
          <span className="ml-2 text-sm sm:text-base">Loading gender demographics...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Average Total</CardTitle>
            <Users className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg sm:text-2xl font-bold">{averageStats.total.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              {getTimePeriodLabel(type)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Average Male</CardTitle>
            <div className="flex items-center space-x-1">
              {getTrendIcon(maleTrend)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-lg sm:text-2xl font-bold" style={{ color: colors.male }}>
              {averageStats.male.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              {overallMalePercentage.toFixed(1)}% • {getTrendText(maleTrend)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Average Female</CardTitle>
            <div className="flex items-center space-x-1">
              {getTrendIcon(femaleTrend)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-lg sm:text-2xl font-bold" style={{ color: colors.female }}>
              {averageStats.female.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              {overallFemalePercentage.toFixed(1)}% • {getTrendText(femaleTrend)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Gender Ratio</CardTitle>
            <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg sm:text-2xl font-bold">
              {totalStats.female > 0 ? (totalStats.male / totalStats.female).toFixed(2) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Male to Female ratio
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Chart Controls */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <CardTitle className="text-base sm:text-lg">Gender Distribution Over Time</CardTitle>
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
              <div className="flex items-center space-x-1">
                <Button
                  variant={chartType === 'bar' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setChartType('bar')}
                  className="text-xs sm:text-sm"
                >
                  Bar
                </Button>
                <Button
                  variant={chartType === 'area' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setChartType('area')}
                  className="text-xs sm:text-sm"
                >
                  Area
                </Button>
                <Button
                  variant={chartType === 'pie' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setChartType('pie')}
                  className="text-xs sm:text-sm"
                >
                  Pie
                </Button>
              </div>
              {chartType !== 'pie' && (
                <Button
                  variant={showPercentages ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setShowPercentages(!showPercentages)}
                  className="text-xs sm:text-sm w-full sm:w-auto"
                >
                  {showPercentages ? 'Count' : 'Percentage'}
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={isMobile ? 300 : 400}>
            {chartType === 'bar' ? (
              <BarChart 
                data={processedData}
                margin={{
                  top: 10,
                  right: isMobile ? 5 : 10,
                  left: isMobile ? 5 : 10,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
                <XAxis 
                  dataKey="period" 
                  stroke={colors.text}
                  fontSize={isMobile ? 10 : 12}
                  tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                  angle={isMobile ? -45 : 0}
                  textAnchor={isMobile ? 'end' : 'middle'}
                  height={isMobile ? 60 : 40}
                />
                <YAxis 
                  stroke={colors.text}
                  fontSize={isMobile ? 10 : 12}
                  tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                  width={isMobile ? 40 : 50}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  wrapperStyle={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}
                  formatter={(value) => (
                    <span style={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}>
                      {value}
                    </span>
                  )}
                />
                <Bar 
                  dataKey={showPercentages ? "malePercentage" : "male"} 
                  fill={colors.male} 
                  name="Male" 
                />
                <Bar 
                  dataKey={showPercentages ? "femalePercentage" : "female"} 
                  fill={colors.female} 
                  name="Female" 
                />
              </BarChart>
            ) : chartType === 'area' ? (
              <AreaChart 
                data={processedData}
                margin={{
                  top: 10,
                  right: isMobile ? 5 : 10,
                  left: isMobile ? 5 : 10,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
                <XAxis 
                  dataKey="period" 
                  stroke={colors.text}
                  fontSize={isMobile ? 10 : 12}
                  tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                  angle={isMobile ? -45 : 0}
                  textAnchor={isMobile ? 'end' : 'middle'}
                  height={isMobile ? 60 : 40}
                />
                <YAxis 
                  stroke={colors.text}
                  fontSize={isMobile ? 10 : 12}
                  tick={{ fontSize: isMobile ? 10 : 12, fill: colors.text }}
                  width={isMobile ? 40 : 50}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  wrapperStyle={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}
                  formatter={(value) => (
                    <span style={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}>
                      {value}
                    </span>
                  )}
                />
                <Area
                  type="monotone"
                  dataKey={showPercentages ? "malePercentage" : "male"}
                  stackId="1"
                  stroke={colors.male}
                  fill={colors.male}
                  name="Male"
                />
                <Area
                  type="monotone"
                  dataKey={showPercentages ? "femalePercentage" : "female"}
                  stackId="1"
                  stroke={colors.female}
                  fill={colors.female}
                  name="Female"
                />
              </AreaChart>
            ) : (
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={isMobile ? 80 : 120}
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
                        fontSize={isMobile ? 10 : 12}
                        fontWeight="bold"
                      >
                        {`${(percent * 100).toFixed(1)}%`}
                      </text>
                    );
                  }}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
                <Legend 
                  wrapperStyle={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}
                  formatter={(value) => (
                    <span style={{ color: colors.text, fontSize: isMobile ? '12px' : '14px' }}>
                      {value}
                    </span>
                  )}
                />
              </PieChart>
            )}
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Period-by-Period Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">Detailed Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-48 sm:max-h-64 overflow-y-auto">
            {processedData.map((item, index) => (
              <div key={index} className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0 p-2 sm:p-3 border rounded-lg">
                <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-4">
                  <div className="font-medium text-sm sm:text-base min-w-[80px]">{item.period}</div>
                  <div className="flex items-center space-x-2 sm:space-x-4">
                    <Badge variant="outline" className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs">
                      M: {item.male}
                    </Badge>
                    <Badge variant="outline" className="bg-pink-50 dark:bg-pink-900/20 text-pink-700 dark:text-pink-300 text-xs">
                      F: {item.female}
                    </Badge>
                  </div>
                </div>
                <div className="flex flex-col space-y-1 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-4 text-xs sm:text-sm text-muted-foreground">
                  <div className="flex items-center space-x-2 sm:space-x-0 sm:block">
                    <span>Male: {item.malePercentage.toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center space-x-2 sm:space-x-0 sm:block">
                    <span>Female: {item.femalePercentage.toFixed(1)}%</span>
                  </div>
                  <div className="font-medium">
                    Total: {item.total}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedGenderDemographics;
