from pathlib import Path
import sys
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)
from init_model.client import LLM_Client
from langchain.messages import SystemMessage, HumanMessage
from schema.cv_schema import MatchingStruture, Final_evaluation
from langchain.messages import AIMessage
import os
from dotenv import load_dotenv
from gateway.router import gateway


load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def orchestrator(jd_title_or_summary: str, skill_result: MatchingStruture, experience_result: MatchingStruture,education_result: MatchingStruture,):
    """Synthesize three independent subagent evaluations into a final screening result.

    This function does not re-read the raw resume or job description text. It only
    combines the already-computed results from skill_matcher, experience_scorer,
    and education_scorer into a single overall score and a coherent final narrative.
    The recommendation label (shortlist / borderline / reject) is deliberately NOT
    decided by the LLM here — it is assigned afterward in the graph layer using a
    fixed numeric threshold on overall_score, so that the human-in-the-loop branching
    logic stays deterministic and consistent across every candidate in a batch.

    Args:
        jd_title_or_summary: A short string identifying the job/position, used only
            to give the LLM context on what "fit" means for this role (e.g. whether
            skills should be weighted more heavily than experience).
        skill_result: The SubagentResult returned by skill_matcher.
        experience_result: The SubagentResult returned by experience_scorer.
        education_result: The SubagentResult returned by education_scorer.

    Returns:
        A CVScreeningResult containing:
            overall_score (int): Weighted overall fit score from 0 to 100.
            final_reasoning (str): A synthesized explanation covering all three
                evaluation dimensions.
            (skill_result, experience_result, education_result are also carried
            through into CVScreeningResult unchanged, for full auditability.)

    Note:
        The recommendation field of CVScreeningResult is populated outside this
        function, not by the LLM, to keep borderline-case detection consistent
        and reproducible across the whole batch.
    """
    sys_prompt = """
    You are a senior recruiter assistant responsible for making a final hiring recommendation by synthesizing three independent evaluations of a candidate: skill match, experience match, and education match. You do not re-evaluate the resume or job description yourself — you only work with the scores and reasoning already produced by the three specialist evaluators.

Your task:
1. Consider the three provided evaluations (skill, experience, education), including their individual scores and reasoning.
2. Weigh the three dimensions appropriately: skill match and experience match are generally the primary drivers of fit for most technical roles, while education match is a baseline qualifier rather than a differentiator, unless the job description explicitly states otherwise.
3. Produce an overall score from 0 to 100 that reflects the candidate's overall fit for the role.
4. Write a concise final reasoning that synthesizes the three inputs into a single coherent narrative — do not simply repeat the three reasoning texts back to back.

Critical rules:
- Do NOT introduce any new skill, experience detail, or education fact that was not present in the three input evaluations. Your role is synthesis, not re-evaluation from scratch.
- If the three scores strongly disagree with each other (e.g. skill score is very high but experience score is very low), explicitly acknowledge this tension in your reasoning rather than silently averaging it away.
- Be honest and calibrated — do not inflate the overall score to appear more positive than the underlying evidence supports.

Output strictly in this JSON structure:
{
  "overall_score": <integer 0-100>,
  "final_reasoning": "<3-5 sentence synthesis referencing all three dimensions>"
}
"""
    # client = LLM_Client(
    #     model_name="openai/gpt-oss-120b",
    #     provider="groq"
    # )
    # model = client.get_model()
    # structured_model = model.with_structured_output(Final_evaluation)

    skill_result = skill_result.model_dump_json(indent=4)
    experience_result = experience_result.model_dump_json(indent=4)
    education_result = education_result.model_dump_json(indent=4)


    input = f"""
   Job Title / Context: {jd_title_or_summary}

Skill Evaluation:
{skill_result}

Experience Evaluation:
{experience_result}

Education Evaluation:
{education_result}

Synthesize these three evaluations into a single overall assessment, following your instructions exactly. Return only the JSON object, with no extra text before or after it.
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

    response = gateway.call_llm("orchestrator",messages=messages, format=Final_evaluation)
    raw_answer = response.choices[0].message.content
    response = Final_evaluation.model_validate_json(raw_answer)

    return response


if __name__ == "__main__":
    pass
    
