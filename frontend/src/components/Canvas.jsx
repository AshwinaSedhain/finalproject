// frontend/src/components/Canvas.jsx
import React, { useRef, useState } from 'react';
import Plot from 'react-plotly.js';
import { 
  BarChart3, 
  Download, 
  Maximize2, 
  Minimize2, 
  X, 
  FileDown,
  Image,
  FileText,
  ChevronDown,
  RotateCcw,
  Archive
} from 'lucide-react';

const Canvas = ({ 
  report, 
  isExpanded, 
  onToggleExpand, 
  allReports, 
  activeReportId, 
  onReportChange, 
  onCloseReport,
  closedReports = [],
  onRestoreReport
}) => {
  const plotRef = useRef(null);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [showClosedReports, setShowClosedReports] = useState(false);

  // Enhanced download handler with multiple formats
  const handleDownload = (format = 'png') => {
    const plotElement = plotRef.current;
    if (!plotElement || !plotElement.el) {
      alert('Could not find the chart to download. Please try again.');
      return;
    }

    const config = {
      png: { format: 'png', width: 1920, height: 1080, scale: 2 },
      svg: { format: 'svg', width: 1920, height: 1080 },
      pdf: { format: 'pdf', width: 1920, height: 1080 },
      jpeg: { format: 'jpeg', width: 1920, height: 1080, scale: 2 }
    };

    const downloadConfig = config[format] || config.png;
    const filename = `${report?.title?.replace(/[^a-z0-9]/gi, '_') || 'chart'}.${format}`;

    plotElement.el.toImage(downloadConfig)
      .then((dataUrl) => {
        // For PDF, we need special handling
        if (format === 'pdf') {
          // Create a link with data URL
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        } else {
          // For image formats
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
        setShowDownloadMenu(false);
      })
      .catch((error) => {
        console.error('Download error:', error);
        alert(`Failed to download chart as ${format.toUpperCase()}. Please try again.`);
      });
  };

  const chartData = report?.chartData;

  return (
    <div className={`
      flex flex-col bg-white border-l border-gray-200
      ${isExpanded ? 'fixed inset-0 z-50' : 'w-1/2 flex-shrink-0'}
      transition-all duration-300 shadow-lg
    `}>
      {/* Tabs header */}
      <div className="border-b border-gray-200 bg-gray-50 flex-shrink-0">
        <div className="flex items-center overflow-x-auto scrollbar-hide">
          {allReports?.map((rep) => (
            <button
              key={rep.id}
              onClick={() => onReportChange(rep.id)}
              className={`group relative px-4 py-3 text-sm font-medium flex items-center gap-2 whitespace-nowrap transition-colors ${
                activeReportId === rep.id
                  ? 'bg-white text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-teal-600 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-4 h-4 flex-shrink-0" />
              <span className="max-w-32 truncate">{rep.title}</span>
              <button
                onClick={(e) => { 
                  e.stopPropagation(); 
                  onCloseReport(rep.id); 
                }}
                className="ml-1 p-0.5 rounded hover:bg-gray-200 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Close report"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </button>
          ))}
          
          {/* Closed Reports Button */}
          {closedReports && closedReports.length > 0 && (
            <button
              onClick={() => setShowClosedReports(!showClosedReports)}
              className="ml-2 px-4 py-3 text-sm font-medium flex items-center gap-2 text-gray-600 hover:text-teal-600 hover:bg-gray-100 transition-colors relative"
              title={`View ${closedReports.length} closed chart${closedReports.length > 1 ? 's' : ''}`}
            >
              <Archive className="w-4 h-4 flex-shrink-0" />
              <span className="whitespace-nowrap">Closed ({closedReports.length})</span>
            </button>
          )}
        </div>
        
        {/* Closed Reports Dropdown */}
        {showClosedReports && closedReports && closedReports.length > 0 && (
          <div className="border-t border-gray-200 bg-white max-h-64 overflow-y-auto">
            <div className="p-2">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide px-2 py-1 mb-1">
                Closed Charts
              </div>
              {closedReports.map((closedRep) => (
                <button
                  key={closedRep.id}
                  onClick={() => {
                    if (onRestoreReport) {
                      onRestoreReport(closedRep.id);
                    }
                    setShowClosedReports(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-teal-50 hover:text-teal-700 rounded-lg flex items-center justify-between group transition-colors"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <BarChart3 className="w-4 h-4 flex-shrink-0 text-gray-400" />
                    <span className="truncate">{closedRep.title}</span>
                  </div>
                  <RotateCcw className="w-4 h-4 text-gray-400 group-hover:text-teal-600 flex-shrink-0 ml-2" title="Restore chart" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Report toolbar */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-white flex-shrink-0">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-teal-600" />
          <h3 className="font-semibold text-gray-900 text-lg">
            {report?.title || 'Report'}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {/* Download menu with dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1"
              title="Download Chart"
              disabled={!chartData}
            >
              <Download className="w-5 h-5" />
              <ChevronDown className={`w-3 h-3 transition-transform ${showDownloadMenu ? 'rotate-180' : ''}`} />
            </button>
            
            {showDownloadMenu && chartData && (
              <>
                <div 
                  className="fixed inset-0 z-10" 
                  onClick={() => setShowDownloadMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                  <button
                    onClick={() => handleDownload('png')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <Image className="w-4 h-4" />
                    Download as PNG
                  </button>
                  <button
                    onClick={() => handleDownload('jpeg')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <Image className="w-4 h-4" />
                    Download as JPEG
                  </button>
                  <button
                    onClick={() => handleDownload('svg')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <FileDown className="w-4 h-4" />
                    Download as SVG
                  </button>
                  <button
                    onClick={() => handleDownload('pdf')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Download as PDF
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Maximize/Minimize button */}
          <button
            onClick={onToggleExpand}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title={isExpanded ? "Exit Fullscreen" : "Enter Fullscreen"}
          >
            {isExpanded ? (
              <Minimize2 className="w-5 h-5" />
            ) : (
              <Maximize2 className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Report content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        {chartData ? (
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm h-full min-h-[500px]">
            <Plot
              ref={plotRef}
              data={chartData.data}
              layout={{ 
                ...chartData.layout, 
                autosize: true,
                title: chartData.layout?.title || '',
                margin: { l: 60, r: 60, t: 60, b: 60 },
                paper_bgcolor: 'white',
                plot_bgcolor: 'white'
              }}
              useResizeHandler={true}
              style={{ width: '100%', height: '100%', minHeight: '500px' }}
              config={{ 
                responsive: true, 
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                toImageButtonOptions: {
                  format: 'png',
                  filename: report?.title?.replace(/[^a-z0-9]/gi, '_') || 'chart',
                  height: 1080,
                  width: 1920,
                  scale: 2
                }
              }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Chart will be displayed here when generated.</p>
            </div>
          </div>
        )}

        {report?.insights && report.insights.length > 0 && (
          <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
            <h4 className="font-semibold text-teal-900 mb-2">Key Insights</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-teal-800">
              {report.insights.map((insight, idx) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Canvas;
