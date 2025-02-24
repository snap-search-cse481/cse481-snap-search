from ollama import ChatResponse, Client, ListResponse
import ollama
import sys
from typing import Optional

class OllamaClient:

    dummy_prompt: str = "You are a helpful assistant."

    filter_summarize_prompt: str = "You are an assistant specialized in extracting and summarizing factual information from provided text excerpts. Your task is to read the given excerpts from various websites and determine which individual is mentioned most frequently, assuming this is the person of interest. Then, using only the information provided in the texts, provide a concise, factual summary about this person. If some sources do not contain relevant details, simply ignore them and focus on those that do. It is critical that you strictly adhere to the provided excerpts, avoid making up any details, and clearly indicate any ambiguities if present. Focus on the basics of a person profile, like the persons's name, job, etc. Keep your summary concise and under 100 words."

    def __init__(self,
                 host: str='http://fruit.alexluo.com:11434',
                 model: str='qwen2.5:14b',
                 system_prompt: Optional[str]=None,
                 custom_name: Optional[str]=None):
        self.client: ChatResponse = Client(
            host=host,
            headers={'x-some-header': 'some-value'}
        )
        self.model = model
        assert (system_prompt is None) == (custom_name is None), "Must supply a custom model name if customizing system prompot"
        self.system_prompt = system_prompt
        self.custom_name = custom_name

        # Download the model if necessary
        res: ListResponse = self.client.list()
        model_names = [x.model for x in res.models]
        if model not in model_names:
            print(f'Model {model} not found. Downloading...')
            self.client.pull(model)

        # Create a new model based on supplied system prompt
        if system_prompt is not None:
            print(f"Create a new model based on custom system prompt...")
            self.client.create(model=self.custom_name, from_=self.model, system=system_prompt)
            self.model = self.custom_name

    def query_lm(self, query: str='Who are you?'):
        msg = {'role': 'user', 'content': query,}
        response = self.client.chat(
            model=self.model,
            messages=[msg],
            options={'num_ctx': 2048},
            stream=True)
        
        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)
        print()


if __name__ == '__main__':
    client = OllamaClient(system_prompt=OllamaClient.filter_summarize_prompt,
                          custom_name='filter_summarize')
    if len(sys.argv) > 1:
        client.query_lm(" ".join(sys.argv[1:]))
    else:
        client.query_lm()
