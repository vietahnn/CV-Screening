from pydantic import BaseModel,Field

class Resume(BaseModel):
    education: str
    experience: str  
    skills: list[str]

class JobDescription(BaseModel):
    title : str
    required_skills: list[str]
    min_experience_years: int
    experience_context: str
    education_requirement: str


class Final_evaluation(BaseModel):
    overall_score: int = Field(
        description="An overall score from 0 to 100 representing the candidate's final fit."
    )
    final_reasoning: str = Field(
        description="A 3-5 sentence synthesis referencing all three dimensions."
    )

class MatchingStruture(BaseModel):
    score: int = Field(...)
    matched_items: list[str] = Field(...)
    missing_items: list[str] = Field(...)
    reasoning: str = Field(...)
