import PyPDF2
import os
import re

class ResumeScanner:
    @staticmethod
    def scan_pdf(file_path):
        """Extracts text from PDF and estimates skill level."""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error scanning PDF: {e}")
            return "Junior"

        # Simple AI simulation: keyword density
        keywords = ["senior", "expert", "lead", "architect", "years", "experience", "managed"]
        found = [k for k in keywords if k in text.lower()]
        
        # Word count also matters
        words = len(re.findall(r'\w+', text))
        
        if len(found) >= 4 or words > 500:
            return "Expert"
        elif len(found) >= 2 or words > 200:
            return "Intermediate"
        return "Junior"

class SemanticMatcher:
    @staticmethod
    def calculate_portfolio_similarity(job_desc, portfolio):
        """
        Simulates semantic matching by comparing job description keywords 
        with portfolio project descriptions.
        """
        if not portfolio:
            return 0.0, "No portfolio data provided."
            
        best_score = 0.0
        best_reason = ""
        
        job_words = set(re.findall(r'\w+', job_desc.lower()))
        
        for project in portfolio:
            proj_text = (project.get("title", "") + " " + project.get("description", "")).lower()
            proj_words = set(re.findall(r'\w+', proj_text))
            
            # Simple Jaccard similarity
            intersection = job_words.intersection(proj_words)
            union = job_words.union(proj_words)
            score = len(intersection) / len(union) if union else 0
            
            if score > best_score:
                best_score = score
                best_reason = f"Highly similar to their past project: '{project.get('title')}'"
        
        # Normalize score to 0-100 scale for matching
        # Since Jaccard is strict, we boost it.
        final_score = min(1.0, best_score * 5) 
        return final_score, best_reason
