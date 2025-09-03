import { format } from 'date-fns';
import type { RefObject } from 'react';
import html2canvas from 'html2canvas-pro';
import jsPDF from 'jspdf';

interface DateRange {
  startDate: Date;
  endDate: Date;
}

interface RangeStats {
  data: Record<string, { male: number; female: number; total?: number }>;
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

interface Totals {
  male: number;
  female: number;
  total: number;
}

// Export basic gender data as CSV
export const exportDataAsCSV = async (
  data: Record<string, { male: number; female: number; total?: number }>,
  dateRange: DateRange
): Promise<void> => {
  try {
    const csvRows = ['Date,Male,Female,Total'];
    
    Object.entries(data).forEach(([date, values]) => {
      const total = values.total || values.male + values.female;
      csvRows.push(`${date},${values.male},${values.female},${total}`);
    });
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `analytics_data_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  } catch (error) {
    console.error('Error exporting CSV:', error);
    throw new Error(`Failed to export CSV file: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export age-gender data as CSV
export const exportAgeGenderDataAsCSV = async (
  data: Record<string, {
    demographics: {
      male: Record<string, number>;
      female: Record<string, number>;
    };
    totals: { male: number; female: number; total: number };
  }>,
  dateRange: DateRange
): Promise<void> => {
  try {
    const ageGroups = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+'];
    const headers = ['Date', 'Total_Male', 'Total_Female', 'Total'];
    
    // Add age group headers
    ageGroups.forEach(ageGroup => {
      headers.push(`Male_${ageGroup}`, `Female_${ageGroup}`);
    });
    
    const csvRows = [headers.join(',')];
    
    Object.entries(data).forEach(([date, values]) => {
      const row = [
        date,
        values.totals.male.toString(),
        values.totals.female.toString(),
        values.totals.total.toString()
      ];
      
      // Add age group data
      ageGroups.forEach(ageGroup => {
        const maleCount = values.demographics.male[ageGroup] || 0;
        const femaleCount = values.demographics.female[ageGroup] || 0;
        row.push(maleCount.toString(), femaleCount.toString());
      });
      
      csvRows.push(row.join(','));
    });
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `age_gender_analytics_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  } catch (error) {
    console.error('Error exporting age-gender CSV:', error);
    throw new Error(`Failed to export age-gender CSV file: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export charts as PNG
export const exportChartsAsPNG = async (
  peopleCountChartRef: RefObject<HTMLDivElement | null>,
  genderDistributionChartRef: RefObject<HTMLDivElement | null>,
  dateRange: DateRange,
  ageDistributionChartRef?: RefObject<HTMLDivElement | null>
): Promise<void> => {
  try {
    const dateStr = `${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}`;
    
    // Export people count chart
    if (peopleCountChartRef.current) {
      console.log('Attempting to export people count chart...');
      try {
        const canvas1 = await html2canvas(peopleCountChartRef.current, {
          backgroundColor: 'white',
          scale: 2,
          useCORS: true,
        });
        
        const link1 = document.createElement('a');
        link1.download = `people_count_chart_${dateStr}.png`;
        link1.href = canvas1.toDataURL();
        link1.click();
        console.log('People count chart exported successfully');
      } catch (chartError) {
        console.error('Error exporting people count chart:', chartError);
        throw new Error(`Failed to export people count chart: ${chartError instanceof Error ? chartError.message : 'Unknown error'}`);
      }
    }
    
    // Export gender distribution chart
    if (genderDistributionChartRef.current) {
      console.log('Attempting to export gender distribution chart...');
      try {
        const canvas2 = await html2canvas(genderDistributionChartRef.current, {
          backgroundColor: 'white',
          scale: 2,
          useCORS: true,
        });
        
        const link2 = document.createElement('a');
        link2.download = `gender_distribution_chart_${dateStr}.png`;
        link2.href = canvas2.toDataURL();
        link2.click();
        console.log('Gender distribution chart exported successfully');
      } catch (chartError) {
        console.error('Error exporting gender distribution chart:', chartError);
        throw new Error(`Failed to export gender distribution chart: ${chartError instanceof Error ? chartError.message : 'Unknown error'}`);
      }
    }

    // Export age distribution chart if provided
    if (ageDistributionChartRef && ageDistributionChartRef.current) {
      console.log('Attempting to export age distribution chart...');
      try {
        const canvas3 = await html2canvas(ageDistributionChartRef.current, {
          backgroundColor: 'white',
          scale: 2,
          useCORS: true,
        });
        
        const link3 = document.createElement('a');
        link3.download = `age_distribution_chart_${dateStr}.png`;
        link3.href = canvas3.toDataURL();
        link3.click();
        console.log('Age distribution chart exported successfully');
      } catch (chartError) {
        console.error('Error exporting age distribution chart:', chartError);
        throw new Error(`Failed to export age distribution chart: ${chartError instanceof Error ? chartError.message : 'Unknown error'}`);
      }
    }
  } catch (error) {
    console.error('Error exporting charts:', error);
    throw new Error(`Failed to export chart images: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export people count chart as PNG
export const exportPeopleCountChartAsPNG = async (
  peopleCountChartRef: RefObject<HTMLDivElement | null>,
  dateRange: DateRange
): Promise<void> => {
  try {
    if (!peopleCountChartRef.current) {
      throw new Error('Chart reference not found');
    }
    
    const canvas = await html2canvas(peopleCountChartRef.current, {
      backgroundColor: 'white',
      scale: 2,
      useCORS: true,
    });
    
    const link = document.createElement('a');
    link.download = `people_count_chart_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.png`;
    link.href = canvas.toDataURL();
    link.click();
  } catch (error) {
    console.error('Error exporting people count chart:', error);
    throw new Error(`Failed to export people count chart: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export age distribution chart as PNG
export const exportAgeDistributionChartAsPNG = async (
  ageDistributionChartRef: RefObject<HTMLDivElement | null>,
  dateRange: DateRange
): Promise<void> => {
  try {
    if (!ageDistributionChartRef.current) {
      throw new Error('Age distribution chart reference not found');
    }
    
    const canvas = await html2canvas(ageDistributionChartRef.current, {
      backgroundColor: 'white',
      scale: 2,
      useCORS: true,
    });
    
    const link = document.createElement('a');
    link.download = `age_distribution_chart_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.png`;
    link.href = canvas.toDataURL();
    link.click();
  } catch (error) {
    console.error('Error exporting age distribution chart:', error);
    throw new Error(`Failed to export age distribution chart: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export data as PDF
export const exportDataAsPDF = async (
  rangeStats: RangeStats,
  dateRange: DateRange,
  totals: Totals,
  peopleCountChartRef: RefObject<HTMLDivElement | null>,
  genderDistributionChartRef: RefObject<HTMLDivElement | null>,
  ageDistributionChartRef?: RefObject<HTMLDivElement | null>
): Promise<void> => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    let yPosition = 20;
    
    // Title
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Analytics Report', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;
    
    // Date range
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    const dateRangeText = `Period: ${format(dateRange.startDate, 'MMM dd, yyyy')} - ${format(dateRange.endDate, 'MMM dd, yyyy')}`;
    pdf.text(dateRangeText, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 20;
    
    // Summary statistics
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Summary Statistics', 20, yPosition);
    yPosition += 10;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Total People: ${totals.total}`, 20, yPosition);
    yPosition += 6;
    pdf.text(`Male: ${totals.male} (${totals.total > 0 ? Math.round((totals.male / totals.total) * 100) : 0}%)`, 20, yPosition);
    yPosition += 6;
    pdf.text(`Female: ${totals.female} (${totals.total > 0 ? Math.round((totals.female / totals.total) * 100) : 0}%)`, 20, yPosition);
    yPosition += 20;
    
    // Add charts if available
    try {
      if (peopleCountChartRef.current) {
        const chartCanvas = await html2canvas(peopleCountChartRef.current, {
          backgroundColor: 'white',
          scale: 1,
          useCORS: true,
        });
        
        const chartImgData = chartCanvas.toDataURL('image/png');
        const chartWidth = pageWidth - 40;
        const chartHeight = (chartCanvas.height * chartWidth) / chartCanvas.width;
        
        // Check if chart fits on current page
        if (yPosition + chartHeight > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('People Count Chart', 20, yPosition);
        yPosition += 10;
        
        pdf.addImage(chartImgData, 'PNG', 20, yPosition, chartWidth, chartHeight);
        yPosition += chartHeight + 15;
      }
      
      if (genderDistributionChartRef.current) {
        const chartCanvas = await html2canvas(genderDistributionChartRef.current, {
          backgroundColor: 'white',
          scale: 1,
          useCORS: true,
        });
        
        const chartImgData = chartCanvas.toDataURL('image/png');
        const chartWidth = pageWidth - 40;
        const chartHeight = (chartCanvas.height * chartWidth) / chartCanvas.width;
        
        // Check if chart fits on current page
        if (yPosition + chartHeight > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Gender Distribution Chart', 20, yPosition);
        yPosition += 10;
        
        pdf.addImage(chartImgData, 'PNG', 20, yPosition, chartWidth, chartHeight);
        yPosition += chartHeight + 15;
      }

      if (ageDistributionChartRef && ageDistributionChartRef.current) {
        const chartCanvas = await html2canvas(ageDistributionChartRef.current, {
          backgroundColor: 'white',
          scale: 1,
          useCORS: true,
        });
        
        const chartImgData = chartCanvas.toDataURL('image/png');
        const chartWidth = pageWidth - 40;
        const chartHeight = (chartCanvas.height * chartWidth) / chartCanvas.width;
        
        // Check if chart fits on current page
        if (yPosition + chartHeight > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Age Distribution Chart', 20, yPosition);
        yPosition += 10;
        
        pdf.addImage(chartImgData, 'PNG', 20, yPosition, chartWidth, chartHeight);
      }
    } catch (chartError) {
      console.warn('Could not add charts to PDF:', chartError);
    }
    
    // Add data table
    pdf.addPage();
    yPosition = 20;
    
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Detailed Data', 20, yPosition);
    yPosition += 15;
    
    // Table headers
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Date', 20, yPosition);
    pdf.text('Male', 60, yPosition);
    pdf.text('Female', 90, yPosition);
    pdf.text('Total', 120, yPosition);
    yPosition += 8;
    
    // Table data
    pdf.setFont('helvetica', 'normal');
    Object.entries(rangeStats.data).forEach(([date, values]) => {
      if (yPosition > pageHeight - 20) {
        pdf.addPage();
        yPosition = 20;
        // Re-add headers
        pdf.setFont('helvetica', 'bold');
        pdf.text('Date', 20, yPosition);
        pdf.text('Male', 60, yPosition);
        pdf.text('Female', 90, yPosition);
        pdf.text('Total', 120, yPosition);
        yPosition += 8;
        pdf.setFont('helvetica', 'normal');
      }
      
      const total = values.total || values.male + values.female;
      pdf.text(date, 20, yPosition);
      pdf.text(values.male.toString(), 60, yPosition);
      pdf.text(values.female.toString(), 90, yPosition);
      pdf.text(total.toString(), 120, yPosition);
      yPosition += 5;
    });
    
    // Save the PDF
    const fileName = `analytics_report_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.pdf`;
    pdf.save(fileName);
  } catch (error) {
    console.error('Error exporting PDF:', error);
    throw new Error(`Failed to export PDF report: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Export age-gender data as PDF
export const exportAgeGenderDataAsPDF = async (
  ageGenderData: AgeGenderData,
  dateRange: DateRange,
  ageDistributionChartRef?: RefObject<HTMLDivElement | null>,
  genderDemographicsChartRef?: RefObject<HTMLDivElement | null>
): Promise<void> => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    let yPosition = 20;

    // Calculate overall totals
    const overallTotals = Object.values(ageGenderData.data).reduce(
      (acc, curr) => ({
        male: acc.male + curr.totals.male,
        female: acc.female + curr.totals.female,
        total: acc.total + curr.totals.total,
      }),
      { male: 0, female: 0, total: 0 }
    );
    
    // Title
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Age-Gender Demographics Report', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;
    
    // Date range
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    const dateRangeText = `Period: ${format(dateRange.startDate, 'MMM dd, yyyy')} - ${format(dateRange.endDate, 'MMM dd, yyyy')}`;
    pdf.text(dateRangeText, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 20;
    
    // Summary statistics
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Summary Statistics', 20, yPosition);
    yPosition += 10;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Total People: ${overallTotals.total}`, 20, yPosition);
    yPosition += 6;
    pdf.text(`Male: ${overallTotals.male} (${overallTotals.total > 0 ? Math.round((overallTotals.male / overallTotals.total) * 100) : 0}%)`, 20, yPosition);
    yPosition += 6;
    pdf.text(`Female: ${overallTotals.female} (${overallTotals.total > 0 ? Math.round((overallTotals.female / overallTotals.total) * 100) : 0}%)`, 20, yPosition);
    yPosition += 20;

    // Add charts if available
    try {
      if (ageDistributionChartRef && ageDistributionChartRef.current) {
        const chartCanvas = await html2canvas(ageDistributionChartRef.current, {
          backgroundColor: 'white',
          scale: 1,
          useCORS: true,
        });
        
        const chartImgData = chartCanvas.toDataURL('image/png');
        const chartWidth = pageWidth - 40;
        const chartHeight = (chartCanvas.height * chartWidth) / chartCanvas.width;
        
        // Check if chart fits on current page
        if (yPosition + chartHeight > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Age Distribution Chart', 20, yPosition);
        yPosition += 10;
        
        pdf.addImage(chartImgData, 'PNG', 20, yPosition, chartWidth, chartHeight);
        yPosition += chartHeight + 15;
      }

      if (genderDemographicsChartRef && genderDemographicsChartRef.current) {
        const chartCanvas = await html2canvas(genderDemographicsChartRef.current, {
          backgroundColor: 'white',
          scale: 1,
          useCORS: true,
        });
        
        const chartImgData = chartCanvas.toDataURL('image/png');
        const chartWidth = pageWidth - 40;
        const chartHeight = (chartCanvas.height * chartWidth) / chartCanvas.width;
        
        // Check if chart fits on current page
        if (yPosition + chartHeight > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Gender Demographics Chart', 20, yPosition);
        yPosition += 10;
        
        pdf.addImage(chartImgData, 'PNG', 20, yPosition, chartWidth, chartHeight);
      }
    } catch (chartError) {
      console.warn('Could not add charts to PDF:', chartError);
    }
    
    // Save the PDF
    const fileName = `age_gender_report_${format(dateRange.startDate, 'yyyy-MM-dd')}_to_${format(dateRange.endDate, 'yyyy-MM-dd')}.pdf`;
    pdf.save(fileName);
  } catch (error) {
    console.error('Error exporting age-gender PDF:', error);
    throw new Error(`Failed to export age-gender PDF report: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};
