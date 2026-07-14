import os


model_list = [
    {
        "model_name": "skills_matcher",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "gpt-oss-120b"}
    },
    {
        "model_name": "education_scorer",
        "litellm_params": {
            "model": "groq/llama-3.1-8b-instant",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "llama-3.1-8b-instant"}
    },
    {
        "model_name": "experience_scorer",
        "litellm_params": {
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "llama-3.3-70b-versatile"}
    },
    {
        "model_name": "orchestrator",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "gpt-oss-120b"}
    },
        {
        "model_name": "extract_info",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "gpt-oss-120b"}
    },
            {
        "model_name": "checker",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "gpt-oss-120b"}
    },
    {
        "model_name": "fallback_model",
        "litellm_params": {
            "model": "gemini/gemini-2.5-flash",
            "api_key": os.getenv("GOOGLE_API_KEY"),
        },
        "model_info": {"id": "gemini-1.5-flash"}
    },
    
]



fallbacks = [
    {"skills_matcher": ["fallback_model"] },
    {"education_scorer": ["fallback_model"] },
    {"experience_scorer": ["fallback_model"] },
    {"orchestrator": ["fallback_model"] },
    {"extract_info": ["fallback_model"] },
    {"checker": ["fallback_model"] },
]

provider_mapping = {
    "openai/gpt-oss-120b" : "groq",
    "llama-3.1-8b-instant" : "groq",
    "llama-3.3-70b-versatile" : "groq",
    "gemini-2.5-flash" : "gemini",
    
}