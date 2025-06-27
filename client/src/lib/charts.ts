import React, { useEffect, useRef } from "react";

// Chart.js types and utilities
export interface ChartProps {
  type: 'doughnut' | 'bar' | 'line';
  data: any;
  options?: any;
  className?: string;
}

export function Chart({ type, data, options = {}, className = "" }: ChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    const loadChart = async () => {
      if (!canvasRef.current) return;

      // Dynamically import Chart.js to avoid SSR issues
      const { Chart: ChartJS, registerables } = await import('chart.js');
      ChartJS.register(...registerables);

      // Destroy existing chart
      if (chartRef.current) {
        chartRef.current.destroy();
      }

      // Create new chart
      chartRef.current = new ChartJS(canvasRef.current, {
        type,
        data,
        options: {
          responsive: true,
          maintainAspectRatio: true,
          ...options
        }
      });
    };

    loadChart();

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [type, data, options]);

  return React.createElement('canvas', { ref: canvasRef, className });
}
