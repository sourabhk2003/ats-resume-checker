from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

class ATSScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            analyzer='word'
        )
        
        # Common skills dictionary
        self.skills_dict = {
            'python': ['python', 'programming', 'coding'],
            'machine learning': ['ml', 'machine learning', 'ai', 'artificial intelligence'],
            'data science': ['data science', 'analytics', 'data analysis'],
            'computer vision': ['computer vision', 'cv', 'image processing'],
            'deep learning': ['deep learning', 'dl', 'neural networks'],
            'sql': ['sql', 'database', 'mysql', 'postgresql'],
            'tableau': ['tableau', 'power bi', 'visualization'],
            'pytorch': ['pytorch', 'tensorflow', 'keras'],
            'git': ['git', 'github', 'version control'],
            'iot': ['iot', 'internet of things', 'esp8266']
        }
    
    def calculate_similarity(self, resume_text: str, jd_text: str) -> float:
        """Advanced similarity calculation"""
        # Preprocess
        resume_clean = self.preprocess_text(resume_text)
        jd_clean = self.preprocess_text(jd_text)
        
        # TF-IDF similarity
        documents = [resume_clean, jd_clean]
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        tfidf_score = similarity[0][0] * 100
        
        # Skill matching score
        skill_score = self.calculate_skill_match(resume_text, jd_text)
        
        # Keyword density score
        keyword_score = self.calculate_keyword_density(resume_text, jd_text)
        
        # Weighted final score (more weight to skills)
        final_score = (tfidf_score * 0.4) + (skill_score * 0.4) + (keyword_score * 0.2)
        
        return min(100, final_score)
    
    def calculate_skill_match(self, resume_text: str, jd_text: str) -> float:
        """Calculate skill matching percentage"""
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        matched_skills = []
        total_skills = 0
        
        for skill, variations in self.skills_dict.items():
            skill_found = False
            for var in variations:
                if var in resume_lower:
                    skill_found = True
                    break
            
            # Check if skill is required in JD
            jd_has = False
            for var in variations:
                if var in jd_lower:
                    jd_has = True
                    break
            
            if jd_has:
                total_skills += 1
                if skill_found:
                    matched_skills.append(skill)
        
        if total_skills == 0:
            return 50
        
        return (len(matched_skills) / total_skills) * 100
    
    def calculate_keyword_density(self, resume_text: str, jd_text: str) -> float:
        """Calculate keyword relevance"""
        resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
        jd_words = set(re.findall(r'\b[a-z]{3,}\b', jd_text.lower()))
        
        stop_words = {'the', 'and', 'for', 'are', 'you', 'with', 'have', 'from', 'your', 
                      'will', 'can', 'this', 'that', 'they', 'was', 'were', 'been', 'has',
                      'had', 'but', 'not', 'all', 'any', 'may', 'our', 'their', 'them'}
        
        jd_words = {w for w in jd_words if w not in stop_words and len(w) > 2}
        
        if len(jd_words) == 0:
            return 50
        
        matched = len(resume_words.intersection(jd_words))
        return (matched / len(jd_words)) * 100
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text
    
    def get_score_category(self, score: float) -> dict:
        """Get score category with proper message"""
        if score >= 80:
            return {
                "category": "Excellent",
                "color": "#10b981",
                "message": "🎉 Excellent match! Your resume is well-optimized for this role."
            }
        elif score >= 60:
            return {
                "category": "Good",
                "color": "#3b82f6",
                "message": "👍 Good match! Minor improvements can make it excellent."
            }
        elif score >= 40:
            return {
                "category": "Average",
                "color": "#f59e0b",
                "message": "📈 Average match. Add more relevant keywords from the JD."
            }
        else:
            return {
                "category": "Needs Improvement",
                "color": "#ef4444",
                "message": "⚠️ Needs significant improvement. Tailor your resume for this role."
            }
    
    def calculate_detailed_score(self, resume_text: str, jd_text: str) -> dict:
        """Calculate detailed scoring metrics"""
        overall_score = self.calculate_similarity(resume_text, jd_text)
        skill_score = self.calculate_skill_match(resume_text, jd_text)
        
        return {
            "overall_score": round(overall_score, 2),
            "similarity_score": round(overall_score * 0.7, 2),
            "keyword_score": round(self.calculate_keyword_density(resume_text, jd_text), 2),
            "formatting_score": 75.0,
            "category_info": self.get_score_category(overall_score)
        }