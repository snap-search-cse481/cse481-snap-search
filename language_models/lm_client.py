from ollama import Client
from ollama import ChatResponse

client: ChatResponse = Client(
  host='http://fruit.alexluo.com:11434',
  headers={'x-some-header': 'some-value'}
)

def query_lm(query: str='Why is the sky blue?'):
    response = client.chat(
        model='deepseek-r1:14b',
        messages=[{
            'role': 'user',
            'content': query,
        },],
        stream=True)

    
    for chunk in response:
        print(chunk['message']['content'], end='', flush=True)

# print(response.message.content)
if __name__ == '__main__':
    query_lm()
