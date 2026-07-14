from pprint import pprint
import re

def extract_cv_info(resume_str):
    # 1. Extract candidate name (Get the first non-empty line of the CV)
    name_match = re.search(r'^(?:\s*")?([^\n]+)', resume_str)
    name = name_match.group(1).strip() if name_match else None
    
    # 2. Extract Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_str)
    email = email_match.group(0).strip() if email_match else None
    
    # 3. Extract social media links (LinkedIn, GitHub)
    social_links = re.findall(r'((?:linkedin\.com|github\.com)/[^\s|]+)', resume_str)
    
    # Clean up social media links by stripping any trailing or leading whitespaces
    social_links = [link.strip() for link in social_links]
    
    return {
        "candidate_name": name,
        "email": email,
        "social_links": social_links
    }




if __name__ =="__main__":

    cv_example = """Nguyen Van An
    AI Engineer
    an.nguyen.aieng@gmail.com  |  +84 908 123 456  |  Ho Chi Minh City, Vietnam  |  linkedin.com/in/annguyen-ai  | 
    github.com/annguyen-ai
    SUMMARY..."""

    print(extract_cv_info(cv_example))
















