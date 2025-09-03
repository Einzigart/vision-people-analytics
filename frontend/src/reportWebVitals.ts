import type { ReportCallback } from 'web-vitals';

const reportWebVitals = (onPerfEntry?: ReportCallback) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then((mod: any) => {
      // Support both older `on*` and newer `get*` exports depending on package version
      const maybe = (names: string[]) => names.map((n) => (mod[n] ? mod[n] : undefined));
      const [cls, fid, fcp, lcp, ttfb] = maybe(['getCLS', 'getFID', 'getFCP', 'getLCP', 'getTTFB']);
      const [onCls, onFid, onFcp, onLcp, onTtfb] = maybe(['onCLS', 'onFID', 'onFCP', 'onLCP', 'onTTFB']);

      (cls || onCls)?.(onPerfEntry);
      (fid || onFid)?.(onPerfEntry);
      (fcp || onFcp)?.(onPerfEntry);
      (lcp || onLcp)?.(onPerfEntry);
      (ttfb || onTtfb)?.(onPerfEntry);
    }).catch(() => {});
  }
};

export default reportWebVitals;