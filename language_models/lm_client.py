from ollama import Client
from ollama import ChatResponse
import sys

client: ChatResponse = Client(
  host='http://fruit.alexluo.com:11434',
  headers={'x-some-header': 'some-value'}
)

def query_lm(query: str='Who are you?'):
    response = client.chat(
        model='qwen2.5:14b',
        messages=[{
            'role': 'user',
            'content': query,
        },],
        stream=True)

    
    for chunk in response:
        print(chunk['message']['content'], end='', flush=True)
    print()

# print(response.message.content)
if __name__ == '__main__':
    client.pull('qwen2.5:14b')
    if len(sys.argv) > 1:
        query_lm(" ".join(sys.argv[1:]))
    else:
        query_lm()
