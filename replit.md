# AI Web Inspector

## Overview

AI Web Inspector is a comprehensive web auditing tool that combines Selenium automation, security analysis, and NLP insights to provide detailed website assessments. The application features a modern React frontend with real-time WebSocket updates and a Node.js backend with Python-based analysis engines.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with shadcn/ui component library
- **State Management**: TanStack Query for server state management
- **Routing**: Wouter for lightweight client-side routing
- **Real-time Updates**: WebSocket integration for live scan progress

### Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time Communication**: WebSocket server for live updates
- **Analysis Engine**: Python-based analyzer using Selenium, spaCy, and BeautifulSoup

## Key Components

### Database Schema
- **scanSessions**: Core table storing scan metadata, progress, results, and analysis data
- **Fields**: URL, status, progress, security scores, performance metrics, vulnerabilities, NLP insights, and logs
- **JSON Columns**: Flexible storage for complex analysis results

### Analysis Pipeline
1. **URL Validation**: Input sanitization and URL verification
2. **Selenium Automation**: Automated browser interaction and data collection
3. **Security Assessment**: Vulnerability scanning and security scoring
4. **Performance Analysis**: Load time measurement and resource analysis
5. **NLP Processing**: Content analysis and insights extraction

### Real-time Communication
- WebSocket server for bidirectional communication
- Session-based subscription model for targeted updates
- Progress tracking and live log streaming
- Automatic reconnection handling

### Storage Strategy
- **Development**: In-memory storage for rapid prototyping
- **Production**: PostgreSQL with Drizzle ORM for data persistence
- **Database Connection**: Neon serverless PostgreSQL integration

## Data Flow

1. **Scan Initiation**: User submits URL with analysis options
2. **Session Creation**: Backend creates scan session and returns ID
3. **WebSocket Subscription**: Frontend subscribes to session updates
4. **Python Analysis**: Spawned Python process performs comprehensive analysis
5. **Progress Updates**: Real-time progress and log updates via WebSocket
6. **Results Storage**: Analysis results stored in database
7. **Frontend Updates**: Real-time UI updates based on WebSocket messages

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: Serverless PostgreSQL driver
- **drizzle-orm**: Type-safe database ORM
- **@tanstack/react-query**: Server state management
- **@radix-ui/***: Accessible UI component primitives
- **selenium**: Web automation framework (Python)
- **spacy**: Natural language processing library (Python)

### Development Tools
- **TypeScript**: Type safety and developer experience
- **ESBuild**: Fast bundling for production builds
- **Tailwind CSS**: Utility-first CSS framework
- **PostCSS**: CSS processing and optimization

## Deployment Strategy

### Environment Configuration
- **Development**: Local development with hot reload
- **Production**: Node.js production server with static asset serving
- **Database**: Neon PostgreSQL for scalable data storage

### Build Process
1. **Frontend Build**: Vite builds optimized React application
2. **Backend Build**: ESBuild bundles server code with external dependencies
3. **Static Assets**: Frontend assets served from dist/public directory

### Runtime Requirements
- Node.js 20+ for modern JavaScript features
- Python 3.11+ for analysis engine
- PostgreSQL 16+ for data persistence
- Selenium WebDriver for browser automation

## Changelog

```
Changelog:
- June 27, 2025. Initial setup and core functionality implementation
- June 27, 2025. Successfully implemented AI web auditing tool with:
  * Python-based analysis engine using requests and BeautifulSoup
  * Real-time WebSocket communication for live updates
  * Security vulnerability scanning (XSS, headers, HTTPS)
  * Performance metrics analysis
  * NLP-powered content analysis and architecture detection
  * Modern React frontend with dark theme
  * Comprehensive vulnerability reporting with export functionality
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```