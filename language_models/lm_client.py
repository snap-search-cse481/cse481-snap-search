import dspy

from ollama import ChatResponse, Client, ListResponse
import ollama
import sys
from typing import Optional, List, Dict, Any

class OllamaClient:
    dummy_prompt: str = "You are a helpful assistant."
    filter_summarize_prompt: str = "You are an assistant specialized in extracting and summarizing factual information from provided text excerpts. Your task is to read the given excerpts from various websites and determine which individual is mentioned most frequently, assuming this is the person of interest. Then, using only the information provided in the texts, provide a concise, factual summary about this person. If some sources do not contain relevant details, simply ignore them and focus on those that do. It is critical that you strictly adhere to the provided excerpts, avoid making up any details, and clearly indicate any ambiguities if present. Focus on the basics of a person profile, like the persons's name, job, etc. Keep your summary concise and under 100 words."

    default_servers: List[str] = ['http://fruit.alexluo.com:11435', 'http://fruit.alexluo.com:11434']

    def __init__(self,
                 hosts: List[str] = default_servers,
                 model: str = 'qwen2.5:3b',
                 system_prompt: Optional[str] = None,
                 custom_name: Optional[str] = None):
        for host in hosts:
            try:
                # Original client initialization
                self.client: ChatResponse = Client(host=host, headers={'x-some-header': 'some-value'})
                self.model = model
                assert (system_prompt is None) == (custom_name is None), "Must supply a custom model name if customizing system prompt"
                self.system_prompt = system_prompt
                self.custom_name = custom_name

                # Original model management
                res: ListResponse = self.client.list()
                model_names = [x.model for x in res.models]
                if model not in model_names:
                    print(f'Model {model} not found. Downloading...')
                    self.client.pull(model)

                if system_prompt is not None:
                    print(f"Create a new model based on custom system prompt...")
                    self.client.create(model=self.custom_name, from_=self.model, system=system_prompt)
                    self.model = self.custom_name
                
                # DSPy configuration added
                # Format model name according to DSPy's Ollama convention
                dspy_model_name = f'ollama_chat/{self.model}'
                self.dspy_lm = dspy.LM(
                    model=dspy_model_name,
                    api_base=host,
                    api_key='',
                    cache=False  # Disable caching
                )
                dspy.configure(lm=self.dspy_lm)
                # print(f"Configured DSPy with model: {dspy_model_name}")

                # print(f"Using server: {host}")
                return
            except ConnectionError as e:
                print(f"Server connection error: {e}")
        
        raise ConnectionError("Could not connect to any server")

    # Original query method remains unchanged
    def query_lm(self, query: str = 'Who are you?'):
        msg = {'role': 'user', 'content': query,}
        response = self.client.chat(
            model=self.model,
            messages=[msg],
            options={'num_ctx': 12288},
            stream=True,
            keep_alive=15)
        
        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)
        print()

    # Improved method for structured extraction using DSPy
    def extract_person_info(self, text: str) -> Dict[str, Any]:
        """Extract structured person information using DSPy's ChainOfThought"""
        
        # First, use a simpler approach to identify the person's name
        class IdentifyPersonSignature(dspy.Signature):
            """Identify the most frequently mentioned person in the text."""
            text = dspy.InputField(desc="Text containing information about various people")
            person_name = dspy.OutputField(desc="The full name of the most frequently mentioned person")
        
        identify = dspy.ChainOfThought(IdentifyPersonSignature)
        name_result = identify(text=text)
        
        # Then use a direct approach with the ollama client for better extraction
        prompt = f"""
        Based on the following text, extract structured information about {name_result.person_name}.
        Text: {text}
        
        Provide a JSON object with the following fields:
        - name: Full name
        - profession: Current job or profession
        - workplace: Current workplace or affiliation
        - email: Email address of person (only show emails explicitly stated in the provided text. Do not make up any email addresses or combine to make one based on your own conclusion). If multiple specifically found, list all found emails
        - fun_facts: A list of 3-5 interesting facts strictly about the person
        
        If any field is not available in the text, leave it blank or empty list for fun_facts.
        Format your response ONLY as valid JSON with these exact field names.
        """
        
        # Use direct ollama client for better structured response
        msg = {'role': 'user', 'content': prompt}
        response = self.client.chat(
            model=self.model,
            messages=[msg],
            options={'num_ctx': 12288},
            stream=False,
            keep_alive=15)
        
        response_text = response['message']['content']
        
        # Extract JSON part from response
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no json code block, try to find anything that looks like a JSON object
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text
        
        try:
            # Try to parse the JSON
            person_data = json.loads(json_str)
            return person_data
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured dict with the raw text
            print("Failed to parse JSON from model response. Returning raw text.")
            return {
                "name": name_result.person_name,
                "profession": "",
                "workplace": "",
                "email": "",
                "fun_facts": ["Information extraction failed"],
                "raw_response": response_text
            }

if __name__ == '__main__':
    client = OllamaClient()
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        
        # Using improved extraction
        result = client.extract_person_info(input_text)
        
        # Formatting the output
        print(f"Name: {result.get('name', '')}")
        print(f"Profession: {result.get('profession', '')}")
        print(f"Workplace: {result.get('workplace', '')}")
        print(f"Email: {result.get('email', '')}")
        print(f"Fun Facts:")
        for fact in result.get('fun_facts', []):
            print(f"- {fact}")

    else:
        # Fallback to original query method
        client.query_lm()   