from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gateway.router import gateway


def is_cv(raw_text:str) ->bool:
    sys_prompt = """
You are an expert system. Analyze the input text and determine 
if it is a CV/resume. Respond with exactly one word: "True" or "False". 
Do not include any explanations or punctuation.
"""

    input = f"Is this a cv : \n {raw_text}"
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
    text = "Nguyen Van An\nAI Engineer\nan.nguyen.aieng@gmail.com  |  +84 908 123 456  |  Ho Chi Minh City, Vietnam  |  linkedin.com/in/annguyen-ai  |\ngithub.com/annguyen-ai\nSUMMARY\nRecent Computer Science graduate with a strong foundation in machine learning and deep learning, gained\nthrough coursework, a research thesis, and a hands-on internship building NLP and computer vision prototypes.\nComfortable with Python, PyTorch, and common ML tooling; eager to apply and grow these skills on real\nproduction AI systems.\nSKILLS\nLanguages\nPython, SQL, basic C++\nML / DL\nscikit-learn, PyTorch, TensorFlow/Keras (coursework), Pandas, NumPy\nNLP / CV basics\nHugging Face Transformers (fine-tuning), OpenCV, spaCy\nTools\nGit, Jupyter, Docker (basic), Google Colab, Linux\nCloud\nBasic exposure to Google Colab GPU, AWS Free Tier (S3, EC2 basics)\nOther\nREST API basics with FastAPI, SQL querying, data cleaning/EDA\nEXPERIENCE\nAI Engineer Intern — DataViet Solutions\nHo Chi Minh City, Vietnam  |  Feb 2025 – Jul 2025 (6 months)\n\nBuilt and fine-tuned a text-classification model (PhoBERT) for customer-feedback tagging, reaching 87%\naccuracy on an internal validation set.\n\nAssisted in cleaning and labeling a 15, 000-row customer support dataset used for model training.\n\nWrote a FastAPI wrapper to serve the trained model behind a REST endpoint for the product team to test.\n\nDocumented experiments and results using MLflow under the guidance of a mentor engineer.\nResearch Assistant (Part-time) — University AI Lab\nHo Chi Minh City, Vietnam  |  Sep 2024 – Jan 2025\n\nSupported a lab project on lightweight image classification models for edge devices.\n\nRan training experiments with different data-augmentation strategies and logged results for the research team.\nPROJECTS\nVietnamese News Summarizer (Personal Project)\n\nFine-tuned a mT5 model to generate short summaries of Vietnamese news articles; deployed a demo with\nStreamlit.\n\nScraped and cleaned ~5, 000 articles to build a small training dataset.\nFruit Freshness Classifier\n\nTrained a CNN (transfer learning on MobileNetV2) to classify fruit freshness from images; 91% test accuracy.\n\nBuilt a simple Flask web app for demoing predictions from uploaded photos.\nEDUCATION\nB.Sc. in Computer Science — University of Science, VNU-HCM\nSep 2021 – Jun 2025  |  GPA: 3.4/4.0\n\nThesis: \"Fine-tuning Transformer Models for Vietnamese Text Summarization\" (Advisor-supervised).\n\nRelevant coursework: Machine Learning, Deep Learning, Data Structures & Algorithms, Probability & Statistics.\nCERTIFICATIONS\n\nDeepLearning.AI — Deep Learning Specialization (Coursera, 2024)\n\nGoogle — Introduction to Machine Learning (2024)"
    response = is_cv(raw_text=text)
    print(response)









