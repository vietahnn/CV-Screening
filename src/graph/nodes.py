from graph.state import AgentState
from schema.cv_schema import Resume, JobDescription
from init_model.client import LLM_Client
from langchain.messages import AIMessage
from subagents.education_scorer import education_scorer
from subagents.experience_scorer import experience_scorer
from subagents.skill_matcher import skill_matcher
from subagents.orchestrator import orchestrator
from gateway.router import gateway
from guardrails.cv_checker import is_cv
from guardrails.jd_checker import is_jd
import logging

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def extract_cv(state:AgentState):
    sys_prompt = """
You are a resume parsing assistant. Your task is to extract three specific categories of information from a raw resume text: education, work experience, and skills. You do not evaluate or score the candidate — you only extract and organize what is explicitly stated in the text.

Your task:
1. Extract the candidate's education background (degrees, fields of study).
2. Extract the candidate's work experience, including roles held and key responsibilities.
3. Extract the candidate's skills as a list of individual skill items (not full sentences).

Critical rules:
- Only extract information explicitly present in the text. Do NOT infer, assume, or add any skill or qualification that is not stated.
- For the skills list, break down compound phrases into individual items where reasonable (e.g. "Python and SQL" becomes two separate items: "Python", "SQL").
- If a category has no information available in the text, return an empty list (for skills) or an empty string (for education/experience) — do not guess or fabricate content to fill a gap.
- Preserve the original wording as much as possible rather than paraphrasing, so that later steps can verify each extracted item against the source text.
"""
    # client = LLM_Client(
    #     model_name="openai/gpt-oss-120b",
    #     provider="groq"
    # )

    resume = state["resume_raw_text"][state["current_cv_index"]]["resume"]

    input = f"""
    Resume: {resume}
Extract the resume into education section, skills section, projects section and experience section
"""

    # response = structured_model.invoke(
    #     [
    #         {"role": "system", "content": sys_prompt},
    #         {"role": "user", "content": input }
    #     ]
    # )

    messages = [
        {"role":"system", "content": sys_prompt},
        {"role":"user", "content": input}
    ]

    response = gateway.call_llm("extract_info",messages=messages, format=Resume)
    raw_answer = response.choices[0].message.content
    response = Resume.model_validate_json(raw_answer)

    return {
        "messages": [AIMessage(content = "Extract data done")],
        "education_section": response.education ,
        "skills_section" : response.skills,
        "experience_section":response.experience
    }


def extract_jd(state:AgentState):
    sys_prompt = """
You are a job description parsing assistant. Your task is to extract structured hiring requirements from a raw job description text. You do not evaluate any candidate — you only extract and organize what the job description explicitly states.

Your task:
1. Extract the required skills as a list of individual skill items (not full sentences).
2. Extract the minimum years of experience required, as a number. If not explicitly stated, estimate conservatively based on the seniority level implied (e.g. "senior" implies at least 5 years).
3. Extract a short phrase describing the type/domain of experience required (e.g. "backend API development", "customer service management").
4. Extract the minimum education requirement as a short string (e.g. "Bachelor's degree in Computer Science or related field"). If no education requirement is stated, return "not specified".

Besides, you also need to return A short string identifying the job/position (around 1-2 sentences - must include the title and position)
Critical rules:
- Only extract what is explicitly stated in the text. Do NOT add requirements that are not mentioned.
- For the skills list, break down compound phrases into individual skill items where reasonable (e.g. "Python and SQL" becomes two separate items).
"""
    # client = LLM_Client(
    #     model_name="gemma4:31b-cloud",
    #     provider="ollama"
    # )
    # model = client.get_model()
    # structured_model = model.with_structured_output(JobDescription)

    content = state["jd_raw_text"]
    input =f"""
Job description text:
{content}

Extract the structured hiring requirements from this job description, following your instructions exactly."""

    # response = structured_model.invoke(
    #     [
    #         {"role": "system", "content": sys_prompt},
    #         {"role": "user", "content": input }
    #     ]
    # )

    messages = [
        {"role":"system", "content": sys_prompt},
        {"role":"user", "content": input}
    ]

    response = gateway.call_llm("extract_info",messages=messages, format=JobDescription)
    raw_answer = response.choices[0].message.content
    response = JobDescription.model_validate_json(raw_answer)


    return {
        "jd_info": response
    }


def skills_node(state:AgentState):
    jd = state["jd_info"]
    jd_skills = jd.required_skills

    cv_skills = state["skills_section"]

    result = skill_matcher(
        jd_skills=jd_skills,
        cv_skills=cv_skills
    )


    return {
        "messages" : [AIMessage(content="Extract SKILLS done")],
        "skills_matching" : result
    }


def education_node(state:AgentState):
    jd = state["jd_info"]
    jd_education = jd.education_requirement

    cv_education = state["education_section"]

    result = education_scorer(
        jd_text= jd_education,
        cv_education_section= cv_education
    )

    return {
        "messages" : [AIMessage(content="Extract EDUCATION done")],
        "education_matching" : result
    }

def experience_node(state:AgentState):
    jd = state["jd_info"]
    jd_experience = jd.experience_context
    jd_min_year_experience = jd.min_experience_years

    cv_experience = state["experience_section"]

    result = experience_scorer(
        jd_experience=jd_experience,
        cv_experience=cv_experience,
        min_experience_years=jd_min_year_experience
    )
    return {
        "messages" : [AIMessage(content="Extract EXPERIENCE done")],
        "experience_matching" : result
    }


def orchestrator_node(state:AgentState):
    jd = state["jd_info"]
    jd_title = jd.title
   
    experience_result = state["experience_matching"]
    education_result = state["education_matching"]
    skills_result = state["skills_matching"]

    result = orchestrator(
        jd_title_or_summary= jd_title,
        skill_result=skills_result,
        experience_result=experience_result,
        education_result=education_result
    )

    logging.info(result)

    resume = state["resume_raw_text"][state["current_cv_index"]]
    resume_info = {
        "id": resume["id"],
        "name": resume["name"],
        "email": resume["email"],
        "social_links": resume["social_links"],
    }

    summary = {
        "resume_info": resume_info,

        "education_section": state["education_section"],
        "skilss_section": state["skills_section"],
        "experience_section": state["experience_section"],
        
        "skills_matching" : state["skills_matching"],
        "education_matching": state["education_matching"],
        "experience_matching": state["experience_matching"],

        "final_score" : result
    }
    
    return {
        "messages" : [AIMessage(content="ORCHESTRATOR DONE")],
        "final_score" : result,
        "summary": state.get("summary",[]) + [summary]
    }


def check_cv_node(state:AgentState):
    cv = state["resume_raw_text"][state["current_cv_index"]]
    response = is_cv(raw_text=cv)

    rejected_cvs = state.get("rejected_cvs", [])
    if response.strip().lower() == "false":
        rejected_cvs = rejected_cvs + [{
            "filename": cv.get("filename") or f"CV_{state['current_cv_index'] + 1}",
            "reason": "CV không đạt điều kiện theo checker",
        }]
    
    return {
        "messages": AIMessage(content = response, name="check_cv"),
        "rejected_cvs": rejected_cvs
    }


def check_jd_node(state:AgentState):
    jd = state["jd_raw_text"]
    logging.info(f"Thông tin jd {jd}")
    response = is_jd(raw_text=jd)
    
    return {
        "messages": AIMessage(content = response, name="check_jd")
    }

def should_continue(state:AgentState):
    last_message = state["messages"][-1]
    content = last_message.content
    return content

def coordinator(state:AgentState):
    list_cv = state["resume_raw_text"]

    if state.get("current_cv_index") is None:
        return {
            "run" : "True",
            "current_cv_index": 0
        }
    
    if state["current_cv_index"] == len(list_cv) -1:
        return {
            "run": "False"
        }
    else:
        return{
            "run":"True",
            "current_cv_index": state["current_cv_index"] + 1
        }

def coordinator_continue(state:AgentState):
    return state["run"]





