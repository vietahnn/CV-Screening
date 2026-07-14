from litellm import completion_cost
from datetime import datetime
from gateway.config import provider_mapping

_records = []

def log_call(role, response):
    model = response.model
    provider = provider_mapping[model]
    cost = completion_cost(completion_response = response, model=f"{provider}/{model}")
    input_token = response.usage.prompt_tokens
    output_token = response.usage.completion_tokens
    

    _records.append({
        "role": role,
        "model_used" : model,
        "prompt_tokens": input_token,
        "completion_tokens": output_token,
        "cost" : cost,
        "timestamp" : datetime.now()
    })

def get_summary():
    summary = {
        "total_cost" : 0,
        "call_models_count" : 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0
    }

    for r in _records:
        summary["total_cost"] += r["cost"]
        summary["call_models_count"] += 1
        summary["total_input_tokens"] += r["prompt_tokens"]
        summary["total_output_tokens"] += r["completion_tokens"]
        summary[r["role"] + " " + r["model_used"]] = summary.get(r["role"], 0) + r["cost"]

    return summary
