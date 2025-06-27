import { scanSessions, type ScanSession, type InsertScanSession, type LogEntry } from "@shared/schema";

export interface IStorage {
  createScanSession(session: InsertScanSession): Promise<ScanSession>;
  getScanSession(id: number): Promise<ScanSession | undefined>;
  updateScanSession(id: number, updates: Partial<ScanSession>): Promise<ScanSession | undefined>;
  addLogEntry(sessionId: number, logEntry: LogEntry): Promise<void>;
  getAllScanSessions(): Promise<ScanSession[]>;
}

export class MemStorage implements IStorage {
  private scanSessions: Map<number, ScanSession>;
  private currentId: number;

  constructor() {
    this.scanSessions = new Map();
    this.currentId = 1;
  }

  async createScanSession(insertSession: InsertScanSession): Promise<ScanSession> {
    const id = this.currentId++;
    const session: ScanSession = {
      ...insertSession,
      id,
      status: "pending",
      progress: 0,
      securityScore: null,
      loadTime: null,
      domElements: null,
      jsErrors: null,
      vulnerabilities: null,
      performanceMetrics: null,
      nlpInsights: null,
      logs: [],
      createdAt: new Date(),
      completedAt: null,
    };
    this.scanSessions.set(id, session);
    return session;
  }

  async getScanSession(id: number): Promise<ScanSession | undefined> {
    return this.scanSessions.get(id);
  }

  async updateScanSession(id: number, updates: Partial<ScanSession>): Promise<ScanSession | undefined> {
    const session = this.scanSessions.get(id);
    if (!session) return undefined;

    const updatedSession = { ...session, ...updates };
    this.scanSessions.set(id, updatedSession);
    return updatedSession;
  }

  async addLogEntry(sessionId: number, logEntry: LogEntry): Promise<void> {
    const session = this.scanSessions.get(sessionId);
    if (!session) return;

    const logs = session.logs || [];
    logs.push(logEntry);
    
    const updatedSession = { ...session, logs };
    this.scanSessions.set(sessionId, updatedSession);
  }

  async getAllScanSessions(): Promise<ScanSession[]> {
    return Array.from(this.scanSessions.values()).sort((a, b) => {
      const aTime = a.createdAt ? new Date(a.createdAt).getTime() : 0;
      const bTime = b.createdAt ? new Date(b.createdAt).getTime() : 0;
      return bTime - aTime;
    });
  }
}

export const storage = new MemStorage();
