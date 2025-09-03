import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { subDays, startOfDay, differenceInDays} from 'date-fns';
import { Button } from '../ui/button';

interface DateRangePickerProps {
  onDateRangeChange: (startDate: Date, endDate: Date) => void;
  initialStartDate?: Date;
  initialEndDate?: Date;
  serverReferenceDate?: Date | null; // Server's current date, or null if not yet fetched
}

const DateRangePicker: React.FC<DateRangePickerProps> = ({ 
  onDateRangeChange, 
  initialStartDate, 
  initialEndDate, 
  serverReferenceDate 
}) => {
  const [startDate, setStartDate] = useState(initialStartDate || subDays(new Date(), 7));
  const [endDate, setEndDate] = useState(initialEndDate || new Date());
  const [activePreset, setActivePreset] = useState('week');
  const [error, setError] = useState<string | null>(null);

  // Maximum allowed range in days
  const MAX_DATE_RANGE = 366; // Approximately 1 year
  
  const validateDateRange = (start: Date, end: Date): string | null => {
    if (!start || !end) {
      return "Please select valid dates";
    }
    
    if (differenceInDays(end, start) > MAX_DATE_RANGE) {
      return `Date range cannot exceed ${MAX_DATE_RANGE} days`;
    }
    
    return null;
  };

  const handleStartDateChange = (date: Date | null) => {
    try {
      if (!date) return;
      
      const validationError = validateDateRange(date, endDate);
      setError(validationError);
      
      setStartDate(date);
      setActivePreset('custom');
      
      if (!validationError) {
        onDateRangeChange(date, endDate);
      }
    } catch (err) {
      console.error('Error handling start date change:', err);
      setError('Invalid date selection');
    }
  };

  const handleEndDateChange = (date: Date | null) => {
    try {
      if (!date) return;
      
      const validationError = validateDateRange(startDate, date);
      setError(validationError);
      
      setEndDate(date);
      setActivePreset('custom');
      
      if (!validationError) {
        onDateRangeChange(startDate, date);
      }
    } catch (err) {
      console.error('Error handling end date change:', err);
      setError('Invalid date selection');
    }
  };

  useEffect(() => {
    if (initialStartDate) {
      setStartDate(initialStartDate);
    }
    if (initialEndDate) {
      setEndDate(initialEndDate);
    }
  }, [initialStartDate, initialEndDate]);

  const applyPreset = (preset: string) => {
    try {
      let newStart: Date;
      let newEnd: Date;

      // Use server's date for presets if available, otherwise fallback to local new Date()
      const baseDateForPresets = serverReferenceDate ? serverReferenceDate : new Date();
      const referenceToday = startOfDay(baseDateForPresets);

      switch (preset) {
        case 'today':
          newStart = referenceToday;
          newEnd = referenceToday;
          break;
        case 'yesterday':
          newStart = subDays(referenceToday, 1);
          newEnd = subDays(referenceToday, 1); // Corrected to be a single day
          break;
        case 'week': // Last 7 days, ending on referenceToday
          newStart = subDays(referenceToday, 6);
          newEnd = referenceToday;
          break;
        case 'month': // Last 30 days, ending on referenceToday
          newStart = subDays(referenceToday, 29);
          newEnd = referenceToday;
          break;
        case 'year': // Last 365 days, ending on referenceToday
          newStart = subDays(referenceToday, 364);
          newEnd = referenceToday;
          break;
        default: // Default to last 7 days
          newStart = subDays(referenceToday, 6);
          newEnd = referenceToday;
          break;
      }
      
      setError(null); // Clear any previous errors
      
      setStartDate(newStart);
      setEndDate(newEnd);
      setActivePreset(preset);
      onDateRangeChange(newStart, newEnd);
    } catch (err) {
      console.error('Error applying preset:', err);
      setError('Failed to apply date preset');
    }
  };

  const presetButtons = [
    { key: 'today', label: 'Today' },
    { key: 'yesterday', label: 'Yesterday' },
    { key: 'week', label: 'Last 7 Days' },
    { key: 'month', label: 'Last 30 Days' },
    { key: 'year', label: 'Last Year' },
  ];

  return (
    <div className="w-full space-y-4">
      <div className="flex flex-wrap gap-2">
        {presetButtons.map(({ key, label }) => (
          <Button
            key={key}
            variant={activePreset === key ? "default" : "outline"}
            size="sm"
            onClick={() => applyPreset(key)}
            className="text-xs"
          >
            {label}
          </Button>
        ))}
      </div>
      
      {error && (
        <div className="text-destructive text-sm bg-destructive/10 p-3 rounded-md border border-destructive/20">
          {error}
        </div>
      )}
      
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-foreground mb-2">
            Start Date
          </label>
          <DatePicker
            selected={startDate}
            onChange={handleStartDateChange}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            maxDate={endDate}
            className="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-foreground mb-2">
            End Date
          </label>
          <DatePicker
            selected={endDate}
            onChange={handleEndDateChange}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            maxDate={new Date()}
            className="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>
    </div>
  );
};

export default DateRangePicker;
