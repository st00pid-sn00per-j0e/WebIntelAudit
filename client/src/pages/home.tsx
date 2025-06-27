import { useState } from "react";
import { Bot, Settings, HelpCircle } from "lucide-react";
import URLInputSection from "@/components/url-input-section";
import AnalysisProgress from "@/components/analysis-progress";
import LiveAnalysisView from "@/components/live-analysis-view";
import AnalysisResults from "@/components/analysis-results";
import DetailedReports from "@/components/detailed-reports";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [currentScanId, setCurrentScanId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-dark text-slate-100">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Bot className="text-primary text-2xl" />
                <h1 className="text-xl font-bold text-white">AI Web Inspector</h1>
              </div>
              <div className="hidden sm:block">
                <span className="px-2 py-1 bg-primary/20 text-primary text-xs rounded-full">
                  Autonomous NLP + Selenium Engine
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="p-2 text-slate-400 hover:text-white">
                <Settings className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="p-2 text-slate-400 hover:text-white">
                <HelpCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* URL Input Section */}
        <URLInputSection onScanStart={setCurrentScanId} />

        {/* Live Analysis View - contains Browser Session, Progress and Results */}
        {currentScanId && <LiveAnalysisView scanId={currentScanId} />}

        {/* Detailed Reports */}
        {currentScanId && <DetailedReports scanId={currentScanId} />}
      </div>
    </div>
  );
}
