import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ATSScorer:
    def calculate_score(self, resume_text: str, jd_text: str) -> dict:
        
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # ========== 1. TF-IDF + COSINE SIMILARITY (ML) ==========
        try:
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            vectors = vectorizer.fit_transform([resume_lower, jd_lower])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            ml_score = similarity * 100
        except:
            ml_score = 50
        
        # ========== 2. EXTRACT KEYWORDS FROM JD (Dynamic) ==========
        # Extract all meaningful words from JD
        jd_words = set(re.findall(r'\b[a-z]{4,}\b', jd_lower))
        resume_words = set(re.findall(r'\b[a-z]{4,}\b', resume_lower))
        
        # Common stop words to ignore
        stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'about', 
                     'should', 'would', 'could', 'what', 'when', 'where', 'which', 
                     'there', 'these', 'those', 'then', 'than', 'please', 'note', 
                     'etc', 'more', 'very', 'just', 'over', 'after', 'before', 
                     'under', 'between', 'through', 'while', 'because', 'without',
                     'their', 'they', 'were', 'been', 'has', 'had', 'but', 'not',
                     'all', 'any', 'may', 'our', 'also', 'into', 'only', 'can',
                     'will', 'from', 'have', 'with', 'your', 'should', 'would'}
        
        jd_words = {w for w in jd_words if w not in stop_words}
        resume_words = {w for w in resume_words if w not in stop_words}
        
        # Calculate keyword score
        if len(jd_words) > 0:
            matched_keywords = resume_words.intersection(jd_words)
            keyword_score = (len(matched_keywords) / len(jd_words)) * 100
        else:
            matched_keywords = set()
            keyword_score = 50
        
        # ========== 3. PROJECT DETECTION (Generic) ==========
        project_indicators = ['project', 'developed', 'built', 'created', 'implemented', 
                             'designed', 'engineered', 'programmed', 'alpr', 'license',
                             'gesture', 'weather', 'iot', 'computer vision', 'detection']
        
        project_count = 0
        for ind in project_indicators:
            if ind in resume_lower:
                project_count += 1
        project_bonus = min(15, project_count * 3)
        
        # ========== 4. FINAL SCORE (Weighted) ==========
        # 60% ML similarity + 30% Keyword match + 10% Project bonus
        final_score = (ml_score * 0.6) + (keyword_score * 0.3) + (project_bonus * 0.1)
        final_score = min(100, max(0, final_score))
        
        # Debug output
        print("="*50)
        print(f"ML Score (60%): {ml_score:.2f}%")
        print(f"Keyword Score (30%): {keyword_score:.2f}%")
        print(f"Project Bonus (10%): {project_bonus:.2f}%")
        print(f"FINAL SCORE: {final_score:.2f}%")
        print(f"JD Keywords: {len(jd_words)}")
        print(f"Matched Keywords: {len(matched_keywords)}")
        print("="*50)
        
        return {
            "overall_score": round(final_score, 2),
            "ml_score": round(ml_score, 2),
            "keyword_score": round(keyword_score, 2),
            "project_bonus": project_bonus,
            "matched_keywords": list(matched_keywords)[:20],
            "missing_keywords": list(jd_words - matched_keywords)[:20]
        }
