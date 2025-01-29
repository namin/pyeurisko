import ollama

model = 'qwen2.5'

def generate(prompt, max_tokens=100, temperature=1.0):
    response = ollama.generate(
        model=model, prompt=prompt,
        options={
            'max_tokens': max_tokens,
            'temperature': temperature
        }
    )
    return response['response']
