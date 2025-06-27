import { useState } from "react";
import { Play, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import type { AnalysisOptions } from "@shared/schema";

interface URLInputSectionProps {
  onScanStart: (scanId: number) => void;
}

export default function URLInputSection({ onScanStart }: URLInputSectionProps) {
  const [url, setUrl] = useState("");
  const [options, setOptions] = useState<AnalysisOptions>({
    securityAudit: true,
    performanceTest: true,
    nlpAnalysis: true,
    deepInspection: false,
  });
  
  const { toast } = useToast();

  const startScanMutation = useMutation({
    mutationFn: async (data: { url: string; options: AnalysisOptions }) => {
      const response = await apiRequest("POST", "/api/scans", data);
      return response.json();
    },
    onSuccess: (data) => {
      onScanStart(data.id);
      toast({
        title: "Scan Started",
        description: `Analysis of ${url} has begun.`,
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to start scan. Please check the URL and try again.",
        variant: "destructive",
      });
    },
  });

  const handleStartScan = () => {
    if (!url.trim()) {
      toast({
        title: "Error", 
        description: "Please enter a valid URL.",
        variant: "destructive",
      });
      return;
    }

    // Add protocol if missing
    let formattedUrl = url.trim();
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = 'https://' + formattedUrl;
    }

    startScanMutation.mutate({ url: formattedUrl, options });
  };

  const handleOptionChange = (option: keyof AnalysisOptions, checked: boolean) => {
    setOptions(prev => ({ ...prev, [option]: checked }));
  };

  return (
    <div className="mb-8">
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="mb-4">
            <h2 className="text-2xl font-semibold text-white mb-2">Website Analysis</h2>
            <p className="text-slate-400">
              Enter a website URL to begin comprehensive AI-powered security and functionality audit
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Label htmlFor="website-url" className="block text-sm font-medium text-slate-300 mb-2">
                Website URL
              </Label>
              <Input
                id="website-url"
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white placeholder-slate-400 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleStartScan}
                disabled={startScanMutation.isPending}
                className={`px-6 py-3 font-medium text-white transition-all duration-300 ${
                  startScanMutation.isPending 
                    ? 'bg-blue-600 animate-pulse shadow-lg shadow-blue-500/50' 
                    : 'bg-primary hover:bg-blue-700 hover:shadow-lg'
                }`}
              >
                {startScanMutation.isPending ? (
                  <div className="flex items-center">
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    <span className="animate-pulse">Analyzing Website...</span>
                  </div>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Start AI Security Scan
                  </>
                )}
              </Button>
            </div>
          </div>
          
          {/* Scan Options */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="security-audit"
                checked={options.securityAudit}
                onCheckedChange={(checked) => handleOptionChange("securityAudit", !!checked)}
                className="border-slate-600 text-primary focus:ring-primary"
              />
              <Label htmlFor="security-audit" className="text-sm text-slate-300 cursor-pointer">
                Security Audit
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="performance-test"
                checked={options.performanceTest}
                onCheckedChange={(checked) => handleOptionChange("performanceTest", !!checked)}
                className="border-slate-600 text-primary focus:ring-primary"
              />
              <Label htmlFor="performance-test" className="text-sm text-slate-300 cursor-pointer">
                Performance Test
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="nlp-analysis"
                checked={options.nlpAnalysis}
                onCheckedChange={(checked) => handleOptionChange("nlpAnalysis", !!checked)}
                className="border-slate-600 text-primary focus:ring-primary"
              />
              <Label htmlFor="nlp-analysis" className="text-sm text-slate-300 cursor-pointer">
                NLP Analysis
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="deep-inspection"
                checked={options.deepInspection}
                onCheckedChange={(checked) => handleOptionChange("deepInspection", !!checked)}
                className="border-slate-600 text-primary focus:ring-primary"
              />
              <Label htmlFor="deep-inspection" className="text-sm text-slate-300 cursor-pointer">
                Deep Inspection
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
