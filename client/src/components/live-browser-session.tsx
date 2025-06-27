import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Monitor, Eye, Activity, Clock, Globe } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import useWebSocket from "@/hooks/use-websocket";
import type { ScanSession } from "@shared/schema";

interface LiveBrowserSessionProps {
  scanId: number;
}

export default function LiveBrowserSession({ scanId }: LiveBrowserSessionProps) {
  const [browserActions, setBrowserActions] = useState<string[]>([]);
  const [currentAction, setCurrentAction] = useState<string>("");
  
  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 200,
  });

  const { logs } = useWebSocket(scanId);

  // Simulate browser actions based on scan progress
  useEffect(() => {
    if (!scanSession) return;
    
    const progress = scanSession.progress || 0;
    const actions = [];
    
    if (progress >= 10) actions.push("Opening browser instance");
    if (progress >= 20) actions.push("Navigating to target URL");
    if (progress >= 30) actions.push("Loading page resources");
    if (progress >= 40) actions.push("Analyzing DOM structure");
    if (progress >= 50) actions.push("Checking security headers");
    if (progress >= 60) actions.push("Testing for vulnerabilities");
    if (progress >= 70) actions.push("Running performance tests");
    if (progress >= 80) actions.push("Extracting content data");
    if (progress >= 90) actions.push("Generating analysis report");
    if (progress >= 100) actions.push("Browser session completed");
    
    setBrowserActions(actions);
    setCurrentAction(actions[actions.length - 1] || "Initializing...");
  }, [scanSession?.progress]);

  const getSessionStatus = () => {
    if (!scanSession) return "initializing";
    return scanSession.status;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "bg-blue-600";
      case "completed": return "bg-green-600";
      case "failed": return "bg-red-600";
      default: return "bg-gray-600";
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-white">
          <Monitor className="h-5 w-5" />
          Live Browser Session
          <Badge className={`ml-auto ${getStatusColor(getSessionStatus())}`}>
            {getSessionStatus().toUpperCase()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Action Display */}
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-blue-400 animate-pulse" />
            <span className="text-sm font-medium text-slate-300">Current Action</span>
          </div>
          <p className="text-white font-mono text-sm">{currentAction}</p>
        </div>

        {/* Browser Viewport Simulation */}
        <div className="bg-slate-900 rounded-lg border border-slate-600 overflow-hidden">
          <div className="bg-slate-700 px-3 py-2 flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <div className="flex-1 bg-slate-600 rounded px-2 py-1 text-xs text-slate-300 font-mono">
              {scanSession?.url || "about:blank"}
            </div>
          </div>
          <div className="p-4 h-32 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
            {scanSession?.status === 'running' && (
              <div className="absolute inset-0 bg-blue-500/10 animate-pulse">
                <div className="absolute top-2 left-2 right-2 h-4 bg-slate-700 rounded animate-pulse"></div>
                <div className="absolute top-8 left-2 w-1/3 h-3 bg-slate-700 rounded animate-pulse"></div>
                <div className="absolute top-14 left-2 w-1/2 h-3 bg-slate-700 rounded animate-pulse"></div>
                <div className="absolute bottom-2 right-2">
                  <Globe className="h-6 w-6 text-blue-400 animate-spin" />
                </div>
              </div>
            )}
            {scanSession?.status === 'completed' && (
              <div className="text-center text-green-400 font-mono text-sm">
                ✓ Page analysis completed successfully
              </div>
            )}
            {scanSession?.status === 'failed' && (
              <div className="text-center text-red-400 font-mono text-sm">
                ✗ Browser session failed
              </div>
            )}
          </div>
        </div>

        {/* Action History */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-300">Session Timeline</span>
          </div>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {browserActions.map((action, index) => (
              <div key={index} className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                <div className="w-1 h-1 rounded-full bg-blue-400"></div>
                {action}
              </div>
            ))}
          </div>
        </div>

        {/* Live Logs */}
        {logs.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-300">Live Console</span>
            </div>
            <div className="bg-black rounded p-2 max-h-24 overflow-y-auto font-mono text-xs">
              {logs.slice(-5).map((log, index) => (
                <div key={index} className="text-green-400">
                  <span className="text-slate-500">[{log.level}]</span> {log.message}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}