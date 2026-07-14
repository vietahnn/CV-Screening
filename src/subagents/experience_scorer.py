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


def experience_scorer( jd_experience: str, cv_experience:str, min_experience_years: int):
    """Evaluate how well a candidate's work experience matches a job description.

    This subagent focuses exclusively on the experience dimension of candidate
    screening. It considers years of relevant experience, seniority level implied
    by past roles, and how closely past responsibilities align with what the job
    description requires.

    Args:
        jd_text: The full text of the job description, used to extract experience
            requirements such as minimum years, seniority level, and expected
            responsibilities.
        cv_experience_section: The candidate's resume text relevant to work
            experience. This may be an isolated "Experience" section if the CV
            cleaning step successfully separated it, or the full cleaned resume
            text as a fallback if section splitting failed.

    Returns:
        A dictionary with the following keys:
            score (int): Experience match score from 0 to 100.
            matched_items (list[str]): Relevant experience highlights that align
                with the job description's requirements.
            missing_items (list[str]): Experience requirements from the job
                description that the candidate does not clearly meet.
            reasoning (str): A short explanation of the score, grounded strictly
                in the provided resume text.

    Note:
        This function does not evaluate skills or education — those are handled
        by separate subagents (skill_matcher, education_scorer) so that each aspect
        of the candidate is scored independently and can be audited on its own.
    """
    sys_prompt = """
   You are a specialized recruiter assistant focused ONLY on comparing a candidate's work experience against pre-extracted job requirements. You do not read raw job description text — the requirements have already been extracted. You do not evaluate skills or education.

Your task:
Given the minimum years of experience required, the type/domain of experience required, and the candidate's experience text, judge how closely the candidate's experience matches what the job requires.

Critical rules:
- Base your judgment only on what is explicitly written in the candidate's experience text — do not assume responsibilities that are not described.
- When calculating years of experience, only count roles that are clearly relevant to the required experience domain provided; unrelated past roles should not inflate the score.
- Do NOT fabricate or assume any responsibility, achievement, or job title that is not stated in the text.
- If duration or dates are ambiguous, note this explicitly in your reasoning rather than guessing a specific number.

Output strictly in this JSON structure:
{
  "score": <integer 0-100>,
  "matched_items": [<relevant experience highlights that align with the requirement, as short strings>],
  "missing_items": [<any part of the requirement not clearly met>],
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
   Required minimum experience: {min_experience_years} years
Required experience domain/type: {jd_experience}

Candidate's Experience:
{cv_experience}

Evaluate how well this candidate's experience matches the requirement above, following your instructions exactly. Return only the JSON object, with no extra text before or after it.
"""

    # response  = structured_model.invoke(
    #         [
    #             SystemMessage(content=sys_prompt),
    #             HumanMessage(content=input)
    #         ])
    # print(response)

    messages = [
        {"role":"system", "content": sys_prompt},
        {"role":"user", "content": input}
    ]

    response = gateway.call_llm("experience_scorer",messages=messages, format=MatchingStruture)
    raw_answer = response.choices[0].message.content
    response = MatchingStruture.model_validate_json(raw_answer)

    return response


if __name__ == "__main__":
    jd_path = r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\raw\jd_information_technology.txt"
    cv = """Experience  

Information Technology Specialist, 02/2019 to Current
Company Name – City, State
Coordinated installation of Microsoft software systems and collaborated with user experience team on design and implementation of new features  Kept hardware and software systems current with latest patches and current licenses  Provided on-site technical support after project implementation and recommended product changes and upgrades to product managers  Trained new employees on support processes, procedures and knowledge base  Mentored other technical engineers and support professionals to provide professional development and skill enhancement  Researched, documented and escalated support cases to higher levels of support when unable to resolve issues using available resources  

Shift Leader, 11/2016 to Current
Company Name – City, State
Assigned daily tasks to employees and monitored activity and task completion.  Diligently restocked work stations and display cases.  Routinely moved and stocked food products weighing up to 40 pounds.  Performed all position responsibilities accurately and in a timely manner.  Strictly followed all cash, security, inventory and labor policies and procedures.  Maintained clean and safe environment, including in the kitchen, bathrooms, building exterior, parking lot, dumpster and sidewalk.  Stored food in designated containers and storage areas to prevent spoilage or cross-contamination.  Reported to all shifts wearing a neat, clean and unwrinkled uniform.  Handled currency and credit transactions quickly and accurately.  Followed food safety procedures according to company policies and health and sanitation regulations.  

Customer Service Representative, 04/2017 to 09/2017
Company Name – City, State
Contacted customer to follow up on purchases, suggest new merchandise and inform them about promotions and upcoming events.  Operated a POS system to itemize and complete an average of 50 customer purchases.  Routinely answered customer questions regarding merchandise and pricing."""
    with open(jd_path,"r", encoding="utf-8") as f:
        jd = f.read()

    response = experience_scorer(
        jd,cv
    )
  
    
