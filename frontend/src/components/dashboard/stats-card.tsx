import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatNumber } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  change?: {
    value: number;
    period: string;
    isPositive?: boolean;
  };
  description?: string;
  className?: string;
  variant?: 'default' | 'success' | 'warning' | 'destructive';
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  change,
  description,
  className,
  variant = 'default',
}: StatsCardProps) {
  const variantStyles = {
    default: 'border-border',
    success: 'border-border',
    warning: 'border-border',
    destructive: 'border-destructive/20',
  };

  const iconStyles = {
    default: 'text-muted-foreground',
    success: 'text-primary',
    warning: 'text-accent-foreground',
    destructive: 'text-destructive',
  };

  return (
    <Card className={cn(variantStyles[variant], className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={cn('h-4 w-4', iconStyles[variant])} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formatNumber(value)}</div>
        
        {change && (
          <div className="flex items-center space-x-2 mt-2">
            <Badge 
              variant={change.isPositive ? 'success' : 'destructive'}
              className="text-xs"
            >
              {change.isPositive ? '+' : ''}{change.value}%
            </Badge>
            <p className="text-xs text-muted-foreground">
              vs {change.period}
            </p>
          </div>
        )}
        
        {description && (
          <p className="text-xs text-muted-foreground mt-2">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

interface StatsGridProps {
  children: React.ReactNode;
  className?: string;
}

export function StatsGrid({ children, className }: StatsGridProps) {
  return (
    <div className={cn(
      'grid gap-4 md:grid-cols-2 lg:grid-cols-4',
      className
    )}>
      {children}
    </div>
  );
}
