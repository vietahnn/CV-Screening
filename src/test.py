from graph.build_graph import get_graph
from pydantic import BaseModel
from graph.nodes import extract_jd
from gateway.cost_tracker import get_summary
import json
from utils import extract_response
from pprint import pprint

cv_path = f"../data/preprocessed/b93b4afe-1881-4b39-9c3a-7a3598c8ad5a/resumes.json"
jd_path = f"../data/preprocessed/b93b4afe-1881-4b39-9c3a-7a3598c8ad5a/jd.txt"

with open(cv_path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(jd_path,"r", encoding="utf-8") as f:
    jd = f.read()



# response = get_graph().invoke({
#     "resume_raw_text" : data,
#     "jd_raw_text": jd
#     })

# result = extract_response(response)

# pprint(result)

pprint(data)




















