#!/usr/bin/env python3
"""
Lightweight NLP module for text analysis without heavy dependencies
Uses basic Python libraries for efficient text processing
"""

import re
import json
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import math

class LightweightNLP:
    def __init__(self):
        # Common English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by', 'for', 
            'from', 'has', 'have', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 
            'that', 'the', 'to', 'was', 'will', 'with', 'the', 'this', 'these',
            'those', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'both', 'each', 'more', 'most',
            'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'can', 'just', 'should', 'now'
        }
        
        # Domain-specific keywords for web analysis
        self.security_keywords = {
            'secure', 'encrypted', 'ssl', 'https', 'certificate', 'authentication',
            'authorization', 'vulnerability', 'exploit', 'injection', 'xss',
            'csrf', 'security', 'protection', 'firewall', 'antivirus', 'malware'
        }
        
        self.performance_keywords = {
            'fast', 'slow', 'performance', 'speed', 'optimize', 'cache',
            'loading', 'responsive', 'efficient', 'latency', 'bandwidth',
            'compression', 'minify', 'bundle', 'lazy', 'async', 'defer'
        }
        
        self.ux_keywords = {
            'user', 'experience', 'interface', 'design', 'accessibility',
            'usability', 'navigation', 'intuitive', 'responsive', 'mobile',
            'desktop', 'tablet', 'touchscreen', 'gesture', 'interaction'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        return text.split()
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF-like scoring"""
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        # Filter out stop words and short words
        words = [w for w in tokens if w not in self.stop_words and len(w) > 3]
        
        # Calculate word frequency
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate TF scores
        tf_scores = {}
        for word, freq in word_freq.items():
            tf_scores[word] = freq / total_words
        
        # Simple IDF approximation (penalize very common words)
        idf_scores = {}
        for word in tf_scores:
            # Higher score for less frequent words
            idf_scores[word] = math.log(total_words / (1 + word_freq[word]))
        
        # Calculate TF-IDF scores
        tfidf_scores = {}
        for word in tf_scores:
            tfidf_scores[word] = tf_scores[word] * idf_scores[word]
        
        # Sort by score and return top keywords
        sorted_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:num_keywords]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Simple entity extraction using patterns"""
        entities = {
            'emails': [],
            'urls': [],
            'phone_numbers': [],
            'dates': [],
            'prices': []
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        entities['urls'] = re.findall(url_pattern, text)
        
        # Phone number pattern (US format)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities['phone_numbers'] = re.findall(phone_pattern, text)
        
        # Simple date pattern
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities['dates'] = re.findall(date_pattern, text)
        
        # Price pattern
        price_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        entities['prices'] = re.findall(price_pattern, text)
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Basic sentiment analysis using keyword matching"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'perfect', 'best', 'awesome', 'nice', 'super', 'happy',
            'beautiful', 'brilliant', 'outstanding', 'positive', 'success'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'disappointing', 'useless', 'broken', 'fail', 'wrong', 'error',
            'problem', 'issue', 'bug', 'crash', 'slow', 'confusing', 'difficult'
        }
        
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {'positive': 0.5, 'negative': 0.5, 'neutral': 1.0}
        
        positive_score = positive_count / total_sentiment_words
        negative_score = negative_count / total_sentiment_words
        
        # Determine overall sentiment
        if positive_score > negative_score:
            sentiment = 'positive'
        elif negative_score > positive_score:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'overall': sentiment,
            'confidence': abs(positive_score - negative_score)
        }
    
    def extract_topics(self, text: str) -> Dict[str, float]:
        """Extract topics based on keyword categories"""
        preprocessed = self.preprocess_text(text)
        tokens = set(self.tokenize(preprocessed))
        
        topics = {}
        
        # Check for security-related content
        security_matches = tokens.intersection(self.security_keywords)
        if security_matches:
            topics['security'] = len(security_matches) / len(self.security_keywords)
        
        # Check for performance-related content
        performance_matches = tokens.intersection(self.performance_keywords)
        if performance_matches:
            topics['performance'] = len(performance_matches) / len(self.performance_keywords)
        
        # Check for UX-related content
        ux_matches = tokens.intersection(self.ux_keywords)
        if ux_matches:
            topics['user_experience'] = len(ux_matches) / len(self.ux_keywords)
        
        return topics
    
    def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        """Simple extractive summarization"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_sentences:
            return text
        
        # Score sentences based on keyword frequency
        keywords, _ = zip(*self.extract_keywords(text, 20))
        keywords = set(keywords)
        
        sentence_scores = []
        for sentence in sentences:
            tokens = set(self.tokenize(self.preprocess_text(sentence)))
            score = len(tokens.intersection(keywords))
            sentence_scores.append((score, sentence))
        
        # Sort by score and select top sentences
        sentence_scores.sort(reverse=True)
        top_sentences = [s[1] for s in sentence_scores[:num_sentences]]
        
        # Return sentences in original order
        summary = []
        for sentence in sentences:
            if sentence in top_sentences:
                summary.append(sentence)
        
        return '. '.join(summary) + '.'
    
    def analyze_web_content(self, text: str) -> Dict:
        """Comprehensive analysis for web content"""
        return {
            'keywords': dict(self.extract_keywords(text, 15)),
            'entities': self.extract_entities(text),
            'sentiment': self.analyze_sentiment(text),
            'topics': self.extract_topics(text),
            'summary': self.summarize_text(text, 5),
            'word_count': len(self.tokenize(text)),
            'unique_words': len(set(self.tokenize(self.preprocess_text(text))))
        }


# Example usage for testing
if __name__ == "__main__":
    nlp = LightweightNLP()
    
    sample_text = """
    Welcome to our secure e-commerce platform! We provide fast, reliable service 
    with SSL encryption and excellent customer support. Our website loads quickly 
    and offers a great user experience on mobile and desktop devices. 
    Contact us at support@example.com or call 555-123-4567.
    """
    
    results = nlp.analyze_web_content(sample_text)
    print(json.dumps(results, indent=2))