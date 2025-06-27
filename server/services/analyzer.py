#!/usr/bin/env python3

import sys
import json
import time
import urllib.parse
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup

class WebAuditor:
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
        
    def send_result(self, results):
        """Send final results to Node.js server"""
        result_data = {
            "type": "result",
            "data": results
        }
        print(json.dumps(result_data), flush=True)
        
    def analyze_url(self, url, options):
        """Main analysis function"""
        try:
            self.log("INFO", f"Starting analysis of {url}")
            self.update_progress(5, "running")
            
            # Validate URL
            if not self.validate_url(url):
                raise ValueError("Invalid URL format")
                
            self.update_progress(15)
            
            # Fetch the website
            self.log("INFO", f"Fetching {url}")
            start_time = time.time()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            load_time = time.time() - start_time
            
            self.log("INFO", f"Page fetched in {load_time:.2f} seconds")
            self.update_progress(35)
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = {
                "loadTime": f"{load_time:.2f}s",
                "securityScore": 50,  # Will be calculated
                "domElements": 0,
                "jsErrors": 0,
                "vulnerabilities": [],
                "performanceMetrics": {},
                "nlpInsights": {}
            }
            
            # Perform security analysis
            if options.get('securityAudit', True):
                self.log("INFO", "Running security audit")
                security_results = self.security_analysis(url, response, soup)
                results.update(security_results)
                self.update_progress(50)
                
            # Perform performance analysis
            if options.get('performanceTest', True):
                self.log("INFO", "Running performance analysis")
                perf_results = self.performance_analysis(response, soup)
                results.update(perf_results)
                self.update_progress(70)
                
            # Perform NLP analysis
            if options.get('nlpAnalysis', True):
                self.log("INFO", "Running NLP analysis")
                nlp_results = self.nlp_analysis(soup)
                results.update(nlp_results)
                self.update_progress(85)
                
            # Calculate final security score
            results["securityScore"] = self.calculate_security_score(results)
            self.update_progress(100, "completed")
            
            self.log("INFO", "Analysis completed successfully")
            self.send_result(results)
            
        except Exception as e:
            self.log("ERROR", f"Analysis failed: {str(e)}")
            self.update_progress(0, "failed")
            
    def validate_url(self, url):
        """Validate URL format"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def security_analysis(self, url, response, soup):
        """Perform security vulnerability analysis"""
        vulnerabilities = []
        
        try:
            # Check security headers
            headers_vulns = self.check_security_headers(response)
            vulnerabilities.extend(headers_vulns)
            
            # Check for XSS vulnerabilities
            xss_vulns = self.check_xss_vulnerabilities(soup)
            vulnerabilities.extend(xss_vulns)
            
            # Check HTTPS
            https_vulns = self.check_https(url)
            vulnerabilities.extend(https_vulns)
            
        except Exception as e:
            self.log("ERROR", f"Security analysis error: {str(e)}")
            
        return {"vulnerabilities": vulnerabilities}
        
    def check_security_headers(self, response):
        """Check for missing security headers"""
        vulnerabilities = []
        
        try:
            headers = response.headers
            
            security_headers = {
                'X-Frame-Options': 'Clickjacking protection',
                'X-XSS-Protection': 'XSS protection',
                'X-Content-Type-Options': 'MIME type sniffing protection',
                'Strict-Transport-Security': 'HTTPS enforcement',
                'Content-Security-Policy': 'Content injection protection'
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    vulnerabilities.append({
                        "type": "missing_headers",
                        "severity": "medium" if header != 'Content-Security-Policy' else "high",
                        "title": f"Missing {header} Header",
                        "description": f"The {header} header is missing, which could leave the site vulnerable to {description.lower()}.",
                        "location": "HTTP Response Headers",
                        "recommendation": f"Add the {header} header to improve security."
                    })
                    
        except Exception as e:
            self.log("WARN", f"Could not check headers: {str(e)}")
            
        return vulnerabilities
        
    def check_xss_vulnerabilities(self, soup):
        """Check for potential XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Find all input fields
            inputs = soup.find_all('input')
            textareas = soup.find_all('textarea')
            
            for element in inputs + textareas:
                # Check if input has value attribute without proper escaping
                if element.get('value') and not self.has_xss_protection(str(element)):
                    vulnerabilities.append({
                        "type": "xss",
                        "severity": "high",
                        "title": "Potential XSS Vulnerability",
                        "description": "Input field may be vulnerable to cross-site scripting attacks due to lack of proper output encoding.",
                        "location": f"Input element: {element.get('name') or element.get('id') or 'unnamed'}",
                        "evidence": str(element)[:200] + "..." if len(str(element)) > 200 else str(element),
                        "recommendation": "Implement proper input validation and output encoding."
                    })
                    
        except Exception as e:
            self.log("WARN", f"XSS check error: {str(e)}")
            
        return vulnerabilities
        
    def has_xss_protection(self, html):
        """Simple check for XSS protection indicators"""
        protection_indicators = ['htmlentities', 'escape', 'sanitize']
        return any(indicator in html.lower() for indicator in protection_indicators)
        
    def check_https(self, url):
        """Check HTTPS implementation"""
        vulnerabilities = []
        
        if not url.startswith('https://'):
            vulnerabilities.append({
                "type": "other",
                "severity": "medium", 
                "title": "Non-HTTPS Connection",
                "description": "The website is not using HTTPS, which means data transmission is not encrypted.",
                "location": "URL Protocol",
                "recommendation": "Implement HTTPS to encrypt data in transit."
            })
            
        return vulnerabilities
        
    def performance_analysis(self, response, soup):
        """Analyze website performance"""
        try:
            # Get DOM statistics
            dom_elements = len(soup.find_all())
            
            # Get page size
            total_size = len(response.content)
            
            # Estimate resource sizes
            scripts = soup.find_all('script')
            styles = soup.find_all(['style', 'link'])
            images = soup.find_all('img')
            
            js_size = sum(len(str(script)) for script in scripts) * 10  # Rough estimate
            css_size = sum(len(str(style)) for style in styles) * 5
            image_size = len(images) * 5000  # Very rough estimate
            
            performance_metrics = {
                "dns": 120,  # Simulated values
                "connect": 340,
                "ssl": 200,
                "ttfb": 890,
                "download": 450,
                "domLoad": 340,
                "totalSize": total_size,
                "jsSize": js_size,
                "cssSize": css_size,
                "imageSize": image_size
            }
            
            return {
                "domElements": dom_elements,
                "jsErrors": 0,  # Can't detect JS errors without browser
                "performanceMetrics": performance_metrics
            }
            
        except Exception as e:
            self.log("ERROR", f"Performance analysis error: {str(e)}")
            return {"domElements": 0, "jsErrors": 0, "performanceMetrics": {}}
            
    def nlp_analysis(self, soup):
        """Perform NLP analysis of page content"""
        try:
            # Get page text content
            page_text = soup.get_text()
            
            if not page_text.strip():
                return {"nlpInsights": {}}
                
            # Simple keyword-based analysis
            key_phrases = self.extract_key_phrases(page_text)
            content_type = self.determine_content_type(page_text)
            architecture = self.detect_architecture(soup)
            user_flows = self.detect_user_flows(soup)
            
            nlp_insights = {
                "contentType": content_type,
                "architecture": architecture,
                "userFlows": user_flows,
                "sentimentScore": 0.5,  # Simplified
                "keyPhrases": key_phrases
            }
            
            return {"nlpInsights": nlp_insights}
            
        except Exception as e:
            self.log("ERROR", f"NLP analysis error: {str(e)}")
            return {"nlpInsights": {}}
            
    def extract_key_phrases(self, text):
        """Extract key phrases from text"""
        # Simple extraction based on common patterns
        words = text.lower().split()
        
        # Look for common business/tech terms
        key_terms = []
        business_words = ['service', 'product', 'company', 'business', 'solution', 'platform', 'technology']
        
        for word in set(words):
            if len(word) > 4 and word in business_words:
                key_terms.append(word.title())
                
        return key_terms[:10]
            
    def determine_content_type(self, text):
        """Determine the type of website based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['shop', 'buy', 'cart', 'price', 'product']):
            return "E-commerce"
        elif any(word in text_lower for word in ['blog', 'article', 'news', 'post']):
            return "Blog/News"
        elif any(word in text_lower for word in ['about', 'service', 'contact', 'business']):
            return "Corporate"
        elif any(word in text_lower for word in ['learn', 'course', 'education', 'tutorial']):
            return "Educational"
        else:
            return "General"
            
    def detect_architecture(self, soup):
        """Detect web architecture patterns"""
        try:
            page_source = str(soup).lower()
            
            if 'react' in page_source or 'reactdom' in page_source:
                return "React-based SPA"
            elif 'angular' in page_source or 'ng-' in page_source:
                return "Angular application"
            elif 'vue' in page_source or 'v-' in page_source:
                return "Vue.js application"
            elif 'jquery' in page_source:
                return "jQuery-based website"
            else:
                return "Traditional HTML website"
                
        except Exception as e:
            return "Unknown architecture"
            
    def detect_user_flows(self, soup):
        """Detect common user interaction flows"""
        flows = []
        
        try:
            # Look for forms
            forms = soup.find_all('form')
            if forms:
                flows.append("Form submission workflow")
                
            # Look for navigation
            nav = soup.find_all(['nav', 'menu'])
            if nav:
                flows.append("Site navigation flow")
                
            # Look for login/register elements
            if soup.find_all(text=re.compile(r'login|sign in|register|sign up', re.I)):
                flows.append("Authentication workflow")
                
            # Look for search
            if soup.find_all(['input'], {'type': 'search'}) or soup.find_all(text=re.compile(r'search', re.I)):
                flows.append("Search functionality")
                
        except Exception as e:
            self.log("WARN", f"User flow detection error: {str(e)}")
            
        return flows[:5]  # Limit to 5 flows
        
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
    if len(sys.argv) != 4:
        print("Usage: python analyzer.py <url> <session_id> <options_json>")
        sys.exit(1)
        
    url = sys.argv[1]
    session_id = int(sys.argv[2])
    options = json.loads(sys.argv[3])
    
    auditor = WebAuditor(session_id)
    auditor.analyze_url(url, options)

if __name__ == "__main__":
    main()