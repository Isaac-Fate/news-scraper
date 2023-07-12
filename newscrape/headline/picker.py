from typing import Optional
import re
import openai

SINGLE_QUOTE_STRING_RE = re.compile(r"^'.*'$")
DOUBLE_QUOTE_STRING_RE = re.compile(r'^".*"$')

def prepare_prompt(headlines: list[str]) -> str:
        
    prompt = (
        'The following is a list of possible news headlines: {headlines}'
        'However, there is one and only one suitable headline.'
        'The most suitable news headline you choose is:'
    ).format(
        headlines=headlines
    )
    
    return prompt

def remove_string_quotes(s: str) -> str:
    
    if SINGLE_QUOTE_STRING_RE.match(s) is not None:
        return s.removeprefix('\'').removesuffix('\'')
    
    if DOUBLE_QUOTE_STRING_RE.match(s) is not None:
        return s.removeprefix('"').removesuffix('"')
    
    return s

class NewsHeadlinePicker:
    
    def __init__(
            self, 
            model_name: str = 'gpt-3.5-turbo-16k', 
            temperature: float = 0.0
        ) -> None:
        
        self._model_name = model_name
        self._temperature = temperature
        
    def pick(
            self, 
            headlines: list[str],
            temperature: Optional[float] = None
        ) -> str:
        
        # prepare the prompt
        prompt = prepare_prompt(headlines)
        
        # get response from ChatGPT
        response = self._get_response(query=prompt, temperature=temperature)
        
        # remove quotes at the two ends of the string
        headline = remove_string_quotes(response)
        
        return headline
        
    def _get_response(
            self, 
            query: str,
            temperature: Optional[float] = None
        ) -> str:
        
        if temperature is None:
            temperature = self._temperature
        
        # send request to ChatGPT
        completion = openai.ChatCompletion.create(
            model=self._model_name,
            temperature=temperature,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful agent that is good at identifying news headlines'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ]
        )
        
        # get the response message
        response = completion.choices[0].message.content
        
        return response
    
    
    