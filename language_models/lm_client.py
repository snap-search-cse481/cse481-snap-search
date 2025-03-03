import dspy

from ollama import ChatResponse, Client, ListResponse
import ollama
import sys
from typing import Optional, List

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
                assert (system_prompt is None) == (custom_name is None), "Must supply a custom model name if customizing system prompot"
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
                    api_key=''
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

    # New method for structured extraction using DSPy
    def extract_person_info(self, text: str) -> dspy.Prediction:
        """Extract structured person information using DSPy's ChainOfThought"""
        class PersonSignature(dspy.Signature):
            """Extract person details from text. Adhere strictly to given information."""
            text = dspy.InputField(desc="Text containing personal information")
            name = dspy.OutputField()
            profession = dspy.OutputField()
            workplace = dspy.OutputField()
            email = dspy.OutputField()
            phone = dspy.OutputField()
            fun_facts = dspy.OutputField(format=list)

        extractor = dspy.ChainOfThought(PersonSignature)
        return extractor(text=text)

if __name__ == '__main__':
    client = OllamaClient()
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        
        # Using DSPy for structured extraction
        result = client.extract_person_info(input_text)
        
        # Formatting the output
        print(f"Name: {result.name}")
        print(f"Profession: {result.profession}")
        print(f"Workplace: {result.workplace}")
        print(f"Email: {result.email}")
        print(f"Phone: {result.phone}")
        print(f"Fun Facts: {result.fun_facts}")

    else:
        # Fallback to original query method
        client.query_lm()