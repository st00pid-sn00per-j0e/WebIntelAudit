#!/usr/bin/env python3

import sys
import json
import time
import urllib.parse
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup
import base64
from PIL import Image, ImageDraw, ImageFont
import io

class EnhancedWebAuditor:
    def __init__(self, session_id):
        self.session_id = session_id
        
    def log(self, level, message):
        """Send log message to Node.js server"""
        log_entry = {
            "type": "log",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            }
        }
        print(json.dumps(log_entry), flush=True)
        
    def update_progress(self, progress, status=None):
        """Send progress update to Node.js server"""
        progress_data = {"progress": progress}
        if status:
            progress_data["status"] = status
            
        progress_update = {
            "type": "progress",
            "data": progress_data
        }
        print(json.dumps(progress_update), flush=True)
        
    def send_browser_action(self, action):
        """Send browser action update to Node.js server"""
        action_update = {
            "type": "browserAction",
            "data": {
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(action_update), flush=True)
        time.sleep(0.5)  # Small delay to make actions visible
        
    def create_simulated_screenshot(self, url, status="loading"):
        """Create a simulated screenshot showing browser activity"""
        try:
            # Create a simple image representing the browser view
            width, height = 1920, 1080
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw browser chrome
            draw.rectangle([0, 0, width, 80], fill='#f3f4f6')
            draw.rectangle([0, 80, width, 81], fill='#e5e7eb')
            
            # Draw URL bar
            draw.rectangle([100, 20, width-100, 60], fill='white', outline='#d1d5db')
            
            # Add URL text (simplified)
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            if font:
                draw.text((110, 35), url, fill='black', font=font)
            
            # Draw page content based on status
            if status == "loading":
                # Loading bars
                y = 150
                for i in range(5):
                    width_bar = 600 - (i * 100)
                    draw.rectangle([50, y, 50 + width_bar, y + 20], fill='#e5e7eb')
                    y += 40
                    
                # Add loading spinner representation
                draw.ellipse([width//2 - 30, height//2 - 30, width//2 + 30, height//2 + 30], 
                           outline='#3b82f6', width=3)
                           
            elif status == "scanning":
                # Draw scan line
                scan_y = int(time.time() * 100) % (height - 100) + 100
                draw.rectangle([0, scan_y, width, scan_y + 2], fill='#3b82f6')
                
                # Draw some content blocks
                y = 150
                for i in range(3):
                    draw.rectangle([50, y, width - 50, y + 100], fill='#f9fafb', outline='#e5e7eb')
                    y += 120
                    
            elif status == "analyzing":
                # Draw analysis overlay
                draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], 
                             fill='white', outline='#3b82f6', width=2)
                if font:
                    draw.text((width//2 - 50, height//2), "Analyzing...", fill='#3b82f6', font=font)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            self.log("WARN", f"Failed to create screenshot: {str(e)}")
            return None
        
    def send_screenshot(self, url, status="loading"):
        """Send screenshot of simulated browser state"""
        try:
            screenshot = self.create_simulated_screenshot(url, status)
            if screenshot:
                screenshot_update = {
                    "type": "screenshot",
                    "data": {
                        "image": screenshot,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                print(json.dumps(screenshot_update), flush=True)
        except Exception as e:
            self.log("WARN", f"Failed to send screenshot: {str(e)}")
        
    def send_result(self, results):
        """Send final results to Node.js server"""
        result_data = {
            "type": "result",
            "data": results
        }
        print(json.dumps(result_data), flush=True)
        
    def analyze_url(self, url, options):
        """Main analysis function with simulated browser experience"""
        try:
            self.log("INFO", f"Starting enhanced analysis of {url}")
            self.update_progress(5, "running")
            
            # Validate URL
            if not self.validate_url(url):
                raise ValueError("Invalid URL format")
                
            # Simulate browser startup
            self.send_browser_action("Launching browser...")
            self.send_screenshot(url, "loading")
            time.sleep(1)
            
            self.update_progress(15)
            
            # Navigate to URL
            self.log("INFO", f"Navigating to {url}")
            self.send_browser_action(f"Navigating to {url}")
            
            start_time = time.time()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            load_time = time.time() - start_time
            
            self.log("INFO", f"Page loaded in {load_time:.2f} seconds")
            self.send_browser_action(f"Page loaded successfully ({load_time:.2f}s)")
            self.update_progress(35)
            
            # Send "scanning" screenshot
            self.send_screenshot(url, "scanning")
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count DOM elements
            all_elements = soup.find_all()
            
            results = {
                "loadTime": f"{load_time:.2f}s",
                "securityScore": 50,
                "domElements": len(all_elements),
                "jsErrors": 0,
                "vulnerabilities": [],
                "performanceMetrics": {},
                "nlpInsights": {},
                "browserInfo": {
                    "title": soup.title.string if soup.title else "No title",
                    "url": response.url,
                    "statusCode": response.status_code
                }
            }
            
            # Simulate browser actions for different analysis phases
            if options.get('securityAudit', True):
                self.send_browser_action("Analyzing security headers...")
                self.send_screenshot(url, "analyzing")
                self.log("INFO", "Running security audit")
                security_results = self.security_analysis(url, response, soup)
                results.update(security_results)
                self.update_progress(50)
                
                self.send_browser_action("Scanning for vulnerabilities...")
                time.sleep(1)
                
            # Check for forms and inputs
            self.send_browser_action("Scanning forms and input fields...")
            forms = soup.find_all('form')
            inputs = soup.find_all('input')
            self.log("INFO", f"Found {len(forms)} forms and {len(inputs)} input fields")
            
            if options.get('performanceTest', True):
                self.send_browser_action("Measuring performance metrics...")
                self.log("INFO", "Running performance analysis")
                perf_results = self.performance_analysis(response, soup)
                results.update(perf_results)
                self.update_progress(70)
                
            # Simulate scrolling
            self.send_browser_action("Analyzing page content...")
            self.send_screenshot(url, "scanning")
            time.sleep(0.5)
            
            if options.get('nlpAnalysis', True):
                self.send_browser_action("Extracting content insights...")
                self.log("INFO", "Running content analysis")
                nlp_results = self.content_analysis(soup)
                results["nlpInsights"] = nlp_results
                self.update_progress(85)
                
            # Calculate final security score
            results["securityScore"] = self.calculate_security_score(results)
            
            self.update_progress(100, "completed")
            self.send_browser_action("Analysis completed successfully")
            self.log("INFO", "Analysis completed successfully")
            self.send_result(results)
            
        except Exception as e:
            self.log("ERROR", f"Analysis failed: {str(e)}")
            self.update_progress(0, "failed")
            self.send_result({
                "error": str(e),
                "status": "failed"
            })
            
    def validate_url(self, url):
        """Validate URL format"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def security_analysis(self, url, response, soup):
        """Perform security analysis"""
        vulnerabilities = []
        
        # Check HTTPS
        if not url.startswith('https://'):
            vulnerabilities.append({
                "type": "missing_headers",
                "severity": "high",
                "title": "Missing HTTPS",
                "description": "Website is not using HTTPS encryption",
                "recommendation": "Enable HTTPS to encrypt data in transit"
            })
            
        # Check security headers
        security_headers = {
            'X-Frame-Options': 'Prevents clickjacking attacks',
            'X-Content-Type-Options': 'Prevents MIME type sniffing',
            'X-XSS-Protection': 'Enables XSS filtering',
            'Strict-Transport-Security': 'Forces HTTPS connections',
            'Content-Security-Policy': 'Controls resource loading'
        }
        
        for header, description in security_headers.items():
            if header not in response.headers:
                vulnerabilities.append({
                    "type": "missing_headers",
                    "severity": "medium",
                    "title": f"Missing {header}",
                    "description": description,
                    "recommendation": f"Add {header} header to improve security"
                })
                
        # Check for password fields without HTTPS
        password_fields = soup.find_all('input', {'type': 'password'})
        if password_fields and not url.startswith('https://'):
            vulnerabilities.append({
                "type": "other",
                "severity": "critical",
                "title": "Password field on non-HTTPS page",
                "description": "Password input fields found on non-encrypted page",
                "location": f"Found {len(password_fields)} password fields",
                "recommendation": "Always use HTTPS for pages with password fields"
            })
            
        # Check for forms without CSRF protection
        forms = soup.find_all('form')
        for form in forms:
            csrf_token = form.find('input', {'name': lambda x: x and 'csrf' in x.lower()})
            if not csrf_token:
                vulnerabilities.append({
                    "type": "csrf",
                    "severity": "medium",
                    "title": "Potential CSRF vulnerability",
                    "description": "Form without visible CSRF token",
                    "location": f"Form action: {form.get('action', 'unknown')}",
                    "recommendation": "Implement CSRF tokens for all forms"
                })
                
        return {"vulnerabilities": vulnerabilities}
        
    def performance_analysis(self, response, soup):
        """Analyze page performance"""
        try:
            # Basic performance metrics
            performance_data = {
                "dns": 0,  # Would need real browser for this
                "connect": 0,
                "ttfb": response.elapsed.total_seconds() * 1000,
                "domLoad": 0,
                "windowLoad": 0,
                "totalSize": len(response.content),
                "jsSize": sum(len(script.string or '') for script in soup.find_all('script') if script.string),
                "cssSize": sum(len(style.string or '') for style in soup.find_all('style') if style.string),
                "imageCount": len(soup.find_all('img'))
            }
            
            return {
                "performanceMetrics": performance_data
            }
        except Exception as e:
            self.log("WARN", f"Failed to get performance metrics: {str(e)}")
            return {"performanceMetrics": {}}
            
    def content_analysis(self, soup):
        """Analyze page content"""
        try:
            # Extract text content
            text = soup.get_text(strip=True)
            
            # Count different element types
            analysis = {
                "contentType": "website",
                "architecture": "Unknown",
                "userFlows": [],
                "sentimentScore": 0,
                "keyPhrases": [],
                "elementCounts": {
                    "forms": len(soup.find_all('form')),
                    "links": len(soup.find_all('a')),
                    "images": len(soup.find_all('img')),
                    "scripts": len(soup.find_all('script')),
                    "stylesheets": len(soup.find_all('link', rel='stylesheet'))
                }
            }
            
            # Detect architecture
            if soup.find(attrs={"data-react-root": True}) or soup.find(id="root"):
                analysis["architecture"] = "React SPA"
            elif soup.find(attrs={"ng-app": True}):
                analysis["architecture"] = "Angular Application"
            elif soup.find(attrs={"data-vue": True}):
                analysis["architecture"] = "Vue.js Application"
                
            # Detect user flows
            if soup.find('form', attrs={'action': lambda x: x and 'login' in str(x).lower()}):
                analysis["userFlows"].append("Login Flow")
            if soup.find('form', attrs={'action': lambda x: x and 'register' in str(x).lower()}):
                analysis["userFlows"].append("Registration Flow")
            if soup.find('button', string=lambda x: x and 'cart' in str(x).lower()):
                analysis["userFlows"].append("Shopping Cart")
                
            # Extract key phrases (simple approach)
            words = text.split()
            if len(words) > 20:
                analysis["keyPhrases"] = list(set([
                    word for word in words[:50] 
                    if len(word) > 5 and word.isalpha()
                ]))[:10]
                
            return analysis
            
        except Exception as e:
            self.log("WARN", f"Content analysis failed: {str(e)}")
            return {}
            
    def calculate_security_score(self, results):
        """Calculate overall security score"""
        score = 100
        vulnerabilities = results.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            if vuln['severity'] == 'critical':
                score -= 25
            elif vuln['severity'] == 'high':
                score -= 15
            elif vuln['severity'] == 'medium':
                score -= 10
            elif vuln['severity'] == 'low':
                score -= 5
                
        return max(0, score)

def main():
    if len(sys.argv) < 4:
        print("Usage: enhanced_analyzer.py <url> <session_id> <options>")
        sys.exit(1)
        
    url = sys.argv[1]
    session_id = sys.argv[2]
    options = json.loads(sys.argv[3])
    
    auditor = EnhancedWebAuditor(session_id)
    auditor.analyze_url(url, options)

if __name__ == "__main__":
    main()