import React, { useRef, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Download, FileText, Image, FileSpreadsheet, Loader2 } from 'lucide-react';

interface ExportMenuProps {
  exporting: boolean;
  exportingType: string;
  showExportMenu: boolean;
  setShowExportMenu: (show: boolean) => void;
  handleExportAction: (action: string) => void;
}

const ExportMenu: React.FC<ExportMenuProps> = ({
  exporting,
  exportingType,
  showExportMenu,
  setShowExportMenu,
  handleExportAction,
}) => {
  const menuRef = useRef<HTMLDivElement>(null);

  // Handle clicking outside to close menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowExportMenu(false);
      }
    };

    if (showExportMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showExportMenu, setShowExportMenu]);

  const exportOptions = [
    {
      key: 'csv',
      label: 'Export as CSV',
      icon: FileSpreadsheet,
      description: 'Download data in spreadsheet format',
    },
    {
      key: 'pdf',
      label: 'Export as PDF',
      icon: FileText,
      description: 'Download comprehensive report',
    },
    {
      key: 'charts',
      label: 'Export Charts',
      icon: Image,
      description: 'Download chart images',
    },
    {
      key: 'all',
      label: 'Export All',
      icon: Download,
      description: 'Download data and charts',
    },
  ];

  if (exporting) {
    return (
      <Button disabled className="min-w-[100px] sm:min-w-[140px] text-sm">
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        <span className="hidden sm:inline">Exporting {exportingType}...</span>
        <span className="sm:hidden">Exporting...</span>
      </Button>
    );
  }

  return (
    <div className="relative" ref={menuRef}>
      <Button
        onClick={() => setShowExportMenu(!showExportMenu)}
        variant="outline"
        className="min-w-[100px] sm:min-w-[140px] text-sm"
        size="sm"
      >
        <Download className="mr-2 h-4 w-4" />
        <span className="hidden sm:inline">Export Data</span>
        <span className="sm:hidden">Export</span>
      </Button>

      {showExportMenu && (
        <Card className="absolute right-0 top-full mt-2 w-56 sm:w-64 p-2 shadow-lg border z-50">
          <div className="space-y-1">
            {exportOptions.map((option) => {
              const IconComponent = option.icon;
              return (
                <button
                  key={option.key}
                  onClick={() => {
                    handleExportAction(option.key);
                    setShowExportMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors flex items-start gap-3"
                >
                  <IconComponent className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{option.label}</p>
                    <p className="text-xs text-muted-foreground break-words">{option.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
};

export default ExportMenu;
