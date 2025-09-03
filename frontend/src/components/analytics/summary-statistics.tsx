import React from 'react';
import { Card } from '../ui/card';
import { Users, User, UserCheck } from 'lucide-react';

interface SummaryStatisticsProps {
  totals: {
    male: number;
    female: number;
    total: number;
  };
}

const SummaryStatistics: React.FC<SummaryStatisticsProps> = ({ totals }) => {
  return (
    <Card className="p-6">
      <h2 className="text-xl font-medium mb-6 text-foreground">Summary Statistics</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {/* Total People */}
        <div className="bg-card/50 rounded-lg p-4 text-center transition-transform hover:scale-105 shadow-sm border border-border">
          <div className="flex items-center justify-center mb-3">
            <Users className="h-8 w-8 text-primary" />
          </div>
          <p className="text-sm text-muted-foreground font-medium mb-1">Total People</p>
          <p className="text-4xl font-bold text-primary">{totals.total}</p>
        </div>

        {/* Male Count */}
        <div className="bg-card/50 rounded-lg p-4 text-center transition-transform hover:scale-105 shadow-sm border border-border">
          <div className="flex items-center justify-center mb-3">
            <User className="h-8 w-8 text-primary" />
          </div>
          <p className="text-sm text-muted-foreground font-medium mb-1">Male</p>
          <p className="text-4xl font-bold text-primary">{totals.male}</p>
          <p className="text-xs text-primary/80 mt-1">
            {totals.total > 0 ? Math.round((totals.male / totals.total) * 100) : 0}% of total
          </p>
        </div>

        {/* Female Count */}
        <div className="bg-card/50 rounded-lg p-4 text-center transition-transform hover:scale-105 shadow-sm border border-border">
          <div className="flex items-center justify-center mb-3">
            <UserCheck className="h-8 w-8 text-secondary-foreground" />
          </div>
          <p className="text-sm text-muted-foreground font-medium mb-1">Female</p>
          <p className="text-4xl font-bold text-secondary-foreground">{totals.female}</p>
          <p className="text-xs text-secondary-foreground/80 mt-1">
            {totals.total > 0 ? Math.round((totals.female / totals.total) * 100) : 0}% of total
          </p>
        </div>
      </div>
    </Card>
  );
};

export default SummaryStatistics;
