import pandas as pd
from data_preprocessing.schema import Candidate
from typing import Literal, Optional, Union
import re
import os
import json
import csv
import uuid
from pypdf import PdfReader
from utils import extract_cv_info


def read_pdf_to_csv(file_or_path: Union[list,str],type: Literal["multiple","single"] = "multiple", destination: str = None):
    if type =="multiple":
        header = ["ID","filename","name","email","social_links","Resume_str"]
        data = []
        list_of_files = os.listdir(file_or_path)
        for file in list_of_files:
            if not file.endswith(".pdf"): 
                continue
            id = uuid.uuid4()
            path = os.path.join(file_or_path, file)
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() +"\n"
            info = extract_cv_info(text)
            
            data.append([id, file, info["candidate_name"], info["email"], info["social_links"] ,text])
        
        if destination != None:
            csv_path = os.path.join(destination,"Resume.csv")
        else:
            csv_path = os.path.join(file_or_path,"Resume.csv")
        with open(csv_path,"w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)


    if type == "single":
        header = ["ID","filename","Resume_str"]
        data = []
        
        id = uuid.uuid4()
        path = os.path.join(file_or_path)
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() +"\n"
        info = extract_cv_info(text)
        data.append([id, os.path.basename(path), text])

        csv_path = os.path.join(file_or_path,"Resume.csv")
        with open(csv_path,"w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)
            
def read_pdf_to_txt(file_path, destination):   
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() +"\n"

        with open(destination, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        raise ValueError(str(e))
        

def cleaner(content: str) -> str:
    # 1. Protect time ranges like "Jun 2004 to Jul 2007" from being split
    content = re.sub(r"\s+to\s+", " to ", content)

    # 2. Protect punctuation formatting for locations (e.g., City, State)
    content = re.sub(r"\s*,\s*", ", ", content)
    content = re.sub(r"\s*－\s*", " － ", content)

    # 3. Replace large structural gaps (4 or more spaces) with newlines
    content = re.sub(r" {4,}", "\n", content)

    # 4. Strip leading/trailing whitespaces and remove empty lines
    lines = [line.strip() for line in content.split("\n")]
    lines = [line for line in lines if line]

    return "\n".join(lines)


# Tới đây rồi
def data_loader_from_csv(path: str):
    list_of_resumes = []
    data = pd.read_csv(path)

    for index, row in data.iterrows():
        id = row["ID"]
        filename = row.get("filename") if "filename" in row else None
        resume = cleaner(row["Resume_str"])
        candidate_name = row["name"]
        email = row["email"]
        social_links = row["social_links"]

        list_of_resumes.append(Candidate(id, candidate_name,email,social_links ,resume, filename))
    
    return list_of_resumes

def store_data_to_json(ls : list[Candidate] |  None, path, type: str = "resumes"):
    
    if ls == None:
        raise ValueError("Function (data_preprocessing/loader/store_data_to_json) :Input data is None. Try again !!!!")

    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, f"{type}.json")
    with open(path, "w", encoding= "utf-8") as f:
        json.dump(ls,f, ensure_ascii=False, indent=4)
        



if __name__ == "__main__":
    # path = r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\raw\Resume.csv"
    # candidates = data_loader_from_csv(path)
    # dict_candidates = [candidate.to_dict() for candidate in candidates]
    # store_data_to_json(
    #     ls=dict_candidates,
    #     path=r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\processed"
    # )

    path = r"C:\Users\dovie\OneDrive\Desktop\vietanh\LLM & Agent Course\CV-Screening\data\raw\cv"
    read_pdf_to_csv(file_or_path=path)