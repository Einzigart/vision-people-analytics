import { useState, useEffect, useRef } from 'react';
import { format, subDays, isSameDay, differenceInDays, isToday, isYesterday, parseISO, startOfDay } from 'date-fns';
import { BarChart3, PieChart, RefreshCw, Calendar, TrendingUp, Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StatsCard, StatsGrid } from '@/components/dashboard/stats-card';
import DateRangePicker from '@/components/common/date-range-picker';
import PeopleCountSection from '@/components/analytics/people-count-section';
import GenderDistributionSection from '@/components/analytics/gender-distribution-section';
import EnhancedGenderDemographics from '@/components/analytics/enhanced-gender-demographics';
import AgeDistributionSection from '@/components/analytics/age-distribution-section';
import ExportMenu from '@/components/analytics/export-menu';
import apiService, { handleApiError, formatDateForApi } from '@/services/api';
import { 
  exportDataAsCSV, 
  exportDataAsPDF, 
  exportChartsAsPNG,
  exportAgeGenderDataAsCSV,
  exportAgeDistributionChartAsPNG,
  exportAgeGenderDataAsPDF
} from '@/services/export-service';

interface RangeStats {
  data: Record<string, { male: number; female: number; total: number }>;
  type: string;
}

interface AgeGenderData {
  data: Record<string, {
    demographics: {
      male: Record<string, number>;
      female: Record<string, number>;
    };
    totals: {
      male: number;
      female: number;
      total: number;
    };
  }>;
  type: string;
}

interface DateRange {
  startDate: Date;
  endDate: Date;
}

interface Totals {
  male: number;
  female: number;
  total: number;
}

export default function Analytics() {
  const [serverToday, setServerToday] = useState<Date | null>(null);
  const [dateRange, setDateRange] = useState<DateRange | null>(null); // Initialize as null
  const [rangeStats, setRangeStats] = useState<RangeStats | null>(null);
  const [ageGenderData, setAgeGenderData] = useState<AgeGenderData | null>(null);
  const [loading, setLoading] = useState(true); // Keep true until serverToday and initial range are set
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportingType, setExportingType] = useState('');
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'gender' | 'age'>('overview');

  // Refs for chart export
  const peopleCountChartRef = useRef<HTMLDivElement>(null);
  const genderDistributionChartRef = useRef<HTMLDivElement>(null);
  const ageDistributionChartRef = useRef<HTMLDivElement>(null);
  const genderDemographicsChartRef = useRef<HTMLDivElement>(null);

  // Calculate totals with better error handling
  const totals: Totals = rangeStats ? Object.values(rangeStats.data).reduce(
    (acc, curr) => {
      // Validate current data entry
      const male = typeof curr.male === 'number' ? curr.male : 0;
      const female = typeof curr.female === 'number' ? curr.female : 0;
      const total = typeof curr.total === 'number' ? curr.total : male + female;
      
      return {
        male: acc.male + male,
        female: acc.female + female,
        total: acc.total + total
      };
    },
    { male: 0, female: 0, total: 0 }
  ) : { male: 0, female: 0, total: 0 };

  const fetchRangeStats = async (startDate: Date, endDate: Date, noCache: boolean = false) => {
    try {
      setIsRefreshing(true);
      setError(null);
      
      const formattedStartDate = formatDateForApi(startDate);
      const formattedEndDate = formatDateForApi(endDate);

      console.log(`Fetching analytics data for ${formattedStartDate} to ${formattedEndDate}`);
      
      // Use single consolidated API call with demographics for better performance
      const consolidatedData = await apiService.getAgeGenderAnalyticsData(
        formattedStartDate,
        formattedEndDate,
        { noCache }
      );
      
      console.log("Received analytics data:", consolidatedData);

      // Validate the received basic data
      if (consolidatedData && typeof consolidatedData === 'object' && consolidatedData.data) {
        setRangeStats(consolidatedData);
        setAgeGenderData(consolidatedData);
      } else {
        console.warn('Invalid basic data format received:', consolidatedData);
        setRangeStats({ data: {}, type: 'daily' });
        setAgeGenderData(null);
      }
    } catch (err: any) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Error fetching range stats:', err);
      
      // Set empty data on error to prevent infinite loading state
      setRangeStats({ data: {}, type: 'daily' });
      setAgeGenderData(null);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Fetch server's current date and then initial stats
  useEffect(() => {
    const initializeAnalytics = async () => {
      try {
        setLoading(true);
        // Fetch server's "today" date from an endpoint that provides it.
        // Using getTodayStats as it returns a 'date' field representing server's today.
        const todayStatsResponse = await apiService.getTodayStats();
        const currentServerDate = startOfDay(parseISO(todayStatsResponse.date));
        setServerToday(currentServerDate);

        // Set initial date range to "Last 7 Days"
        const initialEndDate = currentServerDate;
        const initialStartDate = subDays(currentServerDate, 6); // 6 days back to include today makes 7 days
        
        setDateRange({ startDate: initialStartDate, endDate: initialEndDate });
        // fetchRangeStats will be called by the useEffect watching dateRange

      } catch (err: any) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        console.error('Error initializing analytics with server date:', err);
        // Fallback to client's date if server date fetch fails
        const localToday = startOfDay(new Date());
        setServerToday(localToday); // Use local as fallback
        setDateRange({ startDate: localToday, endDate: localToday });
        setLoading(false); // Ensure loading stops on error
      }
      // setLoading(false) will be handled by fetchRangeStats's finally block
    };

    initializeAnalytics();
  }, []);

  useEffect(() => {
    if (dateRange?.startDate && dateRange?.endDate) {
      fetchRangeStats(dateRange.startDate, dateRange.endDate);
    }
  }, [dateRange]);

  const handleDateRangeChange = (startDate: Date, endDate: Date) => {
    setDateRange({ startDate, endDate });
  };

  const handleRefresh = () => {
    if (dateRange?.startDate && dateRange?.endDate) {
      // Force bypassing cache on refresh to get latest data immediately
      fetchRangeStats(dateRange.startDate, dateRange.endDate, true);
    } else {
      // Handle case where dateRange is not yet set, perhaps re-initialize
      const fallbackDate = serverToday || startOfDay(new Date());
      fetchRangeStats(subDays(fallbackDate, 6), fallbackDate, true);
    }
  };

  // Function to handle specific export actions
  const handleExportAction = async (action: string) => {
    if (exporting || !rangeStats || !dateRange) return; // Add !dateRange check
    
    setShowExportMenu(false);
    setExporting(true);
    
    try {
      switch (action) {
        case 'pdf':
          setExportingType('PDF');
          if (dateRange) { // Add null check for dateRange
            if (activeTab === 'age' && ageGenderData) {
              await exportAgeGenderDataAsPDF(
                ageGenderData,
                dateRange,
                ageDistributionChartRef,
                genderDemographicsChartRef
              );
            } else {
              await exportDataAsPDF(
                rangeStats,
                dateRange,
                totals,
                peopleCountChartRef,
                genderDistributionChartRef,
                ageDistributionChartRef
              );
            }
          }
          break;
        case 'csv':
          setExportingType('CSV');
          if (dateRange) { // Add null check for dateRange
            if (activeTab === 'age' && ageGenderData) {
              await exportAgeGenderDataAsCSV(ageGenderData.data, dateRange);
            } else {
              await exportDataAsCSV(rangeStats.data, dateRange);
            }
          }
          break;
        case 'charts':
          setExportingType('charts');
          if (dateRange) { // Add null check for dateRange
            if (activeTab === 'age' && ageDistributionChartRef.current) {
              await exportAgeDistributionChartAsPNG(ageDistributionChartRef, dateRange);
            } else {
              await exportChartsAsPNG(
                peopleCountChartRef,
                genderDistributionChartRef,
                dateRange,
                ageDistributionChartRef
              );
            }
          }
          break;
        case 'all':
          setExportingType('all files');
          if (dateRange) { // Add null check for dateRange
            if (activeTab === 'age' && ageGenderData) {
              await Promise.all([
                exportAgeGenderDataAsCSV(ageGenderData.data, dateRange),
                ageDistributionChartRef.current ? exportAgeDistributionChartAsPNG(ageDistributionChartRef, dateRange) : Promise.resolve()
              ]);
            } else {
              await Promise.all([
                exportDataAsCSV(rangeStats.data, dateRange),
                exportChartsAsPNG(peopleCountChartRef, genderDistributionChartRef, dateRange, ageDistributionChartRef)
              ]);
            }
          }
          break;
        default:
          break;
      }
    } catch (err) {
      console.error('Error exporting data:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to export data. Please try again.';
      setError(errorMessage);
    } finally {
      setExporting(false);
      setExportingType('');
    }
  };

  // Determine if we should show hourly data
  const isHourlyDisplay = rangeStats && dateRange && ( // Add dateRange null check
    isSameDay(dateRange.startDate, dateRange.endDate) &&
    (isToday(dateRange.startDate) || isYesterday(dateRange.startDate) ||
     differenceInDays(new Date(), dateRange.startDate) <= 2)
  );

  // Calculate period duration for display
  const periodDuration = dateRange ? differenceInDays(dateRange.endDate, dateRange.startDate) + 1 : 0;
  const averagePerDay = periodDuration > 0 ? Math.round(totals.total / periodDuration) : 0;

  if (loading || !dateRange) { // Show skeleton if loading or dateRange not yet initialized
    return <AnalyticsSkeleton />;
  }

  if (error) {
    return (
      <div className="container mx-auto p-4 sm:p-6">
        <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-destructive/50 bg-destructive/10">
          <div className="text-center px-4">
            <h3 className="text-lg font-semibold text-destructive mb-2">Error Loading Analytics</h3>
            <p className="text-muted-foreground mb-4 text-sm">{error}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (
    activeTab !== 'overview' && (
      !rangeStats || !rangeStats.data || Object.keys(rangeStats.data).length === 0 ||
      (Object.keys(rangeStats.data).length === 1 && rangeStats.data[Object.keys(rangeStats.data)[0]].total === 0 && Object.keys(rangeStats.data)[0] !== 'totals')
    )
  ) {
    return (
      <div className="container mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              Advanced analytics and data visualization
            </p>
          </div>
          <Button onClick={handleRefresh} variant="outline" size="sm" disabled={isRefreshing} className="self-start sm:self-auto">
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>

        {/* Date Range Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-base sm:text-lg">
              <Calendar className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
              Date Range Selection
            </CardTitle>
            <CardDescription className="text-sm">
              Choose a date range to analyze people counting data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DateRangePicker 
              onDateRangeChange={handleDateRangeChange} 
              initialStartDate={dateRange.startDate}
              initialEndDate={dateRange.endDate}
              serverReferenceDate={serverToday}
            />
          </CardContent>
        </Card>

        {/* No Data Message */}
        <div className="flex min-h-[300px] sm:min-h-[400px] items-center justify-center rounded-lg border bg-muted/30">
          <div className="text-center px-4">
            <div className="text-muted-foreground mb-2">📊</div>
            <h3 className="text-lg font-semibold mb-2">No Data Available</h3>
            <p className="text-muted-foreground mb-4 text-sm sm:text-base">
              No people counting data found for the selected date range.
              <br className="hidden sm:block" />
              Try selecting a different date range or check if data collection is active.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          {dateRange && (
            <p className="text-sm sm:text-base text-muted-foreground break-words">
              Analytics for {format(dateRange.startDate, 'MMM dd, yyyy')} - {format(dateRange.endDate, 'MMM dd, yyyy')}
              {periodDuration > 1 && ` (${periodDuration} days)`}
            </p>
          )}
        </div>
        <div className="flex items-center space-x-2 flex-shrink-0">
          <Button onClick={handleRefresh} variant="outline" size="sm" disabled={isRefreshing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
          <ExportMenu
            exporting={exporting}
            exportingType={exportingType}
            showExportMenu={showExportMenu}
            setShowExportMenu={setShowExportMenu}
            handleExportAction={handleExportAction}
          />
        </div>
      </div>

      {/* Date Range Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-base sm:text-lg">
            <Calendar className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
            Date Range Selection
          </CardTitle>
            <CardDescription className="text-sm">
              Select the time period for your analytics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DateRangePicker 
              onDateRangeChange={handleDateRangeChange} 
              initialStartDate={dateRange.startDate}
              initialEndDate={dateRange.endDate}
              serverReferenceDate={serverToday}
            />
          </CardContent>
        </Card>

      {/* Navigation Tabs */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-4">
            <Button
              variant={activeTab === 'overview' ? 'default' : 'outline'}
              onClick={() => setActiveTab('overview')}
              className="flex items-center justify-center space-x-2 text-sm sm:text-base w-full sm:w-auto"
              size="sm"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Overview</span>
            </Button>
            <Button
              variant={activeTab === 'gender' ? 'default' : 'outline'}
              onClick={() => setActiveTab('gender')}
              className="flex items-center justify-center space-x-2 text-sm sm:text-base w-full sm:w-auto"
              size="sm"
            >
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Gender Demographics</span>
              <span className="sm:hidden">Gender</span>
            </Button>
            <Button
              variant={activeTab === 'age' ? 'default' : 'outline'}
              onClick={() => setActiveTab('age')}
              className="flex items-center justify-center space-x-2 text-sm sm:text-base w-full sm:w-auto"
              size="sm"
              disabled={!ageGenderData}
            >
              <PieChart className="h-4 w-4" />
              <span className="hidden sm:inline">Age Demographics</span>
              <span className="sm:hidden">Age</span>
              {!ageGenderData && <span className="text-xs">(No Data)</span>}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Stats Cards */}
      <StatsGrid className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total People"
          value={totals.total}
          icon={TrendingUp}
          variant="default"
          description={`${averagePerDay} per day average`}
        />
        <StatsCard
          title="Male Count"
          value={totals.male}
          icon={BarChart3}
          variant="success"
          description={`${totals.total > 0 ? Math.round((totals.male / totals.total) * 100) : 0}% of total`}
        />
        <StatsCard
          title="Female Count"
          value={totals.female}
          icon={PieChart}
          variant="warning"
          description={`${totals.total > 0 ? Math.round((totals.female / totals.total) * 100) : 0}% of total`}
        />
        <StatsCard
          title="Data Points"
          value={rangeStats ? Object.keys(rangeStats.data).length : 0}
          icon={Calendar}
          variant="default"
          description={`${periodDuration} ${periodDuration === 1 ? 'day' : 'days'} selected`}
        />
      </StatsGrid>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
          {/* Time Series Chart - Responsive height */}
          <div className="w-full h-[350px] sm:h-[450px] xl:h-[500px]">
            <PeopleCountSection
              data={rangeStats?.data || {}}
              type={(isHourlyDisplay ? 'hourly' : (rangeStats?.type ?? 'daily')) as 'hourly' | 'daily' | 'weekly' | 'monthly'}
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              ref={peopleCountChartRef}
            />
          </div>

          {/* Gender Distribution Chart - Responsive height */}
          <div className="w-full h-[350px] sm:h-[450px] xl:h-[500px]">
            <GenderDistributionSection
              male={totals.male}
              female={totals.female}
              ref={genderDistributionChartRef}
            />
          </div>
        </div>
      )}

      {activeTab === 'gender' && (
        <div ref={genderDemographicsChartRef}>
          <EnhancedGenderDemographics
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
            data={rangeStats.data}
            type={isHourlyDisplay ? 'hourly' : rangeStats.type as 'hourly' | 'daily' | 'weekly' | 'monthly'}
          />
        </div>
      )}

      {activeTab === 'age' && ageGenderData && (
        <div ref={ageDistributionChartRef}>
          <AgeDistributionSection
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
          />
        </div>
      )}

      {activeTab === 'age' && !ageGenderData && (
        <Card>
          <CardContent className="p-6">
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-blue-800">
                Age distribution data is not available for the selected date range. 
                This may be because age-gender detection is not enabled or no age-gender data has been collected yet.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Additional Analytics Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">Analysis Summary</CardTitle>
          <CardDescription className="text-sm">
            Key insights from the selected time period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
              <Badge variant="secondary" className="text-xs w-fit">
                {rangeStats.type.charAt(0).toUpperCase() + rangeStats.type.slice(1)}
              </Badge>
              <span className="text-xs sm:text-sm text-muted-foreground">Data Granularity</span>
            </div>
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
              <div className="flex items-center space-x-2">
                <Badge variant="default" className="text-xs">{periodDuration} Days</Badge>
              </div>
              <span className="text-xs sm:text-sm text-muted-foreground">Period Length</span>
            </div>
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
              <Badge variant="success" className="text-xs w-fit">
                {totals.total > 0 ? `${Math.round((Math.max(totals.male, totals.female) / totals.total) * 100)}%` : "0%"}
              </Badge>
              <span className="text-xs sm:text-sm text-muted-foreground">Majority Gender</span>
            </div>
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
              <Badge variant="default" className="text-xs w-fit">
                {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
              </Badge>
              <span className="text-xs sm:text-sm text-muted-foreground">Current View</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function AnalyticsSkeleton() {
  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header Skeleton */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div className="space-y-2">
          <Skeleton className="h-6 sm:h-8 w-36 sm:w-48" />
          <Skeleton className="h-3 sm:h-4 w-64 sm:w-96" />
        </div>
        <div className="flex space-x-2">
          <Skeleton className="h-8 sm:h-9 w-20 sm:w-24" />
          <Skeleton className="h-8 sm:h-9 w-28 sm:w-32" />
        </div>
      </div>

      {/* Date Range Picker Skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-5 sm:h-6 w-40 sm:w-48" />
          <Skeleton className="h-3 sm:h-4 w-48 sm:w-64" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-7 sm:h-8 w-20 sm:w-24" />
              ))}
            </div>
            <div className="flex flex-col sm:flex-row gap-4">
              <Skeleton className="h-9 sm:h-10 flex-1" />
              <Skeleton className="h-9 sm:h-10 flex-1" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation Tabs Skeleton */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-8 sm:h-9 w-full sm:w-32" />
            ))}
          </div>
        </CardHeader>
      </Card>

      {/* Stats Cards Skeleton */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-3 sm:h-4 w-20 sm:w-24" />
              <Skeleton className="h-3 sm:h-4 w-3 sm:w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-6 sm:h-8 w-16 sm:w-20 mb-2" />
              <Skeleton className="h-3 w-24 sm:w-32" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid gap-4 sm:gap-6 xl:grid-cols-2">
        <div>
          <Card>
            <CardHeader>
              <Skeleton className="h-5 sm:h-6 w-40 sm:w-48" />
              <Skeleton className="h-3 sm:h-4 w-48 sm:w-64" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 sm:h-80 w-full" />
            </CardContent>
          </Card>
        </div>
        <div>
          <Card>
            <CardHeader>
              <Skeleton className="h-5 sm:h-6 w-40 sm:w-48" />
              <Skeleton className="h-3 sm:h-4 w-48 sm:w-64" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 sm:h-80 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Summary Skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-5 sm:h-6 w-40 sm:w-48" />
          <Skeleton className="h-3 sm:h-4 w-48 sm:w-64" />
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
                <Skeleton className="h-4 sm:h-5 w-12 sm:w-16" />
                <Skeleton className="h-3 sm:h-4 w-20 sm:w-24" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
