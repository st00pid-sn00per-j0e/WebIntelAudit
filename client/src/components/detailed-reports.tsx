import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { 
  AlertTriangle, 
  TrendingUp, 
  Bot, 
  ChevronDown, 
  FileCode, 
  Table, 
  FileText,
  X,
  AlertCircle,
  CheckCircle
} from "lucide-react";
import { Chart } from "@/lib/charts";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import type { ScanSession, VulnerabilityResult } from "@shared/schema";

interface DetailedReportsProps {
  scanId: number;
}

export default function DetailedReports({ scanId }: DetailedReportsProps) {
  const [openSections, setOpenSections] = useState<string[]>([]);
  const { toast } = useToast();

  const { data: scanSession } = useQuery<ScanSession>({
    queryKey: ['/api/scans', scanId],
    refetchInterval: 2000,
  });

  const exportMutation = useMutation({
    mutationFn: async (format: 'json' | 'csv') => {
      const response = await apiRequest('GET', `/api/scans/${scanId}/export/${format}`);
      return { data: response, format };
    },
    onSuccess: ({ data, format }) => {
      // Create download link
      const blob = new Blob([format === 'json' ? JSON.stringify(data, null, 2) : data], {
        type: format === 'json' ? 'application/json' : 'text/csv'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scan-${scanId}-report.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: "Export Complete",
        description: `Report exported as ${format.toUpperCase()}`,
      });
    },
    onError: () => {
      toast({
        title: "Export Failed",
        description: "Failed to export report. Please try again.",
        variant: "destructive",
      });
    }
  });

  const toggleSection = (section: string) => {
    setOpenSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  if (!scanSession || scanSession.status !== 'completed') {
    return null;
  }

  const vulnerabilities = scanSession.vulnerabilities || [];
  const performanceMetrics = scanSession.performanceMetrics;
  const nlpInsights = scanSession.nlpInsights;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "destructive";
      case "high": return "destructive"; 
      case "medium": return "secondary";
      case "low": return "outline";
      default: return "outline";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return <X className="w-4 h-4" />;
      case "medium":
        return <AlertCircle className="w-4 h-4" />;
      case "low":
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Vulnerability Report */}
      <Card className="bg-card border-border overflow-hidden">
        <Collapsible 
          open={openSections.includes('vulnerabilities')}
          onOpenChange={() => toggleSection('vulnerabilities')}
        >
          <CollapsibleTrigger asChild>
            <Button 
              variant="ghost" 
              className="w-full px-6 py-4 text-left flex items-center justify-between bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <AlertTriangle className="h-5 w-5 text-danger" />
                <h3 className="text-lg font-semibold text-white">Security Vulnerabilities</h3>
                <Badge variant="destructive">
                  {vulnerabilities.length} Issue{vulnerabilities.length !== 1 ? 's' : ''}
                </Badge>
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="p-6 border-t border-border">
              {vulnerabilities.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-success mx-auto mb-2" />
                  <p className="text-slate-400">No security vulnerabilities detected</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {vulnerabilities.map((vuln, index) => (
                    <div 
                      key={index}
                      className={`border-l-4 p-4 rounded-r-lg ${
                        vuln.severity === 'critical' || vuln.severity === 'high' 
                          ? 'border-danger bg-danger/5' 
                          : vuln.severity === 'medium'
                          ? 'border-warning bg-warning/5'
                          : 'border-success bg-success/5'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`mt-1 ${
                          vuln.severity === 'critical' || vuln.severity === 'high' ? 'text-danger' :
                          vuln.severity === 'medium' ? 'text-warning' : 'text-success'
                        }`}>
                          {getSeverityIcon(vuln.severity)}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-white mb-1">{vuln.title}</h4>
                          <p className="text-sm text-slate-400 mb-2">{vuln.description}</p>
                          
                          {vuln.evidence && (
                            <div className="bg-slate-900 p-3 rounded font-mono text-xs text-slate-300 mb-2">
                              {vuln.evidence}
                            </div>
                          )}
                          
                          <div className="flex items-center space-x-4 text-xs">
                            <Badge variant={getSeverityColor(vuln.severity)} className="capitalize">
                              {vuln.severity} Risk
                            </Badge>
                            {vuln.location && (
                              <span className="text-slate-400">{vuln.location}</span>
                            )}
                          </div>
                          
                          {vuln.recommendation && (
                            <p className="text-xs text-slate-300 mt-2 italic">
                              Recommendation: {vuln.recommendation}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* Performance Analysis */}
      <Card className="bg-card border-border overflow-hidden">
        <Collapsible 
          open={openSections.includes('performance')}
          onOpenChange={() => toggleSection('performance')}
        >
          <CollapsibleTrigger asChild>
            <Button 
              variant="ghost" 
              className="w-full px-6 py-4 text-left flex items-center justify-between bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <TrendingUp className="h-5 w-5 text-success" />
                <h3 className="text-lg font-semibold text-white">Performance Analysis</h3>
                <Badge variant="secondary">Detailed</Badge>
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="p-6 border-t border-border">
              {performanceMetrics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-white mb-3">Load Time Breakdown</h4>
                    <div className="h-48">
                      <Chart
                        type="bar"
                        data={{
                          labels: ['DNS', 'Connect', 'SSL', 'TTFB', 'Download', 'DOM Load'],
                          datasets: [{
                            data: [
                              performanceMetrics.dns,
                              performanceMetrics.connect,
                              performanceMetrics.ssl,
                              performanceMetrics.ttfb,
                              performanceMetrics.download,
                              performanceMetrics.domLoad
                            ],
                            backgroundColor: '#10B981',
                            borderRadius: 4
                          }]
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: { legend: { display: false } },
                          scales: {
                            y: {
                              beginAtZero: true,
                              grid: { color: '#334155' },
                              ticks: { color: '#94A3B8' }
                            },
                            x: {
                              grid: { display: false },
                              ticks: { color: '#94A3B8' }
                            }
                          }
                        }}
                      />
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-white mb-3">Resource Analysis</h4>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileCode className="h-4 w-4 text-primary" />
                          <span className="text-sm text-slate-300">JavaScript</span>
                        </div>
                        <span className="text-sm text-white">
                          {Math.round(performanceMetrics.jsSize / 1024)}KB
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="h-4 w-4 bg-success rounded" />
                          <span className="text-sm text-slate-300">CSS</span>
                        </div>
                        <span className="text-sm text-white">
                          {Math.round(performanceMetrics.cssSize / 1024)}KB
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="h-4 w-4 bg-warning rounded" />
                          <span className="text-sm text-slate-300">Images</span>
                        </div>
                        <span className="text-sm text-white">
                          {Math.round(performanceMetrics.imageSize / 1024)}KB
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-2" />
                  <p className="text-slate-400">No performance data available</p>
                </div>
              )}
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* AI Analysis Report */}
      <Card className="bg-card border-border overflow-hidden">
        <Collapsible 
          open={openSections.includes('ai-analysis')}
          onOpenChange={() => toggleSection('ai-analysis')}
        >
          <CollapsibleTrigger asChild>
            <Button 
              variant="ghost" 
              className="w-full px-6 py-4 text-left flex items-center justify-between bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <Bot className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-semibold text-white">AI Analysis Report</h3>
                <Badge variant="outline">NLP Powered</Badge>
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent className="p-6 border-t border-border">
              {nlpInsights ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-white mb-3">Content Architecture</h4>
                    <div className="bg-slate-900 p-4 rounded-lg text-center">
                      <Bot className="h-8 w-8 text-primary mx-auto mb-2" />
                      <p className="text-sm text-slate-400 mb-2">Detected Architecture</p>
                      <p className="text-white font-medium">{nlpInsights.architecture}</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-white mb-3">User Flow Analysis</h4>
                    <div className="space-y-3">
                      {nlpInsights.userFlows && nlpInsights.userFlows.length > 0 ? (
                        nlpInsights.userFlows.map((flow, index) => (
                          <div key={index} className="p-3 bg-slate-800/50 rounded-lg">
                            <div className="flex items-center space-x-2 mb-2">
                              <div className="w-2 h-2 bg-primary rounded-full" />
                              <span className="text-sm font-medium text-white">{flow}</span>
                            </div>
                            <div className="flex space-x-2">
                              <Badge variant="secondary" className="text-xs">Detected</Badge>
                              <Badge variant="outline" className="text-xs">Functional</Badge>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-slate-400 text-sm">No specific user flows detected</p>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Bot className="h-12 w-12 text-slate-400 mx-auto mb-2" />
                  <p className="text-slate-400">No AI analysis data available</p>
                </div>
              )}
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* Export Controls */}
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Export Analysis Report</h3>
              <p className="text-sm text-slate-400">Download comprehensive audit results in various formats</p>
            </div>
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => exportMutation.mutate('json')}
                disabled={exportMutation.isPending}
                className="flex items-center space-x-2"
              >
                <FileCode className="h-4 w-4" />
                <span>JSON</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => exportMutation.mutate('csv')}
                disabled={exportMutation.isPending}
                className="flex items-center space-x-2"
              >
                <Table className="h-4 w-4" />
                <span>CSV</span>
              </Button>
              <Button
                size="sm"
                disabled={true}
                className="flex items-center space-x-2 opacity-50"
                title="PDF export coming soon"
              >
                <FileText className="h-4 w-4" />
                <span>PDF Report</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
