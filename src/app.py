from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from data_preprocessing.loader import read_pdf_to_csv, data_loader_from_csv, store_data_to_json, read_pdf_to_txt
import uuid
import logging
import os
import json
from graph.nodes import extract_jd
from graph.build_graph import get_graph
import uvicorn
from gateway.cost_tracker import get_summary

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI()

template = Jinja2Templates(directory="template")


@app.get("/")
async def home(request: Request):
    return template.TemplateResponse(request, "main.html", context={})

@app.post("/upload_cv/")
async def upload_multiple_cv(files: list[UploadFile] = File(...)):
    file_uploaded = []
    file_denided = []
    id = uuid.uuid4()
    directory = f"../data/raw/{id}/cv"
    os.makedirs(directory, exist_ok=True)

    for file in files:
        if not file.filename.endswith(".pdf"):
            file_uploaded.append(file.filename)
            continue
        print(file.filename)
        path = os.path.join(directory, file.filename)
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
        file_uploaded.append(file.filename)

    path = f"../data/raw/{id}/cv"
    destination = f"../data/raw/{id}"
    read_pdf_to_csv(type="multiple", file_or_path=path)
    logging.info(f"CSV file created at {destination}")

    candidates = data_loader_from_csv(f"{destination}/cv/Resume.csv")
    dict_candidates = [candidate.to_dict() for candidate in candidates]
    logging.info(f"Data from csv has been read")

    store_data_to_json(
        ls=dict_candidates,
        path=f"../data/preprocessed/{id}"
    )
    logging.info(f"Data has been stored at ./data/preprocessed/{id}")

    return {
        "id": id,
        "file_uploaded": file_uploaded,
        "file_denided" : file_denided
    }

@app.post("/upload_jd/{id}")
async def upload_jd(id: str, file: UploadFile = File(...)):
    file_uploaded = []
    file_denided = []
    directory = f"../data/raw/{id}/jd"
    os.makedirs(directory, exist_ok=True)

    
    if not file.filename.endswith(".pdf"):
        file_uploaded.append(file.filename)
        return {
            "error": "Please upload a pdf file"
        }
    print(file.filename)
    path = os.path.join(directory, file.filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    file_uploaded.append(file.filename)
    read_pdf_to_txt(
        file_path=path,
        destination=f"../data/preprocessed/{id}/jd.txt"
    )

    return {
        "message": "JD upload successfully"
    }




@app.post("/process/{id}")
async def run_agent(id:str):
    cv_path = f"../data/preprocessed/{id}/resumes.json"
    jd_path = f"../data/preprocessed/{id}/jd.txt"

    with open(cv_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(jd_path,"r", encoding="utf-8") as f:
        jd = f.read()

    response = get_graph().invoke({
    "resume_raw_text" : data,
    "jd_raw_text": jd
    })

    messages = response.get("messages", []) if isinstance(response, dict) else []
    for message in messages:
        content = getattr(message, "content", None)
        name = getattr(message, "name", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")
            name = message.get("name")

        if name == "check_jd" and str(content).strip().lower() == "false":
            raise HTTPException(
                status_code=400,
                detail="File uploaded in JD is not a valid job description. Please upload a different JD file."
            )


    #FOR DEV MODE
    global full_answer
    full_answer = response
    
    summary = response.get("summary",None)
    
    return  {
        "summary" : summary,
        "rejected_cvs" : response.get("rejected_cvs", [])
    }

@app.get("/dev_mode")
def get_full_result():
    return full_answer if full_answer else {
        "content": "No execution found"
    }

@app.get("/cost")
def get_cost():
    return get_summary()



if __name__ == "__main__":
    uvicorn.run("app:app", port=8080,reload=True)