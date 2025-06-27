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
    refetchInterval: scanSession => scanSession?.status === 'completed' ? false : 2000,
  });

  // Subscribe to WebSocket updates
  useWebSocket(scanId);

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
    <div className="mb-8">
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Analysis Progress</h3>
            <div className="flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${scanSession?.status === 'running' ? 'bg-success animate-pulse-slow' : 'bg-slate-400'}`} />
              <span className="text-sm text-slate-400">{getStatusText()}</span>
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
    </div>
  );
}
