
#!/usr/bin/env python3

import chromedriver_autoinstaller
import sys
import json
import time
import urllib.parse
import os
from datetime import datetime
try:
    from selenium import webdriver as selenium_webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    By = None

import requests
from bs4 import BeautifulSoup
import base64
import io

class AppiumWebAuditor:
    def __init__(self, session_id):
        self.session_id = session_id
        self.driver = None
        
    def log(self, level, message):
        """Send log message to Node.js server"""
        log_data = {
            "type": "log",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            }
        }
        print(json.dumps(log_data))
        sys.stdout.flush()
        
    def update_progress(self, progress, status=None):
        """Send progress update to Node.js server"""
        update_data = {
            "type": "progress",
            "data": {
                "progress": progress,
                "status": status
            }
        }
        print(json.dumps(update_data))
        sys.stdout.flush()
        
    def send_browser_action(self, action):
        """Send browser action update to Node.js server"""
        action_data = {
            "type": "browserAction",
            "data": {
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(action_data))
        sys.stdout.flush()
        
    def send_screenshot(self):
        """Send screenshot of current browser state"""
        try:
            if self.driver:
                screenshot = self.driver.get_screenshot_as_base64()
                screenshot_data = {
                    "type": "screenshot",
                    "data": {
                        "image": f"data:image/png;base64,{screenshot}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                print(json.dumps(screenshot_data))
                sys.stdout.flush()
        except Exception as e:
            self.log("ERROR", f"Failed to capture screenshot: {str(e)}")
            
    def send_result(self, results):
        """Send final results to Node.js server"""
        result_data = {
            "type": "result",
            "data": results
        }
        print(json.dumps(result_data))
        sys.stdout.flush()
        
    def setup_driver(self):
        """Setup Chrome WebDriver for web automation"""
        try:
            if not SELENIUM_AVAILABLE:
                self.log("ERROR", "Selenium is not available")
                return False

            # Ensure the correct version of ChromeDriver is installed
            chromedriver_autoinstaller.install()

            # Chrome options optimized for Replit environment
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')  # Use new headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Check for Chrome binary path from environment or search common locations
            chrome_binary = os.environ.get("CHROME_BINARY_PATH")
            if not chrome_binary:
                chrome_binaries = [
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable'
                ]
                
                for binary in chrome_binaries:
                    if os.path.exists(binary):
                        chrome_binary = binary
                        break
            
            if chrome_binary:
                chrome_options.binary_location = chrome_binary
                self.log("INFO", f"Found Chrome binary at: {chrome_binary}")

            # Attempt to establish a WebDriver session
            try:
                self.driver = selenium_webdriver.Chrome(options=chrome_options)
            except WebDriverException as e:
                self.log("ERROR", f"Failed to setup browser driver: {str(e)}")
                return False

            # Test if driver is working
            self.driver.set_page_load_timeout(30)
            self.log("INFO", "Browser driver successfully initialized")
            self.send_browser_action("Browser launched successfully")
            return True
                
        except Exception as e:
            self.log("ERROR", f"Failed to setup browser driver: {str(e)}")
            self.log("ERROR", f"Chrome may not be properly installed. Error details: {type(e).__name__}")
            return False
            
    def analyze_url(self, url, options):
        """Main analysis function using Chrome WebDriver"""
        try:
            self.log("INFO", f"Starting Chrome-based analysis of {url}")
            self.update_progress(5, "running")
            
            # Validate URL
            if not self.validate_url(url):
                raise ValueError("Invalid URL format")
                
            # Setup browser
            self.send_browser_action("Initializing browser...")
            if not self.setup_driver():
                raise Exception("Failed to setup browser driver")
                
            self.update_progress(10)
            
            # Navigate to URL
            self.send_browser_action(f"Navigating to {url}...")
            self.log("INFO", f"Navigating to URL: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            self.send_browser_action("Waiting for page to load...")
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                self.log("WARN", "Page load timeout - continuing with analysis")
                
            self.update_progress(20)
            self.send_screenshot()
            
            # Get page source for analysis
            self.send_browser_action("Extracting page content...")
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Initialize results
            results = {
                "vulnerabilities": [],
                "performanceMetrics": {},
                "nlpInsights": {},
                "browserInfo": {
                    "title": self.driver.title,
                    "url": self.driver.current_url,
                    "windowSize": self.driver.get_window_size() if hasattr(self.driver, 'get_window_size') else {}
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
            
            # Analyze JavaScript and performance
            if options.get('performanceTest', True):
                self.send_browser_action("Analyzing JavaScript and performance...")
                self.log("INFO", "Running performance analysis")
                perf_results = self.performance_analysis()
                results.update(perf_results)
                self.update_progress(70)
                self.send_screenshot()
                
            # Content analysis
            if options.get('nlpAnalysis', True):
                self.send_browser_action("Analyzing page content...")
                self.log("INFO", "Running content analysis")
                content_results = self.content_analysis(soup)
                results.update(content_results)
                self.update_progress(90)
                
            # Security headers analysis via requests
            if options.get('deepInspection', False):
                self.send_browser_action("Deep security headers analysis...")
                self.log("INFO", "Running deep security analysis")
                headers_results = self.analyze_security_headers(url)
                if headers_results:
                    results["vulnerabilities"].extend(headers_results)
                
            # Final screenshot
            self.send_browser_action("Analysis complete!")
            self.send_screenshot()
            
            # Calculate security score
            security_score = self.calculate_security_score(results)
            
            self.update_progress(100, "completed")
            self.send_result({
                "securityScore": security_score,
                "vulnerabilities": results.get("vulnerabilities", []),
                "performanceMetrics": results.get("performanceMetrics", {}),
                "nlpInsights": results.get("nlpInsights", {})
            })
            
        except Exception as e:
            self.log("ERROR", f"Analysis failed: {str(e)}")
            self.update_progress(100, "failed")
            self.send_result({
                "error": str(e),
                "securityScore": 0,
                "vulnerabilities": [],
                "performanceMetrics": {},
                "nlpInsights": {}
            })
        finally:
            # Cleanup
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
            
    def analyze_security_headers(self, url):
        """Analyze security headers using requests"""
        vulnerabilities = []
        try:
            response = requests.head(url, timeout=10)
            
            # Check for important security headers
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
        except Exception as e:
            self.log("WARN", f"Failed to analyze headers: {str(e)}")
            
        return vulnerabilities
            
    def security_analysis(self, url, soup):
        """Perform security analysis using Chrome WebDriver"""
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
                
        # Check for inline JavaScript (potential XSS)
        inline_scripts = soup.find_all('script', string=True)
        if inline_scripts:
            vulnerabilities.append({
                "type": "xss",
                "severity": "medium",
                "title": "Inline JavaScript detected",
                "description": f"Found {len(inline_scripts)} inline script tags",
                "location": "Multiple locations",
                "recommendation": "Move JavaScript to external files and implement CSP"
            })
                
        return {"vulnerabilities": vulnerabilities}
        
    def performance_analysis(self):
        """Analyze page performance using Chrome WebDriver"""
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
                    redirectCount: navigation.redirectCount || 0
                };
            """)
            
            # Get resource sizes
            resource_data = self.driver.execute_script("""
                var resources = performance.getEntriesByType('resource');
                var sizes = {
                    total: 0,
                    js: 0,
                    css: 0,
                    img: 0,
                    other: 0
                };
                
                resources.forEach(function(resource) {
                    var size = resource.transferSize || resource.encodedBodySize || 0;
                    sizes.total += size;
                    
                    if (resource.name.match(/\\.js$/)) {
                        sizes.js += size;
                    } else if (resource.name.match(/\\.css$/)) {
                        sizes.css += size;
                    } else if (resource.name.match(/\\.(jpg|jpeg|png|gif|webp|svg)$/)) {
                        sizes.img += size;
                    } else {
                        sizes.other += size;
                    }
                });
                
                return sizes;
            """)
            
            # Analyze cookies
            cookies = self.driver.get_cookies()
            insecure_cookies = []
            for cookie in cookies:
                if not cookie.get('httpOnly', False) or not cookie.get('secure', False):
                    insecure_cookies.append(cookie['name'])
            
            return {
                "performanceMetrics": {
                    "dns": performance_data.get('dns', 0),
                    "connect": performance_data.get('connect', 0),
                    "ttfb": performance_data.get('ttfb', 0),
                    "domLoad": performance_data.get('domLoad', 0),
                    "totalTime": performance_data.get('windowLoad', 0),
                    "redirects": performance_data.get('redirectCount', 0),
                    "totalSize": resource_data.get('total', 0),
                    "jsSize": resource_data.get('js', 0),
                    "cssSize": resource_data.get('css', 0),
                    "imageSize": resource_data.get('img', 0),
                    "cookieCount": len(cookies),
                    "insecureCookies": len(insecure_cookies)
                }
            }
        except Exception as e:
            self.log("ERROR", f"Performance analysis failed: {str(e)}")
            return {"performanceMetrics": {}}
            
    def content_analysis(self, soup):
        """Analyze page content"""
        try:
            # Extract text content
            text_content = soup.get_text()
            
            # Basic content analysis
            nlp_insights = {
                "contentType": "website",
                "architecture": "standard",
                "userFlows": [],
                "sentimentScore": 0.7,
                "keyPhrases": []
            }
            
            # Detect common patterns
            if soup.find('nav'):
                nlp_insights["userFlows"].append("navigation")
            if soup.find_all('form'):
                nlp_insights["userFlows"].append("forms")
            if soup.find_all(['article', 'section']):
                nlp_insights["contentType"] = "content-heavy"
            if soup.find_all(['button', 'input']):
                nlp_insights["userFlows"].append("interactive")
                
            # Detect modern web frameworks
            if soup.find(attrs={"data-react-root": True}) or soup.find(id="root"):
                nlp_insights["architecture"] = "React SPA"
            elif soup.find(attrs={"ng-app": True}):
                nlp_insights["architecture"] = "Angular Application"
            elif soup.find(attrs={"data-vue": True}):
                nlp_insights["architecture"] = "Vue.js Application"
                
            # Extract key phrases (simplified)
            title_tag = soup.find('title')
            if title_tag:
                nlp_insights["keyPhrases"].append(title_tag.text.strip())
                
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags[:3]:
                nlp_insights["keyPhrases"].append(h1.text.strip())
                
            return {"nlpInsights": nlp_insights}
            
        except Exception as e:
            self.log("ERROR", f"Content analysis failed: {str(e)}")
            return {"nlpInsights": {}}
            
    def calculate_security_score(self, results):
        """Calculate overall security score"""
        vulnerabilities = results.get("vulnerabilities", [])
        
        if not vulnerabilities:
            return 100
            
        score = 100
        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 10,
            "low": 5
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            score -= severity_weights.get(severity, 5)
            
        return max(0, score)

def main():
    if len(sys.argv) < 4:
        print("Usage: appium_analyzer.py <session_id> <url> <options>")
        sys.exit(1)
        
    session_id = sys.argv[1]
    url = sys.argv[2]
    options = json.loads(sys.argv[3])
    
    auditor = AppiumWebAuditor(session_id)
    auditor.analyze_url(url, options)

if __name__ == "__main__":
    main()
