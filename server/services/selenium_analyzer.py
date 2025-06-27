#!/usr/bin/env python3

import sys
import json
import time
import urllib.parse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from bs4 import BeautifulSoup
import base64
import io

class SeleniumWebAuditor:
    def __init__(self, session_id):
        self.session_id = session_id
        self.driver = None
        
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
        
    def send_screenshot(self):
        """Send screenshot of current browser state"""
        try:
            if self.driver:
                screenshot = self.driver.get_screenshot_as_base64()
                screenshot_update = {
                    "type": "screenshot",
                    "data": {
                        "image": screenshot,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                print(json.dumps(screenshot_update), flush=True)
        except Exception as e:
            self.log("WARN", f"Failed to capture screenshot: {str(e)}")
        
    def send_result(self, results):
        """Send final results to Node.js server"""
        result_data = {
            "type": "result",
            "data": results
        }
        print(json.dumps(result_data), flush=True)
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set binary location to the installed Chromium
        chrome_options.binary_location = '/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium'
        
        try:
            # Use ChromeDriverManager to automatically download and manage chromedriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.log("INFO", "Browser instance created successfully")
            self.send_browser_action("Browser launched in headless mode")
            return True
        except ImportError:
            # Fallback to direct Chrome driver
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.log("INFO", "Browser instance created successfully")
                self.send_browser_action("Browser launched in headless mode")
                return True
            except Exception as e:
                self.log("ERROR", f"Failed to create browser instance: {str(e)}")
                return False
        except Exception as e:
            self.log("ERROR", f"Failed to create browser instance: {str(e)}")
            return False
            
    def analyze_url(self, url, options):
        """Main analysis function using Selenium"""
        try:
            self.log("INFO", f"Starting Selenium-based analysis of {url}")
            self.update_progress(5, "running")
            
            # Validate URL
            if not self.validate_url(url):
                raise ValueError("Invalid URL format")
                
            # Setup browser
            self.send_browser_action("Initializing browser...")
            if not self.setup_driver():
                raise Exception("Failed to setup browser driver")
                
            self.update_progress(15)
            
            # Navigate to URL
            self.log("INFO", f"Navigating to {url}")
            self.send_browser_action(f"Navigating to {url}")
            
            start_time = time.time()
            self.driver.get(url)
            
            # Wait for page to load
            self.send_browser_action("Waiting for page to load...")
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                self.log("WARN", "Page load timeout - continuing with partial content")
                
            load_time = time.time() - start_time
            self.log("INFO", f"Page loaded in {load_time:.2f} seconds")
            self.send_browser_action(f"Page loaded successfully ({load_time:.2f}s)")
            self.update_progress(35)
            
            # Take screenshot
            self.send_screenshot()
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            results = {
                "loadTime": f"{load_time:.2f}s",
                "securityScore": 50,
                "domElements": len(self.driver.find_elements(By.XPATH, "//*")),
                "jsErrors": 0,
                "vulnerabilities": [],
                "performanceMetrics": {},
                "nlpInsights": {},
                "browserInfo": {
                    "title": self.driver.title,
                    "url": self.driver.current_url,
                    "windowSize": self.driver.get_window_size()
                }
            }
            
            # Analyze page elements
            if options.get('securityAudit', True):
                self.send_browser_action("Analyzing security headers...")
                self.log("INFO", "Running security audit")
                security_results = self.security_analysis(url, soup)
                results.update(security_results)
                self.update_progress(50)
                self.send_screenshot()
                
            # Check for forms and inputs
            self.send_browser_action("Scanning for forms and input fields...")
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            self.log("INFO", f"Found {len(forms)} forms and {len(inputs)} input fields")
            
            # Analyze JavaScript
            if options.get('performanceTest', True):
                self.send_browser_action("Analyzing JavaScript and performance...")
                self.log("INFO", "Running performance analysis")
                perf_results = self.performance_analysis()
                results.update(perf_results)
                self.update_progress(70)
                
            # Scroll through page
            self.send_browser_action("Scrolling through page content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(0.5)
            self.send_screenshot()
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            self.send_screenshot()
            
            # Check for interactive elements
            if options.get('nlpAnalysis', True):
                self.send_browser_action("Analyzing page content and structure...")
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
        finally:
            if self.driver:
                self.send_browser_action("Closing browser...")
                self.driver.quit()
                
    def validate_url(self, url):
        """Validate URL format"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def security_analysis(self, url, soup):
        """Perform security analysis using Selenium"""
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
            
        # Check for password fields without HTTPS
        password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
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
        
    def performance_analysis(self):
        """Analyze page performance using Selenium"""
        try:
            # Execute JavaScript to get performance metrics
            performance_data = self.driver.execute_script("""
                var performance = window.performance || {};
                var timing = performance.timing || {};
                var navigation = performance.navigation || {};
                
                return {
                    dns: timing.domainLookupEnd - timing.domainLookupStart,
                    connect: timing.connectEnd - timing.connectStart,
                    ttfb: timing.responseStart - timing.navigationStart,
                    domLoad: timing.domContentLoadedEventEnd - timing.navigationStart,
                    windowLoad: timing.loadEventEnd - timing.navigationStart,
                    totalSize: 0
                };
            """)
            
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
            if soup.find('form', attrs={'action': lambda x: x and 'login' in x.lower()}):
                analysis["userFlows"].append("Login Flow")
            if soup.find('form', attrs={'action': lambda x: x and 'register' in x.lower()}):
                analysis["userFlows"].append("Registration Flow")
            if soup.find('button', string=lambda x: x and 'cart' in x.lower()):
                analysis["userFlows"].append("Shopping Cart")
                
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
        print("Usage: selenium_analyzer.py <url> <session_id> <options>")
        sys.exit(1)
        
    url = sys.argv[1]
    session_id = sys.argv[2]
    options = json.loads(sys.argv[3])
    
    auditor = SeleniumWebAuditor(session_id)
    auditor.analyze_url(url, options)

if __name__ == "__main__":
    main()