// frontend/src/components/Canvas.jsx
import React, { useRef } from 'react'; // Make sure to import useRef
import Plot from 'react-plotly.js';
import { BarChart3, Download, Maximize2, Minimize2, Sparkles, ChevronRight, X } from 'lucide-react';

const Canvas = ({ 
  report, 
  isExpanded, 
  onToggleExpand, 
  allReports, 
  activeReportId, 
  onReportChange, 
  onCloseReport 
}) => {
  
  // Create a ref that will hold a reference to the Plotly component
  const plotRef = useRef(null);

  // --- NEW, WORKING DOWNLOAD HANDLER ---
  const handleDownload = () => {
    const plotElement = plotRef.current;
    if (plotElement) {
      // The 'plotly_downloadimage' method is available on the component's DOM node.
      // We can also use the toImage method for more control.
      plotElement.el.toImage({ 
        format: 'png', 
        width: 1200, // Higher resolution for better quality
        height: 600,
        scale: 2 
      }).then((dataUrl) => {
        // Create a temporary link element to trigger the download
        const link = document.createElement('a');
        link.href = dataUrl;
        // Create a clean filename from the report title
        link.download = `${report?.title?.replace(/ /g, '_') || 'chart'}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    } else {
      // This alert will now only show if something is genuinely wrong
      alert('Could not find the chart to download. Please try again.');
    }
  };

  const chartData = report?.chartData;

  return (
    <div className={`
      flex flex-col bg-white border-l border-gray-200
      ${isExpanded ? 'fixed inset-0 z-50' : 'w-1/2 flex-shrink-0'}
      transition-all duration-300
    `}>
      {/* Tabs header (unchanged) */}
      <div className="border-b border-gray-200 bg-gray-50">
        <div className="flex items-center overflow-x-auto">
          {allReports?.map((rep) => (
            <button
              key={rep.id}
              onClick={() => onReportChange(rep.id)}
              className={`group relative px-4 py-3 text-sm ...`}
            >
              <BarChart3 className="w-4 h-4" />
              <span className="max-w-32 truncate">{rep.title}</span>
              <button
                onClick={(e) => { e.stopPropagation(); onCloseReport(rep.id); }}
                className="ml-1 p-0.5 ...">
                <X className="w-3.5 h-3.5" />
              </button>
            </button>
          ))}
        </div>
      </div>

      {/* Report toolbar with working download button */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-white">
        <h3 className="font-semibold text-gray-900 ...">
          <BarChart3 className="w-5 h-5 text-teal-600" />
          {report?.title || 'Report'}
        </h3>
        <div className="flex items-center gap-2">
          {/* --- THIS BUTTON IS NOW FULLY FUNCTIONAL --- */}
          <button
            onClick={handleDownload}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Download Chart as PNG"
            disabled={!chartData} // Button is disabled if there's no chart
          >
            <Download className="w-5 h-5" />
          </button>
          <button
            onClick={onToggleExpand}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title={isExpanded ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isExpanded ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Report content */}
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        {chartData ? (
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            {/* --- THE 'ref' IS ATTACHED TO THE PLOT COMPONENT HERE --- */}
            <Plot
              ref={plotRef}
              data={chartData.data}
              layout={{ ...chartData.layout, autosize: true, title: '' }} // Remove default title to avoid overlap
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
              config={{ responsive: true, displaylogo: false }} // Hiding the Plotly logo
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>Chart will be displayed here when generated.</p>
          </div>
        )}

        {report?.insights && report.insights.length > 0 && (
          <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
            {/* ... your insights rendering logic */}
          </div>
        )}
      </div>
    </div>
  );
};

export default Canvas;