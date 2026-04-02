from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

router = APIRouter()

class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

@router.post("/analyze")
async def analyze_resume(request: AnalysisRequest):
    try:
        # Validate inputs
        if not request.resume_text or not request.job_description:
            raise HTTPException(status_code=400, detail="Resume and job description are required")
        
        # Calculate similarity score
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        documents = [request.resume_text, request.job_description]
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        base_score = similarity[0][0] * 100
        
        # Extract keywords
        resume_lower = request.resume_text.lower()
        jd_lower = request.job_description.lower()
        
        # Important skills
        important_skills = {
            'python': ['python', 'programming'],
            'machine_learning': ['machine learning', 'ml', 'deep learning'],
            'computer_vision': ['computer vision', 'opencv', 'yolo'],
            'data_visualization': ['visualization', 'matplotlib', 'seaborn', 'tableau'],
            'pytorch': ['pytorch', 'tensorflow', 'keras'],
            'sql': ['sql', 'database'],
            'git': ['git', 'github'],
            'pandas': ['pandas', 'numpy'],
            'scikit': ['scikit-learn', 'sklearn']
        }
        
        matched = []
        missing = []
        
        for skill, variations in important_skills.items():
            jd_has = any(var in jd_lower for var in variations)
            resume_has = any(var in resume_lower for var in variations)
            
            if jd_has:
                if resume_has:
                    matched.append(skill.replace('_', ' ').title())
                else:
                    missing.append(skill.replace('_', ' ').title())
        
        # Project bonus
        projects_keywords = ['project', 'built', 'developed', 'alpr', 'license plate', 'gesture']
        has_projects = any(keyword in resume_lower for keyword in projects_keywords)
        project_bonus = 15 if has_projects else 0
        
        # Final score
        final_score = min(100, base_score + project_bonus)
        
        return {
            "success": True,
            "analysis": {
                "ats_score": round(final_score, 2),
                "score_details": {
                    "overall_score": final_score,
                    "similarity_score": base_score,
                    "keyword_score": len(matched) / (len(matched) + len(missing)) * 100 if (len(matched) + len(missing)) > 0 else 50,
                    "formatting_score": 75
                },
                "keyword_analysis": {
                    "matched_keywords": matched,
                    "missing_keywords": missing,
                    "match_percentage": len(matched) / (len(matched) + len(missing)) * 100 if (len(matched) + len(missing)) > 0 else 50,
                    "total_jd_keywords": len(matched) + len(missing),
                    "matched_count": len(matched)
                },
                "skills": {
                    "found": matched,
                    "missing": missing
                },
                "suggestions": [
                    {
                        "type": "success" if final_score > 70 else "warning",
                        "title": "ATS Analysis Complete",
                        "description": f"Your resume matches {len(matched)} key skills. Score: {round(final_score)}%",
                        "action_items": missing[:8] if missing else ["Great job! Your resume is well optimized."]
                    }
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
