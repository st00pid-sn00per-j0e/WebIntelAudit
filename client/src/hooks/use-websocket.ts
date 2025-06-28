import { useEffect, useState, useRef } from "react";
import type { LogEntry } from "@shared/schema";

interface WebSocketMessage {
  type: 'log' | 'progress' | 'result' | 'status' | 'subscribed' | 'browserAction' | 'screenshot';
  data: any;
}

export default function useWebSocket(scanId: number) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [browserAction, setBrowserAction] = useState<string>("");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);

  const connect = () => {
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/ws`;

      console.log(`Connecting to WebSocket for scan ${scanId}: ${wsUrl}`);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`WebSocket connected for scan ${scanId}`);
        setIsConnected(true);
        reconnectAttempts.current = 0;

        // Subscribe to updates for this scan session with delay to ensure connection is ready
        setTimeout(() => {
          const subscribeMessage = {
            type: 'subscribe',
            sessionId: scanId.toString()
          };
          console.log('Sending subscription:', subscribeMessage);
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(subscribeMessage));
          }
        }, 100);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log(`WebSocket message for scan ${scanId}:`, message);

          switch (message.type) {
            case 'subscribed':
              console.log(`Successfully subscribed to scan ${scanId}`);
              break;
            case 'log':
              setLogs(prev => [...prev, message.data]);
              break;
            case 'progress':
              console.log(`Progress update for scan ${scanId}:`, message.data);
              // Force a query invalidation to refresh UI
              break;
            case 'result':
              console.log(`Result received for scan ${scanId}`);
              break;
            case 'status':
              console.log(`Status update for scan ${scanId}:`, message.data);
              break;
            case 'browserAction':
              console.log(`Browser action for scan ${scanId}:`, message.data.action);
              setBrowserAction(message.data.action);
              break;
            case 'screenshot':
              console.log(`Screenshot received for scan ${scanId}`);
              setScreenshot(message.data.image);
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < 5) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000;
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
    fetch("/api/scans")
      .then(res => res.ok && res.json())
      .then(data => setScanData(data));
  }, 5000); // Throttled to 5 seconds

    return () => {
      clearInterval(interval);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [scanId]);

  return {
    logs,
    isConnected,
    browserAction,
    screenshot
  };
}