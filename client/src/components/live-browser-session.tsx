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
  const [currentScreenshot, setCurrentScreenshot] = useState<string | null>(null);
  
  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 200,
  });

  const { logs, isConnected, browserAction, screenshot } = useWebSocket(scanId);

  // Update browser actions from WebSocket
  useEffect(() => {
    if (browserAction) {
      setBrowserActions(prev => [...prev, browserAction]);
      setCurrentAction(browserAction);
    }
  }, [browserAction]);

  // Update screenshot from WebSocket
  useEffect(() => {
    if (screenshot) {
      setCurrentScreenshot(screenshot);
    }
  }, [screenshot]);

  const getSessionStatus = () => {
    if (!scanSession) return "initializing";
    return scanSession.status || "pending";
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
            {getSessionStatus()?.toUpperCase() || "PENDING"}
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
          <div className="relative bg-white h-96 overflow-hidden">
            {scanSession?.status === 'running' ? (
              <div className="absolute inset-0">
                {currentScreenshot ? (
                  // Show real screenshot from Selenium
                  <img 
                    src={`data:image/png;base64,${currentScreenshot}`} 
                    alt="Live browser view" 
                    className="w-full h-full object-cover object-top"
                  />
                ) : (
                  // Live scanning simulation
                  <div className="absolute inset-0 bg-slate-50">
                    <div className="p-4 space-y-4">
                      {/* URL Bar */}
                      <div className="bg-white border border-slate-200 rounded-md p-2 flex items-center gap-2">
                        <Globe className="h-4 w-4 text-slate-400" />
                        <span className="text-sm text-slate-600 font-mono flex-1">{scanSession?.url || 'Loading...'}</span>
                      </div>
                      
                      {/* Page Content Simulation */}
                      <div className="space-y-3">
                        <div className="bg-slate-200 h-12 rounded animate-pulse"></div>
                        <div className="grid grid-cols-3 gap-4">
                          <div className="bg-slate-200 h-32 rounded animate-pulse"></div>
                          <div className="bg-slate-200 h-32 rounded animate-pulse delay-75"></div>
                          <div className="bg-slate-200 h-32 rounded animate-pulse delay-150"></div>
                        </div>
                        <div className="space-y-2">
                          <div className="bg-slate-200 h-4 rounded animate-pulse w-full"></div>
                          <div className="bg-slate-200 h-4 rounded animate-pulse w-5/6"></div>
                          <div className="bg-slate-200 h-4 rounded animate-pulse w-4/6"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {/* Scanning Overlay */}
                <div className="absolute inset-0 bg-blue-500/5 pointer-events-none">
                  <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500 animate-scan"></div>
                </div>
                {/* Status Indicator */}
                <div className="absolute bottom-4 right-4 bg-black/80 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
                  <Activity className="h-3 w-3 animate-pulse" />
                  {currentAction || "Analyzing Page..."}
                </div>
              </div>
            ) : scanSession?.status === 'completed' ? (
              <div className="absolute inset-0 bg-slate-50 flex items-center justify-center">
                <div className="text-center">
                  <Eye className="h-16 w-16 text-green-500 mx-auto mb-4" />
                  <p className="text-slate-700 font-medium">Analysis Complete</p>
                  <p className="text-slate-500 text-sm mt-1">All tests passed successfully</p>
                </div>
              </div>
            ) : scanSession?.status === 'failed' ? (
              <div className="absolute inset-0 bg-slate-50 flex items-center justify-center">
                <div className="text-center">
                  <div className="bg-red-100 rounded-full p-4 inline-block mb-4">
                    <Monitor className="h-12 w-12 text-red-500" />
                  </div>
                  <p className="text-slate-700 font-medium">Session Failed</p>
                  <p className="text-slate-500 text-sm mt-1">Unable to analyze the webpage</p>
                </div>
              </div>
            ) : (
              <div className="absolute inset-0 bg-slate-100 flex items-center justify-center">
                <div className="text-center">
                  <Globe className="h-12 w-12 text-slate-400 mb-2" />
                  <p className="text-slate-400">Waiting to start...</p>
                </div>
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