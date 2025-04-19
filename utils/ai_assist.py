from django.conf import settings

# Determine whether to use Azure OpenAI or OpenAI API key
_USE_AZURE = bool(settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_DEPLOYMENT_NAME)
if _USE_AZURE:
    from azure.ai.openai import OpenAIClient
    from azure.core.credentials import AzureKeyCredential
    _azure_client = OpenAIClient(settings.AZURE_OPENAI_ENDPOINT, AzureKeyCredential(settings.AZURE_OPENAI_KEY))
    _deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
else:
    import openai

def get_hint(problem_description, user_attempt=None):
    prompt = (
        "You are an AI coding assistant. Provide a helpful hint for the following problem:\n" + problem_description
    )
    if user_attempt:
        prompt += "\nUser attempt:\n" + user_attempt
    if _USE_AZURE:
        response = _azure_client.get_chat_completions(
            deployment_id=_deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    else:
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content

def get_solution(problem_description, user_attempt=None):
    prompt = (
        "You are an AI coding assistant. Provide a full solution and explanation for the following problem:\n" + problem_description
    )
    if user_attempt:
        prompt += "\nUser attempt:\n" + user_attempt
    if _USE_AZURE:
        response = _azure_client.get_chat_completions(
            deployment_id=_deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return {"solution": response.choices[0].message.content}
    else:
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return {"solution": response.choices[0].message.content}