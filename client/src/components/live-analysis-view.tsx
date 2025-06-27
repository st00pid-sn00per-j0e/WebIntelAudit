import LiveBrowserSession from "./live-browser-session";
import AnalysisProgress from "./analysis-progress";
import AnalysisResults from "./analysis-results";

interface LiveAnalysisViewProps {
  scanId: number;
}

export default function LiveAnalysisView({ scanId }: LiveAnalysisViewProps) {
  return (
    <div className="space-y-6">
      {/* Live Browser Session */}
      <LiveBrowserSession scanId={scanId} />
      
      {/* Analysis Progress */}
      <AnalysisProgress scanId={scanId} />
      
      {/* Results */}
      <AnalysisResults scanId={scanId} />
    </div>
  );
}