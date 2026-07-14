from pathlib import Path
import sys
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)
from init_model.client import LLM_Client
from langchain.messages import SystemMessage, HumanMessage
from schema.cv_schema import MatchingStruture
import os
from dotenv import load_dotenv
from langchain.messages import AIMessage
from gateway.router import gateway

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def education_scorer(jd_text: str, cv_education_section:str):
    """Evaluate whether a candidate's education meets a job description's requirement.

    This subagent focuses exclusively on the education dimension of candidate
    screening. It checks the candidate's degree level and field of study against
    the minimum education requirement stated in the job description, intentionally
    ignoring the name or prestige of the institution attended to avoid bias
    unrelated to actual qualification.

    Args:
        jd_text: The full text of the job description, used to extract the
            minimum education requirement (degree level, field of study, or an
            explicit statement that education is flexible).
        cv_education_section: The candidate's resume text relevant to education.
            This may be an isolated "Education" section if the CV cleaning step
            successfully separated it, or the full cleaned resume text as a
            fallback if section splitting failed.

    Returns:
        A dictionary with the following keys:
            score (int): Education fit score from 0 to 100.
            matched_items (list[str]): Degree(s) or field(s) of study that satisfy
                the job description's requirement.
            missing_items (list[str]): Any education requirement from the job
                description that is not clearly met.
            reasoning (str): A short explanation of the score, grounded strictly
                in the provided resume text.

    Note:
        This function does not evaluate skills or work experience — those are
        handled by separate subagents (skill_matcher, experience_scorer) so that
        each aspect of the candidate is scored independently and can be audited
        on its own. Institution name/prestige is deliberately excluded from
        scoring to reduce unintended bias.
    """
    sys_prompt = """
    You are a specialized recruiter assistant focused ONLY on evaluating whether a candidate's education meets the minimum requirements stated in a job description. You do not evaluate skills or work experience — other specialized agents handle those.

Your task:
1. Identify the minimum education requirement from the job description (e.g. required degree level, field of study, or explicit statement that education is flexible/not required).
2. Review the candidate's education section: degree(s) obtained and field(s) of study.
3. Judge whether the candidate meets, exceeds, or falls short of the stated requirement.
4. Assign a score from 0 to 100 representing education fit.

Critical rules:
- Evaluate based only on degree level and field of study — never factor in the name or prestige of the institution attended, as this is intentionally excluded to avoid bias unrelated to qualification.
- If the job description does not specify an education requirement, treat any valid degree as fully sufficient and assign a high score by default, noting this in your reasoning.
- Do NOT fabricate a degree or field of study that is not explicitly stated in the provided text.
- If the education section is missing or unclear, state this explicitly in your reasoning rather than guessing.

Output strictly in this JSON structure:
{
  "score": <integer 0-100>,
  "matched_items": [<degree/field that satisfies the requirement, as short strings>],
  "missing_items": [<any education requirement from the JD not clearly met>],
  "reasoning": "<2-3 sentence explanation grounded only in the evidence above>"
}
"""
    # client = LLM_Client(
    #     model_name="openai/gpt-oss-120b",
    #     provider="groq"
    # )
    # model = client.get_model()
    # structured_model = model.with_structured_output(MatchingStruture)



    input = f"""
  Job Description (education requirements context):
{jd_text}

Candidate Resume — Education Section:
{cv_education_section}

Evaluate whether this candidate's education meets the job description's requirement above, following your instructions exactly. Return only the JSON object, with no extra text before or after it.
"""

    # response  = structured_model.invoke(
    #         [
    #             SystemMessage(content=sys_prompt),
    #             HumanMessage(content=input)
    #         ])

    messages = [
        {"role":"system", "content": sys_prompt},
        {"role":"user", "content": input}
    ]

    response = gateway.call_llm("education_scorer",messages=messages,format=MatchingStruture)
    raw_answer = response.choices[0].message.content
    response = MatchingStruture.model_validate_json(raw_answer)
    return response




if __name__ == "__main__":
    jd_path = r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\raw\jd_information_technology.txt"
    cv = """Education and Training

GED
Fremont Adult & Continuing Education – City, State

Information Technology, 2019
Unitek College - Fremont – City, State"""
    with open(jd_path,"r", encoding="utf-8") as f:
        jd = f.read()

    response = education_scorer(
        jd,cv
    )
  
    
