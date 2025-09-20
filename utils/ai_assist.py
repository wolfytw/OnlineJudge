import json
from options.options import SysOptions

# Determine whether to use Azure OpenAI or OpenAI API
def _use_azure():
    return bool(SysOptions.azure_openai_endpoint and SysOptions.azure_openai_key and SysOptions.azure_openai_deployment_name)

def _get_openai_client():
    """Get OpenAI client based on configuration"""
    if _use_azure():
        try:
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=SysOptions.azure_openai_key,
                api_version="2024-02-01",
                azure_endpoint=SysOptions.azure_openai_endpoint
            )
        except ImportError:
            raise ImportError("Please install openai>=1.0.0 to use Azure OpenAI")
    else:
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=SysOptions.openai_api_key,
                base_url=SysOptions.openai_base_url if SysOptions.openai_base_url else "https://api.openai.com/v1"
            )
        except ImportError:
            raise ImportError("Please install openai>=1.0.0 to use OpenAI API")

def _get_chat_completion(messages, max_tokens=500, temperature=0.7):
    """Get chat completion from OpenAI or Azure OpenAI"""
    client = _get_openai_client()
    
    if _use_azure():
        model = SysOptions.azure_openai_deployment_name
    else:
        model = SysOptions.openai_model or "gpt-3.5-turbo"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

import json
from options.options import SysOptions

# Determine whether to use Azure OpenAI or OpenAI API
def _use_azure():
    return bool(SysOptions.azure_openai_endpoint and SysOptions.azure_openai_key and SysOptions.azure_openai_deployment_name)

def _get_openai_client():
    """Get OpenAI client based on configuration"""
    if _use_azure():
        try:
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=SysOptions.azure_openai_key,
                api_version="2024-02-01",
                azure_endpoint=SysOptions.azure_openai_endpoint
            )
        except ImportError:
            raise ImportError("Please install openai>=1.0.0 to use Azure OpenAI")
    else:
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=SysOptions.openai_api_key,
                base_url=SysOptions.openai_base_url if SysOptions.openai_base_url else "https://api.openai.com/v1"
            )
        except ImportError:
            raise ImportError("Please install openai>=1.0.0 to use OpenAI API")

def _get_chat_completion(messages, max_tokens=500, temperature=0.7):
    """Get chat completion from OpenAI or Azure OpenAI"""
    client = _get_openai_client()
    
    if _use_azure():
        model = SysOptions.azure_openai_deployment_name
    else:
        model = SysOptions.openai_model or "gpt-3.5-turbo"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_hint(problem_description, user_attempt=None):
    """Get AI hint for a problem"""
    prompt = (
        "You are an AI coding assistant. Provide a helpful hint for the following problem:\n" + problem_description
    )
    if user_attempt:
        prompt += "\nUser attempt:\n" + user_attempt
    
    messages = [
        {"role": "system", "content": "You are a helpful programming assistant. Provide hints without giving away the complete solution."},
        {"role": "user", "content": prompt}
    ]
    
    return _get_chat_completion(messages, max_tokens=300, temperature=0.7)

def get_solution(problem_description, user_attempt=None):
    """Get AI solution for a problem"""
    prompt = (
        "You are an AI coding assistant. Provide a complete solution and explanation for the following problem:\n" + problem_description
    )
    if user_attempt:
        prompt += "\nUser attempt:\n" + user_attempt
    
    messages = [
        {"role": "system", "content": "You are a helpful programming assistant. Provide complete solutions with clear explanations."},
        {"role": "user", "content": prompt}
    ]
    
    solution_content = _get_chat_completion(messages, max_tokens=1000, temperature=0.7)
    return {"solution": solution_content}

def chat_with_ai(problem_description, chat_history, user_message):
    """Handle AI chat for problem solving"""
    # Build conversation context
    messages = [
        {"role": "system", "content": f"You are a helpful programming assistant helping with this problem:\n{problem_description}\nProvide helpful guidance and answer questions about the problem."}
    ]
    
    # Add chat history
    for entry in chat_history[-10:]:  # Keep last 10 messages for context
        messages.append({"role": "user" if entry.get("is_user") else "assistant", "content": entry.get("message", "")})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    response = _get_chat_completion(messages, max_tokens=500, temperature=0.7)
    return response