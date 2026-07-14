from langgraph.graph import  MessagesState
from schema.cv_schema import MatchingStruture, Final_evaluation, JobDescription

class AgentState(MessagesState):
    #Input data
    resume_raw_text: list
    jd_raw_text : str

    run : str
    current_cv_index : int

    #Extracted data
    jd_info : JobDescription
    education_section: str
    skills_section: str
    experience_section: str

    #Result data
    skills_matching: MatchingStruture
    education_matching: MatchingStruture
    experience_matching: MatchingStruture

    #final score
    final_score : Final_evaluation

    summary : list
    rejected_cvs : list

