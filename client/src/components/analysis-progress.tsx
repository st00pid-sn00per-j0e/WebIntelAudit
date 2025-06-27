import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Globe, Bot, Brain, Shield } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import useWebSocket from "@/hooks/use-websocket";
import type { ScanSession } from "@shared/schema";

interface AnalysisProgressProps {
  scanId: number;
}

export default function AnalysisProgress({ scanId }: AnalysisProgressProps) {
  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 200, // Fast polling for real-time updates
  });

  // Subscribe to WebSocket updates for real-time progress and logs
  const { logs } = useWebSocket(scanId);

  // Show immediate loading state for better UX
  if (!scanSession) {
    return (
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold text-white mb-2">Starting AI Security Analysis</h3>
          <p className="text-slate-400">Connecting to target website and initializing vulnerability scanner...</p>
          
          <div className="mt-6 space-y-4">
            <div className="w-full bg-slate-700 rounded-full h-3 relative overflow-hidden">
              <div className="h-3 rounded-full bg-gradient-to-r from-blue-600 to-blue-400 animate-pulse" 
                   style={{ width: '25%' }} />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-300/30 to-transparent animate-shimmer" />
            </div>
            <div className="flex justify-between text-sm text-slate-400">
              <span>Establishing secure connection...</span>
              <span>25%</span>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  const getProgressSteps = () => {
    const progress = scanSession?.progress || 0;
    
    return [
      {
        icon: Globe,
        title: "Website Connection",
        status: progress >= 25 ? "completed" : progress >= 5 ? "running" : "pending",
        progress: Math.min(100, Math.max(0, (progress - 5) * 5))
      },
      {
        icon: Bot,
        title: "Selenium Automation", 
        status: progress >= 50 ? "completed" : progress >= 25 ? "running" : "pending",
        progress: Math.min(100, Math.max(0, (progress - 25) * 4))
      },
      {
        icon: Brain,
        title: "NLP Analysis",
        status: progress >= 85 ? "completed" : progress >= 50 ? "running" : "pending", 
        progress: Math.min(100, Math.max(0, (progress - 50) * 2.86))
      },
      {
        icon: Shield,
        title: "Security Assessment",
        status: progress >= 100 ? "completed" : progress >= 85 ? "running" : "pending",
        progress: Math.min(100, Math.max(0, (progress - 85) * 6.67))
      }
    ];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-success";
      case "running": return "text-warning";
      default: return "text-slate-400";
    }
  };

  const getProgressColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-success";
      case "running": return "bg-warning";
      default: return "bg-slate-600";
    }
  };

  const getStatusText = () => {
    if (!scanSession) return "Initializing...";
    
    switch (scanSession.status) {
      case "pending": return "Ready to scan";
      case "running": return "Analysis in progress";
      case "completed": return "Analysis completed";
      case "failed": return "Analysis failed";
      default: return "Unknown status";
    }
  };

  return (
    <div className="mb-8 space-y-4">
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Analysis Progress</h3>
            <div className="flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${scanSession?.status === 'running' ? 'bg-success animate-pulse-slow' : 'bg-slate-400'}`} />
              <span className="text-sm text-slate-400">{getStatusText()}</span>
            </div>
          </div>
          
          {/* Overall Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white">Overall Progress</span>
              <span className="text-sm text-slate-400">{scanSession?.progress || 0}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-3 relative overflow-hidden">
              <div 
                className={`h-3 rounded-full transition-all duration-300 ${
                  scanSession?.status === 'running' ? 'bg-gradient-to-r from-blue-600 to-blue-400 animate-pulse' : 
                  scanSession?.status === 'completed' ? 'bg-green-600' :
                  scanSession?.status === 'failed' ? 'bg-red-600' : 'bg-slate-600'
                }`}
                style={{ width: `${Math.max(5, scanSession?.progress || 0)}%` }}
              />
              {(scanSession?.status === 'running' || scanSession?.status === 'pending') && (
                <div 
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-300/30 to-transparent animate-shimmer"
                  style={{ animation: 'shimmer 1.5s infinite' }}
                />
              )}
            </div>
          </div>
          
          <div className="space-y-4">
            {getProgressSteps().map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={index} className="flex items-center space-x-4 p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      step.status === 'completed' ? 'bg-success' :
                      step.status === 'running' ? 'bg-warning animate-pulse' :
                      'bg-slate-600'
                    }`}>
                      <Icon className="h-4 w-4 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white">{step.title}</span>
                      <span className={`text-xs capitalize ${getStatusColor(step.status)}`}>
                        {step.status === 'running' ? `${Math.round(step.progress)}%` : step.status}
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2 mt-1">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(step.status)}`}
                        style={{ width: `${step.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Live Logs Section */}
      {(logs.length > 0 || (scanSession?.logs && scanSession.logs.length > 0)) && (
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Analysis Logs</h3>
            <div className="bg-slate-900 rounded-lg p-4 max-h-64 overflow-y-auto font-mono text-xs space-y-1">
              {(scanSession?.logs || logs).map((log, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <span className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <span className={`font-semibold ${
                    log.level === 'ERROR' ? 'text-red-400' :
                    log.level === 'WARN' ? 'text-yellow-400' :
                    log.level === 'INFO' ? 'text-blue-400' :
                    log.level === 'DEBUG' ? 'text-slate-400' :
                    'text-green-400'
                  }`}>[{log.level}]</span>
                  <span className="text-slate-300 flex-1">{log.message}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
