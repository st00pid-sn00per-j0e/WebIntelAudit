import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { spawn } from "child_process";
import path from "path";
import { storage } from "./storage";
import { insertScanSessionSchema, type AnalysisOptions, type LogEntry } from "@shared/schema";
import { z } from "zod";

const analysisOptionsSchema = z.object({
  securityAudit: z.boolean().default(true),
  performanceTest: z.boolean().default(true),
  nlpAnalysis: z.boolean().default(true),
  deepInspection: z.boolean().default(false),
});

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);
  
  // WebSocket server for real-time updates
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  const sessionConnections = new Map<number, Set<WebSocket>>();

  wss.on('connection', (ws, req) => {
    console.log('WebSocket client connected');
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        console.log('Received WebSocket message:', message);
        if (message.type === 'subscribe' && message.sessionId) {
          const sessionId = parseInt(message.sessionId);
          console.log(`Subscribing WebSocket to session ${sessionId}`);
          if (!sessionConnections.has(sessionId)) {
            sessionConnections.set(sessionId, new Set());
          }
          sessionConnections.get(sessionId)!.add(ws);
          console.log(`Total connections for session ${sessionId}: ${sessionConnections.get(sessionId)!.size}`);
          
          // Send confirmation back to client
          ws.send(JSON.stringify({
            type: 'subscribed',
            sessionId: sessionId
          }));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    });

    ws.on('close', () => {
      // Remove connection from all sessions
      sessionConnections.forEach((connections) => {
        connections.delete(ws);
      });
    });
  });

  // Broadcast update to all clients subscribed to a session
  const broadcastUpdate = (sessionId: number, data: any) => {
    console.log(`Broadcasting to session ${sessionId}:`, data.type, data);
    const connections = sessionConnections.get(sessionId);
    if (connections && connections.size > 0) {
      console.log(`Found ${connections.size} connections for session ${sessionId}`);
      connections.forEach((ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          console.log(`Sending data to WebSocket:`, data);
          ws.send(JSON.stringify(data));
        } else {
          console.log(`WebSocket connection not open, removing from session ${sessionId}`);
          connections.delete(ws);
        }
      });
    } else {
      console.log(`No active connections for session ${sessionId}`);
    }
  };

  // Start a new scan
  app.post('/api/scans', async (req, res) => {
    try {
      const { url, options } = req.body;
      
      // Validate input
      const validatedUrl = insertScanSessionSchema.parse({ url });
      const validatedOptions = analysisOptionsSchema.parse(options || {});

      // Create scan session
      const session = await storage.createScanSession(validatedUrl);

      // Start the Python enhanced analyzer process
      const pythonScript = path.join(process.cwd(), 'server', 'services', 'enhanced_analyzer.py');
      console.log(`Starting enhanced analysis for session ${session.id}: ${pythonScript}`);
      console.log(`Command: python3 ${pythonScript} ${url} ${session.id} '${JSON.stringify(validatedOptions)}'`);
      
      const analysisProcess = spawn('python3', [
        pythonScript,
        url,
        session.id.toString(),
        JSON.stringify(validatedOptions)
      ], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Handle Python process output
      analysisProcess.stdout.on('data', async (data) => {
        try {
          const lines = data.toString().split('\n').filter(Boolean);
          for (const line of lines) {
            const update = JSON.parse(line);
            
            if (update.type === 'log') {
              await storage.addLogEntry(session.id, update.data);
              broadcastUpdate(session.id, { type: 'log', data: update.data });
            } else if (update.type === 'progress') {
              await storage.updateScanSession(session.id, { 
                progress: update.data.progress,
                status: update.data.status || 'running'
              });
              broadcastUpdate(session.id, { type: 'progress', data: update.data });
            } else if (update.type === 'result') {
              await storage.updateScanSession(session.id, {
                ...update.data,
                status: 'completed',
                completedAt: new Date()
              });
              broadcastUpdate(session.id, { type: 'result', data: update.data });
            } else if (update.type === 'browserAction') {
              broadcastUpdate(session.id, { type: 'browserAction', data: update.data });
            } else if (update.type === 'screenshot') {
              broadcastUpdate(session.id, { type: 'screenshot', data: update.data });
            }
          }
        } catch (error) {
          console.error('Error parsing Python output:', error);
        }
      });

      analysisProcess.stderr.on('data', async (data) => {
        const errorMessage = data.toString().trim();
        console.error(`Python stderr for session ${session.id}:`, errorMessage);
        const errorLog: LogEntry = {
          timestamp: new Date().toISOString(),
          level: 'ERROR',
          message: errorMessage
        };
        await storage.addLogEntry(session.id, errorLog);
        broadcastUpdate(session.id, { type: 'log', data: errorLog });
      });

      analysisProcess.on('close', async (code) => {
        console.log(`Python process for session ${session.id} exited with code ${code}`);
        if (code !== 0) {
          await storage.updateScanSession(session.id, { 
            status: 'failed',
            completedAt: new Date()
          });
          broadcastUpdate(session.id, { type: 'status', data: { status: 'failed' } });
        }
      });

      analysisProcess.on('error', (error) => {
        console.error(`Failed to start Python process for session ${session.id}:`, error);
      });

      res.json(session);
    } catch (error) {
      console.error('Error starting scan:', error);
      res.status(400).json({ message: 'Failed to start scan' });
    }
  });

  // Get scan session
  app.get('/api/scans/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const session = await storage.getScanSession(id);
      
      if (!session) {
        return res.status(404).json({ message: 'Scan session not found' });
      }
      
      res.json(session);
    } catch (error) {
      console.error('Error fetching scan:', error);
      res.status(500).json({ message: 'Failed to fetch scan' });
    }
  });

  // Get all scan sessions
  app.get('/api/scans', async (req, res) => {
    try {
      const sessions = await storage.getAllScanSessions();
      res.json(sessions);
    } catch (error) {
      console.error('Error fetching scans:', error);
      res.status(500).json({ message: 'Failed to fetch scans' });
    }
  });

  // Export scan report
  app.get('/api/scans/:id/export/:format', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const format = req.params.format;
      const session = await storage.getScanSession(id);
      
      if (!session) {
        return res.status(404).json({ message: 'Scan session not found' });
      }

      switch (format) {
        case 'json':
          res.setHeader('Content-Type', 'application/json');
          res.setHeader('Content-Disposition', `attachment; filename="scan-${id}-report.json"`);
          res.json(session);
          break;
        case 'csv':
          // Simple CSV export of vulnerabilities
          let csv = 'Type,Severity,Title,Description,Location\n';
          if (session.vulnerabilities) {
            session.vulnerabilities.forEach(vuln => {
              csv += `"${vuln.type}","${vuln.severity}","${vuln.title}","${vuln.description}","${vuln.location || ''}"\n`;
            });
          }
          res.setHeader('Content-Type', 'text/csv');
          res.setHeader('Content-Disposition', `attachment; filename="scan-${id}-vulnerabilities.csv"`);
          res.send(csv);
          break;
        default:
          res.status(400).json({ message: 'Unsupported export format' });
      }
    } catch (error) {
      console.error('Error exporting scan:', error);
      res.status(500).json({ message: 'Failed to export scan' });
    }
  });

  return httpServer;
}
