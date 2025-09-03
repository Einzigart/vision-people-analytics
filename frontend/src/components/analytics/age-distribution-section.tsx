import { useState, useEffect, forwardRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Users, TrendingUp, Activity } from 'lucide-react';
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
} from 'recharts';
import apiService, { 
  Demographics, 
  AgeGroup, 
  AGE_GROUPS, 
  calculateDemographicsTotal, 
  getGenderPercentages 
} from '@/services/api';

interface AgeDistributionSectionProps {
  startDate: Date;
  endDate: Date;
}

interface AgeGroupData {
  ageGroup: string;
  male: number;
  female: number;
  total: number;
  percentage: number;
}

const AgeDistributionSection = forwardRef<HTMLDivElement, AgeDistributionSectionProps>(({
  startDate,
  endDate,
}, ref) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demographics, setDemographics] = useState<Demographics | null>(null);
  const [ageGroupData, setAgeGroupData] = useState<AgeGroupData[]>([]);

  // Get CSS custom properties for consistent theming
  const getCustomProperty = (property: string) => {
    if (typeof window !== 'undefined') {
      return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    }
    return '';
  };

  // Color palette for age groups using theme colors
  const AGE_GROUP_COLORS = [
    getCustomProperty('--chart-1') || '#8884d8', // 0-9
    getCustomProperty('--chart-2') || '#82ca9d', // 10-19
    getCustomProperty('--chart-3') || '#ffc658', // 20-29
    getCustomProperty('--chart-4') || '#ff7c7c', // 30-39
    getCustomProperty('--chart-5') || '#8dd1e1', // 40-49
    getCustomProperty('--chart-6') || '#e879f9', // 50+ - Bright purple/magenta
  ];


  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const apiResponse = await apiService.getAgeGenderDateRangeStats(startDate, endDate);
        
        // Handle different response structures based on data type
        if (apiResponse && typeof apiResponse === 'object') {
          let demographicsData: Demographics | null = null;
          
          // For hourly data, demographics are at the top level
          if (apiResponse.type === 'hourly' && apiResponse.demographics) {
            demographicsData = apiResponse.demographics;
          } 
          // For daily data, demographics are at the top level
          else if (apiResponse.type === 'daily' && apiResponse.demographics) {
            demographicsData = apiResponse.demographics;
          }
          // For monthly data, we need to aggregate demographics from each month
          else if (apiResponse.type === 'monthly' && apiResponse.data && typeof apiResponse.data === 'object') {
            const aggregatedDemographicsLocal: Demographics = { male: {}, female: {} };
            AGE_GROUPS.forEach(ageGroup => {
              aggregatedDemographicsLocal.male[ageGroup] = 0;
              aggregatedDemographicsLocal.female[ageGroup] = 0;
            });

            Object.values(apiResponse.data).forEach((periodData: any) => {
              if (periodData && periodData.demographics) {
                AGE_GROUPS.forEach(ageGroup => {
                  aggregatedDemographicsLocal.male[ageGroup] += periodData.demographics.male[ageGroup] || 0;
                  aggregatedDemographicsLocal.female[ageGroup] += periodData.demographics.female[ageGroup] || 0;
                });
              }
            });
            
            demographicsData = aggregatedDemographicsLocal;
          }
          // For daily data without top-level demographics (fallback), aggregate from the data periods
          else if (apiResponse.type === 'daily' && apiResponse.data && typeof apiResponse.data === 'object') {
            const aggregatedDemographicsLocal: Demographics = { male: {}, female: {} };
            AGE_GROUPS.forEach(ageGroup => {
              aggregatedDemographicsLocal.male[ageGroup] = 0;
              aggregatedDemographicsLocal.female[ageGroup] = 0;
            });

            Object.values(apiResponse.data).forEach((periodData: any) => {
              if (periodData && periodData.demographics) {
                AGE_GROUPS.forEach(ageGroup => {
                  aggregatedDemographicsLocal.male[ageGroup] += periodData.demographics.male[ageGroup] || 0;
                  aggregatedDemographicsLocal.female[ageGroup] += periodData.demographics.female[ageGroup] || 0;
                });
              }
            });
            
            demographicsData = aggregatedDemographicsLocal;
          }

          if (demographicsData) {
            setDemographics(demographicsData);

            const total = calculateDemographicsTotal(demographicsData);
            const chartData: AgeGroupData[] = AGE_GROUPS.map(ageGroup => {
              const maleCount = demographicsData!.male[ageGroup] || 0;
              const femaleCount = demographicsData!.female[ageGroup] || 0;
              const ageGroupTotal = maleCount + femaleCount;
              
              return {
                ageGroup,
                male: maleCount,
                female: femaleCount,
                total: ageGroupTotal,
                percentage: total > 0 ? (ageGroupTotal / total) * 100 : 0
              };
            });
            setAgeGroupData(chartData);
          } else {
            // No demographics data available
            setAgeGroupData([]);
          }
        } else {
          // Invalid API response
          setAgeGroupData([]);
        }
      } catch (err) {
        console.error('Error fetching age-gender data:', err);
        setError('Failed to load age distribution data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading age distribution data...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
            <p className="text-destructive">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!demographics) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="bg-muted/50 border border-border rounded-md p-4">
            <p className="text-muted-foreground">No age distribution data available for the selected period.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const genderPercentages = getGenderPercentages(demographics);

  // Calculate Average Age
  const calculateAverageAge = (demographicsData: Demographics): number => {
    const ageGroupMidpoints: Record<AgeGroup, number> = {
      '0-9': 4.5,
      '10-19': 14.5,
      '20-29': 24.5,
      '30-39': 34.5,
      '40-49': 44.5,
      '50+': 55, // Estimate for 50+
    };

    let totalAgeSum = 0;
    let totalPeople = 0;

    AGE_GROUPS.forEach(ageGroup => {
      const maleCount = demographicsData.male[ageGroup] || 0;
      const femaleCount = demographicsData.female[ageGroup] || 0;
      const groupTotal = maleCount + femaleCount;
      
      totalAgeSum += groupTotal * ageGroupMidpoints[ageGroup];
      totalPeople += groupTotal;
    });

    return totalPeople > 0 ? totalAgeSum / totalPeople : 0;
  };

  const averageAge = calculateAverageAge(demographics);

  // Prepare pie chart data
  const pieChartData = ageGroupData
    .filter(item => item.total > 0)
    .map((item, index) => ({
      name: item.ageGroup,
      value: item.total,
      percentage: item.percentage,
      color: AGE_GROUP_COLORS[index % AGE_GROUP_COLORS.length]
    }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background p-3 border border-border rounded-lg shadow-lg">
          <p className="font-medium text-foreground">{`Age Group: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}`}
            </p>
          ))}
          <p className="text-sm text-muted-foreground">
            Total: {payload.reduce((sum: number, entry: any) => sum + entry.value, 0)}
          </p>
        </div>
      );
    }
    return null;
  };

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
    <div ref={ref} className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Age</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageAge.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Average age of detected individuals
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Most Common Age</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {ageGroupData.reduce((max, current) => 
                current.total > max.total ? current : max, ageGroupData[0] || { ageGroup: 'N/A', total: 0 }
              ).ageGroup}
            </div>
            <p className="text-xs text-muted-foreground">
              {ageGroupData.reduce((max, current) => 
                current.total > max.total ? current : max, ageGroupData[0] || { total: 0 }
              ).total} people
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gender Split</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              <div>
                <div className="text-lg font-bold text-primary">
                  {genderPercentages.male.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">Male</p>
              </div>
              <div>
                <div className="text-lg font-bold text-secondary-foreground">
                  {genderPercentages.female.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">Female</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Container - This is what gets exported */}
      <div className="age-distribution-charts space-y-6">
        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bar Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Age Distribution by Gender</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ageGroupData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ageGroup" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="male" fill={getCustomProperty('--chart-1') || '#3b82f6'} name="Male" />
                  <Bar dataKey="female" fill={getCustomProperty('--chart-2') || '#ec4899'} name="Female" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Pie Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Age Group Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
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
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip content={<PieTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Detailed Age Group Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {ageGroupData.map((item, index) => (
                <div key={item.ageGroup} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: AGE_GROUP_COLORS[index % AGE_GROUP_COLORS.length] }}
                    />
                    <div>
                      <div className="font-medium">Age {item.ageGroup}</div>
                      <div className="text-sm text-muted-foreground">
                        {item.percentage.toFixed(1)}% of total
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-6 text-sm">
                    <div className="text-center">
                      <div className="font-medium text-primary">{item.male}</div>
                      <div className="text-muted-foreground">Male</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-secondary-foreground">{item.female}</div>
                      <div className="text-muted-foreground">Female</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">{item.total}</div>
                      <div className="text-muted-foreground">Total</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
});

AgeDistributionSection.displayName = 'AgeDistributionSection';

export default AgeDistributionSection;
