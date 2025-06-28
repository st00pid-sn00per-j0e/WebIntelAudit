#!/usr/bin/env python3
import json
import sys
import time
import os
import base64
from datetime import datetime
from urllib.parse import urlparse
import asyncio
from playwright.async_api import async_playwright
import re
from collections import Counter
import hashlib
import sys
sys.path.append(os.path.dirname(__file__))
from nlp_module import LightweightNLP

class OptimizedWebAnalyzer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.start_time = time.time()
        self.logs_dir = "logs"
        self.log_file = None
        self.context = None
        self.browser = None
        self.playwright = None
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(self.logs_dir, f"scan_{session_id}_{timestamp}.json")
        
    def log(self, level, message, data=None):
        """Send log message to Node.js server and save to file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": level,
            "message": message,
            "data": data
        }
        
        # Send to Node.js
        print(json.dumps({
            "type": "log",
            "data": {
                "level": level,
                "message": message,
                "timestamp": log_entry["timestamp"]
            }
        }), flush=True)
        
        # Save to file
        with open(self.log_file_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def update_progress(self, progress, status=None):
        """Send progress update to Node.js server"""
        print(json.dumps({
            "type": "progress",
            "data": {
                "progress": progress,
                "status": status
            }
        }), flush=True)
    
    def send_browser_action(self, action):
        """Send browser action update to Node.js server"""
        print(json.dumps({
            "type": "browserAction",
            "data": action
        }), flush=True)
    
    async def send_screenshot(self, page, status="analyzing"):
        """Send optimized screenshot of current browser state"""
        try:
            # Take screenshot with reduced quality for memory efficiency
            screenshot = await page.screenshot(
                quality=30,  # Reduced quality for smaller size
                type='jpeg',  # JPEG is more efficient than PNG
                full_page=False  # Only visible viewport
            )
            
            # Convert to base64
            screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            print(json.dumps({
                "type": "screenshot",
                "data": {
                    "screenshot": f"data:image/jpeg;base64,{screenshot_base64}",
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }
            }), flush=True)
            
        except Exception as e:
            self.log("ERROR", f"Failed to capture screenshot: {str(e)}")
    
    def send_result(self, results):
        """Send final results to Node.js server and save to file"""
        # Save results to file
        results_file = os.path.join(self.logs_dir, f"results_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Send to Node.js
        print(json.dumps({
            "type": "result",
            "data": results
        }), flush=True)
    
    async def analyze_url(self, url, options):
        """Main analysis function using Playwright"""
        try:
            self.log("INFO", f"Starting optimized analysis for {url}")
            self.update_progress(0, "Initializing browser")
            
            # Validate URL
            if not self.validate_url(url):
                raise ValueError("Invalid URL format")
            
            # Setup Playwright with optimizations
            self.playwright = await async_playwright().start()
            
            # Browser launch options for memory efficiency
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=site-per-process',
                    '--disable-blink-features=AutomationControlled',
                    '--window-size=1280,720',  # Fixed smaller window size
                    '--max_old_space_size=512',  # Limit memory usage
                    '--disable-images',  # Disable image loading for performance
                    '--disable-javascript',  # Initial load without JS
                ]
            )
            
            # Create context with resource optimization
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                ignore_https_errors=True,
                java_script_enabled=False,  # Start with JS disabled
                bypass_csp=True,
                reduced_motion='reduce'
            )
            
            # Block unnecessary resources
            await self.context.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}", 
                                   lambda route: route.abort())
            
            page = await self.context.new_page()
            
            # Navigate and analyze
            self.update_progress(10, "Loading page")
            self.send_browser_action({"action": "navigate", "url": url})
            
            # Initial load without JavaScript
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            await self.send_screenshot(page, "initial_load")
            
            # Get initial metrics
            performance_metrics = await self.performance_analysis(page, response)
            
            # Enable JavaScript for dynamic content if needed
            if options.get('deepInspection', False):
                self.update_progress(30, "Analyzing dynamic content")
                await page.evaluate("() => { window.__PLAYWRIGHT__ = true; }")
                await page.reload(wait_until='networkidle', timeout=20000)
                await self.send_screenshot(page, "with_javascript")
            
            # Security analysis
            security_results = None
            if options.get('securityAudit', True):
                self.update_progress(50, "Performing security analysis")
                security_results = await self.security_analysis(url, page, response)
            
            # Content analysis with lightweight NLP
            nlp_results = None
            if options.get('nlpAnalysis', True):
                self.update_progress(70, "Analyzing content")
                nlp_results = await self.content_analysis(page)
            
            # Calculate security score
            security_score = self.calculate_security_score(security_results) if security_results else 0
            
            # Compile results
            results = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "security": {
                    "score": security_score,
                    "vulnerabilities": security_results.get('vulnerabilities', []) if security_results else [],
                    "headers": security_results.get('headers', {}) if security_results else {},
                    "https": security_results.get('https', {}) if security_results else {}
                },
                "performance": performance_metrics,
                "nlp": nlp_results or {},
                "analyzed_with": "playwright_optimized"
            }
            
            self.update_progress(100, "Analysis complete")
            self.send_result(results)
            
        except Exception as e:
            self.log("ERROR", f"Analysis failed: {str(e)}")
            self.send_result({
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            })
        finally:
            # Cleanup
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
    
    def validate_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    async def security_analysis(self, url, page, response):
        """Perform security analysis"""
        self.log("INFO", "Starting security analysis")
        vulnerabilities = []
        
        # Check security headers
        headers = response.headers if response else {}
        missing_headers = []
        
        security_headers = [
            'strict-transport-security',
            'x-content-type-options',
            'x-frame-options',
            'x-xss-protection',
            'content-security-policy',
            'referrer-policy'
        ]
        
        for header in security_headers:
            if header not in headers:
                missing_headers.append(header)
                vulnerabilities.append({
                    "type": "missing_headers",
                    "severity": "medium",
                    "title": f"Missing Security Header: {header}",
                    "description": f"The {header} header is not set",
                    "recommendation": f"Add the {header} header to improve security"
                })
        
        # Check HTTPS
        https_info = {
            "enabled": url.startswith('https://'),
            "issues": []
        }
        
        if not https_info['enabled']:
            vulnerabilities.append({
                "type": "other",
                "severity": "high",
                "title": "No HTTPS",
                "description": "The site is not using HTTPS encryption",
                "recommendation": "Enable HTTPS to encrypt data in transit"
            })
        
        # Basic XSS check
        try:
            # Check for basic XSS vulnerabilities in forms
            forms = await page.query_selector_all('form')
            for form in forms[:5]:  # Limit to first 5 forms for performance
                action = await form.get_attribute('action')
                if action and ('javascript:' in action.lower() or 'data:' in action.lower()):
                    vulnerabilities.append({
                        "type": "xss",
                        "severity": "high",
                        "title": "Potential XSS in form action",
                        "description": "Form action contains potentially dangerous protocol",
                        "location": f"Form with action: {action[:50]}..."
                    })
        except Exception as e:
            self.log("WARN", f"XSS check failed: {str(e)}")
        
        return {
            "vulnerabilities": vulnerabilities,
            "headers": dict(headers),
            "https": https_info
        }
    
    async def performance_analysis(self, page, response):
        """Analyze page performance"""
        self.log("INFO", "Analyzing performance metrics")
        
        try:
            # Get timing metrics using Performance API
            timing = await page.evaluate('''() => {
                const perf = window.performance;
                const timing = perf.timing || {};
                const navigation = perf.getEntriesByType('navigation')[0] || {};
                
                return {
                    dns: timing.domainLookupEnd - timing.domainLookupStart || 0,
                    connect: timing.connectEnd - timing.connectStart || 0,
                    ttfb: timing.responseStart - timing.requestStart || navigation.responseStart || 0,
                    domLoad: timing.domContentLoadedEventEnd - timing.navigationStart || 0,
                    totalLoad: timing.loadEventEnd - timing.navigationStart || 0
                };
            }''')
            
            # Get resource sizes
            resources = await page.evaluate('''() => {
                const resources = window.performance.getEntriesByType('resource');
                let jsSize = 0, cssSize = 0, imageSize = 0, totalSize = 0;
                
                resources.forEach(r => {
                    const size = r.transferSize || 0;
                    totalSize += size;
                    
                    if (r.name.match(/\\.js$/i)) jsSize += size;
                    else if (r.name.match(/\\.css$/i)) cssSize += size;
                    else if (r.name.match(/\\.(jpg|jpeg|png|gif|svg|webp)$/i)) imageSize += size;
                });
                
                return { jsSize, cssSize, imageSize, totalSize };
            }''')
            
            return {
                **timing,
                **resources,
                "responseTime": time.time() - self.start_time
            }
            
        except Exception as e:
            self.log("WARN", f"Performance analysis error: {str(e)}")
            return {
                "dns": 0,
                "connect": 0,
                "ttfb": 0,
                "domLoad": 0,
                "totalSize": 0,
                "jsSize": 0,
                "cssSize": 0,
                "imageSize": 0
            }
    
    async def content_analysis(self, page):
        """Content analysis using lightweight NLP module"""
        self.log("INFO", "Analyzing page content with NLP")
        
        try:
            # Extract text content
            text_content = await page.evaluate('''() => {
                // Remove script and style elements
                const scripts = document.querySelectorAll('script, style');
                scripts.forEach(el => el.remove());
                
                // Get text content
                return document.body ? document.body.innerText : '';
            }''')
            
            # Use our lightweight NLP module
            nlp = LightweightNLP()
            nlp_results = nlp.analyze_web_content(text_content)
            
            # Detect content type and architecture
            content_type = await self.detect_content_type(page, text_content)
            architecture = await self.detect_architecture(page)
            
            return {
                "contentType": content_type,
                "architecture": architecture,
                "keyPhrases": list(nlp_results['keywords'].keys())[:10],
                "wordCount": nlp_results['word_count'],
                "uniqueWords": nlp_results['unique_words'],
                "sentiment": nlp_results['sentiment'],
                "topics": nlp_results['topics'],
                "entities": nlp_results['entities'],
                "summary": nlp_results['summary']
            }
            
        except Exception as e:
            self.log("WARN", f"Content analysis error: {str(e)}")
            return {
                "contentType": "unknown",
                "architecture": "unknown",
                "keyPhrases": [],
                "wordCount": 0,
                "sentiment": {"overall": "neutral"},
                "topics": {}
            }
    
    async def detect_content_type(self, page, text_content):
        """Detect website content type"""
        text_lower = text_content.lower()
        
        # Check for e-commerce indicators
        if any(word in text_lower for word in ['cart', 'checkout', 'buy now', 'add to cart', 'price', 'product']):
            return "e-commerce"
        
        # Check for blog/news indicators
        if any(word in text_lower for word in ['blog', 'article', 'posted', 'comments', 'author', 'published']):
            return "blog/news"
        
        # Check for corporate indicators
        if any(word in text_lower for word in ['about us', 'contact us', 'services', 'company', 'team', 'mission']):
            return "corporate"
        
        # Check for social media indicators
        if any(word in text_lower for word in ['profile', 'follow', 'share', 'like', 'comment', 'friends']):
            return "social"
        
        return "general"
    
    async def detect_architecture(self, page):
        """Detect web architecture patterns"""
        try:
            # Check for common frameworks
            html = await page.content()
            
            if 'react' in html.lower() or '__react' in html.lower():
                return "React"
            elif 'ng-' in html or 'angular' in html.lower():
                return "Angular"
            elif 'vue' in html.lower() or 'v-' in html:
                return "Vue.js"
            elif 'wp-content' in html or 'wordpress' in html.lower():
                return "WordPress"
            
            return "Traditional"
            
        except:
            return "Unknown"
    
    def calculate_security_score(self, results):
        """Calculate overall security score"""
        if not results:
            return 0
        
        score = 100
        vulnerabilities = results.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            if severity == 'critical':
                score -= 25
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 10
            elif severity == 'low':
                score -= 5
        
        return max(0, score)

async def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    session_id = int(sys.argv[1])
    url = sys.argv[2]
    options = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    
    analyzer = OptimizedWebAnalyzer(session_id)
    await analyzer.analyze_url(url, options)

if __name__ == "__main__":
    asyncio.run(main())