import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Gauge, Brain } from "lucide-react";
import { Chart } from "@/lib/charts";
import useWebSocket from "@/hooks/use-websocket";
import type { ScanSession } from "@shared/schema";

interface AnalysisResultsProps {
  scanId: number;
}

export default function AnalysisResults({ scanId }: AnalysisResultsProps) {
  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 2000,
  });

  useWebSocket(scanId);

  if (!scanSession || scanSession.status !== 'completed') {
    return null;
  }

  const securityScore = scanSession.securityScore || 0;
  const getSecurityStatus = (score: number) => {
    if (score >= 80) return { text: "Excellent", color: "text-success" };
    if (score >= 60) return { text: "Good", color: "text-success" };
    if (score >= 40) return { text: "Needs Attention", color: "text-warning" };
    return { text: "Critical", color: "text-danger" };
  };

  const securityStatus = getSecurityStatus(securityScore);
  const vulnerabilities = scanSession.vulnerabilities || [];
  const performanceMetrics = scanSession.performanceMetrics;
  const nlpInsights = scanSession.nlpInsights;

  const getVulnerabilityIcon = (severity: string) => {
    switch (severity) {
      case "critical": return "text-danger";
      case "high": return "text-danger";
      case "medium": return "text-warning";
      case "low": return "text-success";
      default: return "text-slate-400";
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
      {/* Security Overview */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold text-white">Security Score</span>
            <Shield className="h-5 w-5 text-danger" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="relative w-24 h-24 mx-auto mb-4">
              <Chart
                type="doughnut"
                data={{
                  datasets: [{
                    data: [securityScore, 100 - securityScore],
                    backgroundColor: [
                      securityScore >= 60 ? '#10B981' : '#EF4444',
                      '#374151'
                    ],
                    borderWidth: 0
                  }]
                }}
                options={{
                  cutout: '75%',
                  plugins: { legend: { display: false } },
                  maintainAspectRatio: false
                }}
                className="w-24 h-24"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-xl font-bold ${securityScore >= 60 ? 'text-success' : 'text-danger'}`}>
                  {securityScore}
                </span>
              </div>
            </div>
            <p className={`text-sm ${securityStatus.color}`}>{securityStatus.text}</p>
            
            <div className="mt-4 space-y-2 text-left">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">SSL/TLS</span>
                <span className="text-success">✓</span>
              </div>
              {vulnerabilities.some(v => v.type === 'missing_headers') && (
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300">Security Headers</span>
                  <span className="text-warning">⚠</span>
                </div>
              )}
              {vulnerabilities.some(v => v.type === 'xss') && (
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-300">XSS Protection</span>
                  <span className="text-danger">✗</span>
                </div>
              )}
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">CSRF Protection</span>
                <span className="text-warning">?</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold text-white">Performance</span>
            <Gauge className="h-5 w-5 text-success" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-300">Load Time</span>
                <span className="text-sm text-success">{scanSession.loadTime || "N/A"}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-success h-2 rounded-full w-3/4" />
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-300">DOM Elements</span>
                <span className="text-sm text-white">{scanSession.domElements?.toLocaleString() || "N/A"}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-warning h-2 rounded-full w-1/2" />
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-300">JS Errors</span>
                <span className="text-sm text-danger">{scanSession.jsErrors || 0}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-danger h-2 rounded-full w-1/4" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* NLP Insights */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold text-white">NLP Insights</span>
            <Brain className="h-5 w-5 text-primary" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {nlpInsights?.contentType && (
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-primary rounded-full" />
                  <span className="text-sm font-medium text-white">Content Analysis</span>
                </div>
                <p className="text-xs text-slate-400">
                  Detected {nlpInsights.contentType.toLowerCase()} patterns with structured content
                </p>
              </div>
            )}
            
            {nlpInsights?.architecture && (
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-success rounded-full" />
                  <span className="text-sm font-medium text-white">Architecture</span>
                </div>
                <p className="text-xs text-slate-400">{nlpInsights.architecture}</p>
              </div>
            )}
            
            {nlpInsights?.userFlows && nlpInsights.userFlows.length > 0 && (
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-warning rounded-full" />
                  <span className="text-sm font-medium text-white">User Flows</span>
                </div>
                <p className="text-xs text-slate-400">
                  {nlpInsights.userFlows.length} interaction pathway{nlpInsights.userFlows.length !== 1 ? 's' : ''} identified
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
