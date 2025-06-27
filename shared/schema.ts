import { pgTable, text, serial, integer, boolean, timestamp, json } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const scanSessions = pgTable("scan_sessions", {
  id: serial("id").primaryKey(),
  url: text("url").notNull(),
  status: text("status").notNull().default("pending"), // pending, running, completed, failed
  progress: integer("progress").default(0),
  securityScore: integer("security_score"),
  loadTime: text("load_time"),
  domElements: integer("dom_elements"),
  jsErrors: integer("js_errors"),
  vulnerabilities: json("vulnerabilities").$type<VulnerabilityResult[]>(),
  performanceMetrics: json("performance_metrics").$type<PerformanceMetrics>(),
  nlpInsights: json("nlp_insights").$type<NLPInsights>(),
  logs: json("logs").$type<LogEntry[]>().default([]),
  createdAt: timestamp("created_at").defaultNow(),
  completedAt: timestamp("completed_at"),
});

export const insertScanSessionSchema = createInsertSchema(scanSessions).pick({
  url: true,
});

export type InsertScanSession = z.infer<typeof insertScanSessionSchema>;
export type ScanSession = typeof scanSessions.$inferSelect;

// Supporting types
export interface VulnerabilityResult {
  type: 'xss' | 'missing_headers' | 'csrf' | 'sql_injection' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location?: string;
  evidence?: string;
  recommendation?: string;
}

export interface PerformanceMetrics {
  dns: number;
  connect: number;
  ssl: number;
  ttfb: number;
  download: number;
  domLoad: number;
  totalSize: number;
  jsSize: number;
  cssSize: number;
  imageSize: number;
}

export interface NLPInsights {
  contentType: string;
  architecture: string;
  userFlows: string[];
  sentimentScore: number;
  keyPhrases: string[];
}

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'DEBUG' | 'WARN' | 'ERROR' | 'PROCESSING';
  message: string;
}

export interface AnalysisOptions {
  securityAudit: boolean;
  performanceTest: boolean;
  nlpAnalysis: boolean;
  deepInspection: boolean;
}
