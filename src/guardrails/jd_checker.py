from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gateway.router import gateway


def is_jd(raw_text:str) ->bool:
    sys_prompt = """
You are an expert recruitment system. Analyze the input text and determine if it is a Job Description (JD). 

A Job Description (JD) MUST meet these criteria:
- It represents an open position from a company looking to hire.
- It uses commanding or demanding language targeting candidates (e.g., "Responsibilities:", "Requirements:", "We are looking for", "What you will do", "Qualifications:").

CRITICAL EXCLUSION RULE:
- If the text is a Curriculum Vitae (CV), Resume, or Personal Profile (describing a single person's past work history, education, personal projects, or achievements, e.g., "I am an AI Engineer", "Worked at Company X", "Education: UEH University"), you MUST classify it as FALSE. Even if it contains tech keywords, a person's resume is NOT a job description.

Respond with exactly one word: "True" or "False". Do not include any explanations, reasoning, or punctuation.
"""

    input = f"Is this a job description for recruitment : \n {raw_text}"
    message = [
        {"role": "system" , "content": sys_prompt},
        {"role" : "user", "content": input}
    ]

    response = gateway.call_llm(
        role="checker",
        messages=message,
        format=None
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    text = """Tran Thi Bich Ngoc
AI Engineer
ngoc.tran.ai.eng@gmail.com  |  +84 913 555 789  |  Ho Chi Minh City, Vietnam  |  linkedin.com/in/ngoctran-ai  | 
github.com/ngoctran-ml
SUMMARY
AI Engineer with 3+ years of experience designing, training, and deploying machine learning models into
production. Track record of shipping NLP and recommendation features used by hundreds of thousands of users,
building reusable ML pipelines, and collaborating closely with product and backend teams to turn prototypes into
reliable services.
SKILLS
Languages
Python, SQL, Bash
ML / DL
PyTorch, TensorFlow, scikit-learn, XGBoost, Optuna (hyperparameter tuning)
NLP
Hugging Face Transformers, PhoBERT, BERT fine-tuning, sentence embeddings,
RAG pipelines
MLOps
MLflow, Docker, Kubernetes (basic), Airflow, CI/CD with GitHub Actions
Cloud
AWS (SageMaker, S3, Lambda, EC2), basic GCP Vertex AI
Data
Spark (PySpark), PostgreSQL, Redis, Feature Store concepts
EXPERIENCE
AI Engineer — Fintek Digital JSC
Ho Chi Minh City, Vietnam  |  Apr 2023 – Present (2+ years)

Designed and deployed a transaction-risk scoring model (XGBoost) into production, reducing fraud losses by an
estimated 18% in its first two quarters.

Built a document-question-answering feature using a retrieval-augmented generation (RAG) pipeline over
internal policy documents, cutting average support-ticket resolution time by 30%.

Owned the model-serving layer (FastAPI + Docker on AWS ECS) and set up monitoring/alerting for data drift
and latency using CloudWatch and custom dashboards.

Mentored two incoming engineers on ML experimentation practices and code review standards.

Collaborated with backend and product teams to define API contracts and rollout plans for new ML features
(canary releases, A/B testing).
Machine Learning Engineer — CloudMinds Vietnam
Ho Chi Minh City, Vietnam  |  Jul 2021 – Mar 2023 (1 yr 9 months)

Built a product-recommendation model (collaborative filtering + content-based hybrid) that lifted click-through
rate by 12% in A/B testing.

Migrated legacy batch-scoring pipelines to Airflow, reducing manual pipeline failures by roughly 40%.

Implemented data-validation checks (Great Expectations) that caught upstream data-quality issues before they
reached training jobs.
SELECTED PROJECTS

Internal RAG chatbot template used across 3 product teams to prototype Q&A; features on their own
documents.

Open-source contribution: added a PhoBERT tokenizer fix accepted into a mid-size Vietnamese NLP toolkit
repo.

EDUCATION
B.Sc. in Computer Science — Ho Chi Minh City University of Technology (Bach Khoa)
Sep 2017 – Jun 2021
CERTIFICATIONS

AWS Certified Machine Learning – Specialty (2024)

DeepLearning.AI — Natural Language Processing Specialization (2022)



"""
    response = is_jd(raw_text=text)
    print(response)









