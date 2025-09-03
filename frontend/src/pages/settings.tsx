import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { ConfirmModal } from '../components/ui/modal';
import apiService, { ModelSettings, handleApiError } from '../services/api';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<ModelSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aggregating, setAggregating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showAggregationModal, setShowAggregationModal] = useState(false);
  const [formData, setFormData] = useState({
    confidence_threshold_person: 0.5,
    confidence_threshold_face: 0.5,
    log_interval_seconds: 60,
  });

  // Load current settings
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const currentSettings = await apiService.getModelSettings();
      setSettings(currentSettings);
      setFormData({
        confidence_threshold_person: currentSettings.confidence_threshold_person,
        confidence_threshold_face: currentSettings.confidence_threshold_face,
        log_interval_seconds: currentSettings.log_interval_seconds,
      });
    } catch (err) {
      console.error('Error loading settings:', err);
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof typeof formData, value: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear messages when user starts editing
    setError(null);
    setSuccessMessage(null);
  };

  const validateForm = (): string | null => {
    if (formData.confidence_threshold_person < 0 || formData.confidence_threshold_person > 1) {
      return 'Person confidence threshold must be between 0.0 and 1.0';
    }
    if (formData.confidence_threshold_face < 0 || formData.confidence_threshold_face > 1) {
      return 'Face confidence threshold must be between 0.0 and 1.0';
    }
    if (formData.log_interval_seconds < 1 || formData.log_interval_seconds > 3600) {
      return 'Log interval must be between 1 and 3600 seconds';
    }
    return null;
  };

  const handleSave = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);

      const updatedSettings = await apiService.updateModelSettings(formData);
      setSettings(updatedSettings);
      setSuccessMessage('Settings saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (settings) {
      setFormData({
        confidence_threshold_person: settings.confidence_threshold_person,
        confidence_threshold_face: settings.confidence_threshold_face,
        log_interval_seconds: settings.log_interval_seconds,
      });
      setError(null);
      setSuccessMessage(null);
    }
  };

  const handleManualAggregation = async () => {
    try {
      setAggregating(true);
      setError(null);
      setSuccessMessage(null);
      setShowAggregationModal(false);

      const result = await apiService.triggerDataAggregation();

      if (result.success) {
        let message = 'Data aggregation completed successfully!';

        // Add stats if available
        if (result.stats) {
          const { processed_records, daily_aggregations_created, monthly_aggregations_created } = result.stats;
          message += ` Processed ${processed_records} records, created ${daily_aggregations_created} daily and ${monthly_aggregations_created} monthly aggregations.`;
        }

        // Handle warning status (timeout but likely successful)
        if (result.status === 'warning') {
          message = result.message + ' You can check your dashboard to see if new aggregated data appears.';
        }

        setSuccessMessage(message);
        // Clear success message after 10 seconds (longer for detailed message)
        setTimeout(() => setSuccessMessage(null), 10000);
      } else {
        setError(result.message || 'Data aggregation failed');
      }
    } catch (err) {
      console.error('Error triggering data aggregation:', err);
      setError(handleApiError(err));
    } finally {
      setAggregating(false);
    }
  };

  const hasChanges = settings && (
    formData.confidence_threshold_person !== settings.confidence_threshold_person ||
    formData.confidence_threshold_face !== settings.confidence_threshold_face ||
    formData.log_interval_seconds !== settings.log_interval_seconds
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-foreground mb-6">Detection Model Settings</h1>
          <Card className="p-6">
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-3 text-muted-foreground">Loading settings...</span>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-6">Detection Model Settings</h1>

        {/* Status Messages */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-destructive" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-destructive-foreground">{error}</p>
              </div>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700 dark:text-green-300">{successMessage}</p>
              </div>
            </div>
          </div>
        )}

        {/* Settings Form */}
        <Card className="p-6 mb-6">
          <div className="space-y-6">
            {/* Person Detection Confidence */}
            <div>
              <label htmlFor="confidence_threshold_person" className="block text-sm font-medium text-foreground mb-2">
                Person Detection Confidence Threshold
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  id="confidence_threshold_person"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.confidence_threshold_person}
                  onChange={(e) => handleInputChange('confidence_threshold_person', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer"
                />
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.confidence_threshold_person}
                  onChange={(e) => handleInputChange('confidence_threshold_person', parseFloat(e.target.value) || 0)}
                  className="w-20 px-3 py-2 text-sm border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Minimum confidence level for person detection (0.0 - 1.0). Higher values = fewer false positives but might miss some detections.
              </p>
            </div>

            {/* Face Detection Confidence */}
            <div>
              <label htmlFor="confidence_threshold_face" className="block text-sm font-medium text-foreground mb-2">
                Face Detection Confidence Threshold
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  id="confidence_threshold_face"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.confidence_threshold_face}
                  onChange={(e) => handleInputChange('confidence_threshold_face', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer"
                />
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.confidence_threshold_face}
                  onChange={(e) => handleInputChange('confidence_threshold_face', parseFloat(e.target.value) || 0)}
                  className="w-20 px-3 py-2 text-sm border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Minimum confidence level for face detection (0.0 - 1.0). Higher values = more accurate face detection but might miss some faces.
              </p>
            </div>

            {/* Log Interval */}
            <div>
              <label htmlFor="log_interval_seconds" className="block text-sm font-medium text-foreground mb-2">
                Data Logging Interval (seconds)
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  id="log_interval_seconds"
                  min="1"
                  max="3600"
                  step="1"
                  value={formData.log_interval_seconds}
                  onChange={(e) => handleInputChange('log_interval_seconds', parseInt(e.target.value))}
                  className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer"
                />
                <input
                  type="number"
                  min="1"
                  max="3600"
                  step="1"
                  value={formData.log_interval_seconds}
                  onChange={(e) => handleInputChange('log_interval_seconds', parseInt(e.target.value) || 1)}
                  className="w-24 px-3 py-2 text-sm border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                />
                <span className="text-sm text-muted-foreground">sec</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                How often the detection model sends data to the server (1 - 3600 seconds). Shorter intervals = more frequent updates but higher server load.
              </p>
            </div>

            {/* Current Settings Info */}
            {settings && (
              <div className="bg-muted p-4 rounded-lg">
                <h3 className="text-sm font-medium text-foreground mb-3">Current Settings Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span className="ml-2 font-medium text-foreground">
                      {new Date(settings.last_updated).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Updated By:</span>
                    <span className="ml-2 font-medium text-foreground">
                      {settings.updated_by?.username || 'System'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-border">
              <Button
                variant="outline"
                onClick={handleReset}
                disabled={!hasChanges || saving}
              >
                Reset
              </Button>
              <Button
                onClick={handleSave}
                disabled={!hasChanges || saving}
                className="min-w-[100px]"
              >
                {saving ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2"></div>
                    Saving...
                  </div>
                ) : (
                  'Save Settings'
                )}
              </Button>
            </div>
          </div>
        </Card>

        {/* Data Management Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Data Management</h2>

          <div className="space-y-4">
            <div className="bg-primary/10 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-foreground mb-2">Manual Data Aggregation</h3>
              <p className="text-sm text-foreground mb-4">
                Manually trigger the aggregation process to update daily and monthly summaries from raw detection data.
                This process consolidates raw detection logs into optimized summary tables for faster analytics.
              </p>

              <div className="flex items-center space-x-4">
                <Button
                  onClick={() => setShowAggregationModal(true)}
                  disabled={aggregating}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground"
                >
                  {aggregating ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2"></div>
                      Processing...
                    </div>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Run Data Aggregation
                    </>
                  )}
                </Button>
              </div>

              <div className="mt-3 text-xs text-muted-foreground">
                <strong>Note:</strong> This process may take a few minutes depending on the amount of data.
                The system automatically runs this process daily, but you can trigger it manually if needed.
              </div>
            </div>
          </div>
        </Card>

        {/* Information Card */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">How to Use These Settings</h2>
          <div className="space-y-3 text-sm text-muted-foreground">
            <div>
              <strong className="text-foreground">Person Detection Confidence:</strong>
              <span className="ml-2">Controls how certain the AI must be before identifying a person. Lower values detect more people but may include false positives.</span>
            </div>
            <div>
              <strong className="text-foreground">Face Detection Confidence:</strong>
              <span className="ml-2">Controls face detection accuracy. Higher values ensure better face detection for age/gender analysis.</span>
            </div>
            <div>
              <strong className="text-foreground">Log Interval:</strong>
              <span className="ml-2">How often data is sent from the detection model to the server. Shorter intervals provide more real-time data but use more bandwidth.</span>
            </div>
            <div>
              <strong className="text-foreground">Data Aggregation:</strong>
              <span className="ml-2">Processes raw detection data into daily and monthly summaries for improved analytics performance and historical reporting.</span>
            </div>
          </div>
          <div className="mt-4 p-3 bg-primary/10 rounded-lg">
            <p className="text-sm text-primary">
              <strong>Note:</strong> Changes will take effect immediately for new detections. The detection model will automatically use these new settings.
            </p>
          </div>
        </Card>

        {/* Confirmation Modal */}
        <ConfirmModal
          isOpen={showAggregationModal}
          onClose={() => setShowAggregationModal(false)}
          onConfirm={handleManualAggregation}
          title="Confirm Data Aggregation"
          message="Are you sure you want to run the data aggregation process? This will process all raw detection data and update the daily and monthly summary tables. The process may take a few minutes to complete."
          confirmText="Start Aggregation"
          cancelText="Cancel"
          isLoading={aggregating}
        />
      </div>
    </div>
  );
};

export default SettingsPage;
