import re

def clean_json_response(response: str) -> str:
    """
    Cleans the AI response by removing markdown code blocks and extra text.
    """
    # Remove markdown code blocks like ```json ... ```
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        return json_match.group(1).strip()
        
    # If no code block, try to find the first '{' or '[' and last '}' or ']'
    start_idx = response.find('{')
    if start_idx == -1:
        start_idx = response.find('[')
            
    end_idx = response.rfind('}')
    if end_idx == -1:
        end_idx = response.rfind(']')
            
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return response[start_idx:end_idx + 1].strip()
            
    return response.strip()