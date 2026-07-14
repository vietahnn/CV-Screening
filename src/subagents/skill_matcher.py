from pathlib import Path
import sys
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)
from init_model.client import LLM_Client
from langchain.messages import SystemMessage, HumanMessage
from schema.cv_schema import MatchingStruture
from langchain.messages import AIMessage
import os
from dotenv import load_dotenv
from gateway.router import gateway


load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def skill_matcher( jd_skills: list[str], cv_skills:list[str]):
    """Evaluate how well a candidate's skills match the requirements in a job description.

    This subagent focuses exclusively on the skill dimension of candidate screening.
    It compares the skills required or preferred in the job description against the
    skills explicitly stated in the candidate's resume, then produces a match score
    along with the specific skills that were matched or found missing.

    Args:
        jd_skills: The full text of the job description, used to extract required
            and preferred skills along with their context.
        cv_skills: The candidate's resume text relevant to skills. This may
            be an isolated "Skills" section if the CV cleaning step successfully
            separated it, or the full cleaned resume text as a fallback if section
            splitting failed.

    Returns:
        A dictionary with the following keys:
            score (int): Skill match score from 0 to 100.
            matched_items (list[str]): Skills from the job description that were
                found in the candidate's resume.
            missing_items (list[str]): Skills from the job description that were
                not found in the candidate's resume.
            reasoning (str): A short explanation of the score, grounded strictly
                in the provided resume text.

    Note:
        This function does not evaluate work experience or education — those are
        handled by separate subagents (experience_scorer, education_scorer) so that
        each aspect of the candidate is scored independently and can be audited on
        its own.
    """
    sys_prompt = """
    You are a specialized technical recruiter assistant focused ONLY on evaluating skill match between a candidate's resume and a job description. You do not evaluate experience duration, job titles, or education — other specialized agents handle those.

Your task:
1. Extract the list of required/preferred skills from the job description.
2. Extract the list of skills explicitly mentioned in the candidate's resume text.
3. Compare the two lists and determine which required skills are matched and which are missing.
4. Assign a score from 0 to 100 representing how well the candidate's skills align with the job's skill requirements.

Critical rules:
- Only count a skill as "matched" if it is explicitly stated or unambiguously implied in the resume text provided. Never infer a skill from a job title or company name alone.
- Do NOT invent, assume, or hallucinate any skill that is not present in the given resume text, even if it seems likely for someone in that role.
- If the resume text is incomplete or a skill section could not be cleanly isolated, do your best with whatever text you are given, but stay strictly grounded in it.
- Treat closely related terms as equivalent when reasonable (e.g. "React.js" and "React"), but do not treat loosely related terms as equivalent (e.g. "SQL" is not the same as "Python").

Output strictly in this JSON structure:
{
  "score": <integer 0-100>,
  "matched_items": [<list of matched skills as strings>],
  "missing_items": [<list of required skills not found in resume>],
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
    Job Description (required/preferred skills context):
{", ".join(jd_skills)}

Candidate Resume — Skills Section:
{", ". join(cv_skills)}

Evaluate the skill match between this candidate and the job description above, following your instructions exactly. Return only the JSON object, with no extra text before or after it.
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

    response = gateway.call_llm("skills_matcher",messages=messages, format=MatchingStruture)
    raw_answer = response.choices[0].message.content
    response = MatchingStruture.model_validate_json(raw_answer)

    return response



if __name__ == "__main__":
    jd_path = r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\raw\jd_information_technology.txt"
    cv = "Skills\nA+ Certified, Active Directory, billing, business process, C, cash flow, Cisco, Cisco Routers, Hardware, network systems, Content management, contracts, Coral, databases, Database, delivery, disaster recovery, Email, ERP, extranet, financial, Firewalls, internet marketing, laptops, Lotus, Microsoft Access I, Microsoft Access, Microsoft Certified Professional, Microsoft Certified, Microsoft Exchange, Office, Microsoft Office 97, Windows, Windows 2000, 2000, Microsoft Windows 2003, Microsoft NT 4, NT 4 0, Windows NT 4 0, Microsoft Windows NT4 0, Windows XP, Navision, network security, network, Office Suites, Operating Systems, Organizing, Report Writer I, reporting, SCO Unix, servers, Microsoft SQL, SQL 2000, Sybase, System Administrator, phones, phone, training employees, Visio, voice mail, web site, website"
    with open(jd_path,"r", encoding="utf-8") as f:
        jd = f.read()

    response = skill_matcher(
        jd,cv
    )
    print(type(response))
  
    
