import { useState, useEffect, useCallback } from 'react';
import { Users, UserCheck, UserX, Clock, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StatsCard, StatsGrid } from '@/components/dashboard/stats-card';
import { PeopleCountChart } from '@/components/charts/people-count-chart';
import { AgeDistributionChart } from '@/components/charts/age-distribution-chart';
import apiService, { TodayStats, TodayAgeGenderStats, handleApiError } from '@/services/api';
import { formatDateTime } from '@/lib/utils';

export default function Dashboard() {
  const [todayStats, setTodayStats] = useState<TodayStats | null>(null);
  const [todayAgeGenderStats, setTodayAgeGenderStats] = useState<TodayAgeGenderStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchTodayStats = useCallback(async () => {
    try {
      setIsRefreshing(true);

      // Use single consolidated API call with demographics
      const consolidatedData = await apiService.getTodayStats(true);

      setTodayStats(consolidatedData);
      setTodayAgeGenderStats(consolidatedData);
      setLastUpdated(new Date());
    } catch (err: any) {
      handleApiError(err);
      console.error('Error fetching today\'s stats:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchTodayStats();

    // Set up polling interval (every 2 minutes to reduce load)
    const intervalId = setInterval(fetchTodayStats, 120000);

    return () => clearInterval(intervalId);
  }, [fetchTodayStats]); // Add fetchTodayStats to dependency array

  const handleRefresh = () => {
    fetchTodayStats();
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  // Error is now handled by logging to the console, not blocking the UI.

  if (!todayStats) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex min-h-[400px] items-center justify-center rounded-lg border bg-muted/30">
          <div className="text-center">
            <div className="text-muted-foreground mb-2">📊</div>
            <h3 className="text-lg font-semibold mb-2">No Data Available</h3>
            <p className="text-muted-foreground mb-4">
              No people counting data found for today.
            </p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time people counting statistics for today
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <div className="text-sm text-muted-foreground">
              Last updated: {formatDateTime(lastUpdated)}
            </div>
          )}
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            disabled={isRefreshing}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsGrid>
        <StatsCard
          title="Total People"
          value={todayStats.totals.total}
          icon={Users}
          variant="default"
          description="People detected today"
        />
        <StatsCard
          title="Male"
          value={todayStats.totals.male}
          icon={UserCheck}
          variant="success"
          description="Male detections"
        />
        <StatsCard
          title="Female"
          value={todayStats.totals.female}
          icon={UserX}
          variant="warning"
          description="Female detections"
        />
        <StatsCard
          title="Last Detection"
          value={todayStats.last_detection ? 1 : 0}
          icon={Clock}
          variant={todayStats.last_detection ? 'success' : 'default'}
          description={
            todayStats.last_detection
              ? `${formatDateTime(todayStats.last_detection)}`
              : 'No detections yet'
          }
        />
      </StatsGrid>

      {/* Charts Section */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Hourly Traffic Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Today's Hourly Traffic</CardTitle>
            <CardDescription>
              People count distribution throughout the day
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PeopleCountChart
              data={todayStats.hourly_data || todayStats.hourly_breakdown}
              period="hourly"
              height={350}
            />
          </CardContent>
        </Card>

        {/* Age Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Age Distribution</CardTitle>
            <CardDescription>
              Today's age group breakdown
            </CardDescription>
          </CardHeader>
          <CardContent>
            {todayAgeGenderStats ? (
              <AgeDistributionChart
                demographics={todayAgeGenderStats.demographics}
                height={350}
              />
            ) : (
              <div className="flex h-80 items-center justify-center rounded-lg border bg-muted/30">
                <p className="text-muted-foreground">Age distribution data not available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>
            Current system information and status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center space-x-2">
              <Badge variant="success">Online</Badge>
              <span className="text-sm text-muted-foreground">Detection System</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="info">Real-time</Badge>
              <span className="text-sm text-muted-foreground">Data Updates</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary">Active</Badge>
              <span className="text-sm text-muted-foreground">Monitoring</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-9 w-24" />
      </div>

      {/* Stats Cards Skeleton */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-20 mb-2" />
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid gap-6 md:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-64" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-80 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
