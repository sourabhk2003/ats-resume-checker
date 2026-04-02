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
        
        # Extract keywords and calculate match
        resume_lower = request.resume_text.lower()
        jd_lower = request.job_description.lower()
        
        # Important skills dictionary
        important_skills = {
            'python': ['python', 'programming'],
            'machine_learning': ['machine learning', 'ml', 'deep learning', 'dl'],
            'computer_vision': ['computer vision', 'cv', 'opencv', 'yolo'],
            'data_visualization': ['visualization', 'matplotlib', 'seaborn', 'tableau', 'power bi'],
            'pytorch': ['pytorch', 'tensorflow', 'keras'],
            'sql': ['sql', 'database', 'mysql', 'postgresql'],
            'git': ['git', 'github', 'version control'],
            'pandas': ['pandas', 'numpy', 'data manipulation'],
            'scikit': ['scikit-learn', 'sklearn'],
            'iot': ['iot', 'internet of things', 'esp8266']
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
        
        # Calculate skill match percentage
        total_required = len(matched) + len(missing)
        skill_percentage = (len(matched) / total_required * 100) if total_required > 0 else 70
        
        # Project bonus (if candidate has projects)
        projects_keywords = ['project', 'built', 'developed', 'implemented', 'alpr', 'license plate', 'gesture', 'weather']
        has_projects = any(keyword in resume_lower for keyword in projects_keywords)
        project_bonus = 10 if has_projects else 0
        
        # Final score
        final_score = min(100, base_score + project_bonus)
        
        # Adjust if skill percentage is higher
        if skill_percentage > final_score:
            final_score = skill_percentage
        
        return {
            "success": True,
            "analysis": {
                "ats_score": round(final_score, 2),
                "score_details": {
                    "overall_score": final_score,
                    "similarity_score": base_score,
                    "keyword_score": skill_percentage,
                    "formatting_score": 75
                },
                "keyword_analysis": {
                    "matched_keywords": matched,
                    "missing_keywords": missing,
                    "match_percentage": skill_percentage,
                    "total_jd_keywords": total_required,
                    "matched_count": len(matched)
                },
                "skills": {
                    "found": matched,
                    "missing": missing
                },
                "suggestions": generate_suggestions(final_score, missing, matched)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_suggestions(score: float, missing: list, matched: list) -> list:
    suggestions = []
    
    if score >= 80:
        suggestions.append({
            "type": "success",
            "title": "Excellent Match! 🎉",
            "description": f"Your resume matches {len(matched)} key skills. Great job!",
            "action_items": [
                "Quantify your achievements with numbers",
                "Add GitHub links to your projects",
                "Keep your resume updated"
            ]
        })
    elif score >= 60:
        suggestions.append({
            "type": "good",
            "title": "Good Match! 👍",
            "description": f"You're almost there! Add these {len(missing)} skills to improve.",
            "action_items": missing[:8] if missing else ["Add more relevant keywords", "Tailor your resume for each job"]
        })
    else:
        suggestions.append({
            "type": "improvement",
            "title": "Needs Improvement ⚠️",
            "description": "Your resume needs more relevant keywords and skills.",
            "action_items": [
                "Add a dedicated Skills section",
                "Include keywords from job description",
                "Use standard section headings",
                "Quantify your achievements"
            ]
        })
    
    return suggestions