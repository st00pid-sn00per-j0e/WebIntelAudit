import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Monitor, Terminal } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import useWebSocket from "@/hooks/use-websocket";
import type { ScanSession, LogEntry } from "@shared/schema";

interface LiveAnalysisViewProps {
  scanId: number;
}

export default function LiveAnalysisView({ scanId }: LiveAnalysisViewProps) {
  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 2000,
  });

  // Subscribe to real-time updates
  const { logs } = useWebSocket(scanId);

  const getLevelColor = (level: string) => {
    switch (level) {
      case "ERROR": return "text-danger";
      case "WARN": return "text-warning";
      case "INFO": return "text-success";
      case "DEBUG": return "text-primary";
      case "PROCESSING": return "text-warning";
      default: return "text-slate-400";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const allLogs = [...(scanSession?.logs || []), ...logs];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      {/* Live Browser Session Simulation */}
      <Card className="bg-card border-border overflow-hidden">
        <CardHeader className="bg-slate-800 border-b border-border">
          <CardTitle className="text-sm font-medium text-white flex items-center space-x-2">
            <Monitor className="h-4 w-4" />
            <span>Live Browser Session</span>
            <div className="flex items-center space-x-2 ml-auto">
              <div className={`h-2 w-2 rounded-full ${scanSession?.status === 'running' ? 'bg-success animate-pulse' : 'bg-slate-400'}`} />
              <span className="text-xs text-slate-400">
                {scanSession?.status === 'running' ? 'Active' : 'Inactive'}
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="aspect-video bg-slate-900 flex items-center justify-center">
            <div className="text-center">
              <Monitor className="h-16 w-16 text-slate-600 mb-4 mx-auto" />
              <p className="text-slate-400 mb-2">Browser session simulation</p>
              <p className="text-xs text-slate-500">
                {scanSession?.status === 'running' 
                  ? 'Real-time Selenium automation in progress' 
                  : 'Waiting for analysis to start'
                }
              </p>
              {scanSession?.url && (
                <p className="text-xs text-primary mt-2">Target: {scanSession.url}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Logs */}
      <Card className="bg-card border-border overflow-hidden">
        <CardHeader className="bg-slate-800 border-b border-border">
          <CardTitle className="text-sm font-medium text-white flex items-center space-x-2">
            <Terminal className="h-4 w-4" />
            <span>Analysis Log Stream</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-80 p-4">
            <div className="font-mono text-xs space-y-1">
              {allLogs.length === 0 ? (
                <div className="text-slate-400 text-center py-8">
                  <Terminal className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>Waiting for analysis logs...</p>
                </div>
              ) : (
                allLogs.map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className="text-slate-400">
                    <span className="text-slate-500">[{formatTimestamp(log.timestamp)}]</span>{' '}
                    <span className={getLevelColor(log.level)}>{log.level}</span>{' '}
                    <span>{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
