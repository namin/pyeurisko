import ollama
import logging

logger = logging.getLogger(__name__)

model = 'qwen2.5'

def generate(prompt, max_tokens=100, temperature=1.0):
    logger.info(f"Sending request to ollama (model={model}, max_tokens={max_tokens}, temp={temperature})")
    logger.debug(f"Prompt:\n{prompt}")
    
    try:
        response = ollama.generate(
            model=model, prompt=prompt,
            options={
                'max_tokens': max_tokens,
                'temperature': temperature
            }
        )
        logger.info("Received response from ollama")
        logger.debug(f"Response:\n{response['response']}")
        return response['response']
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        # Return a simple JSON-like string that won't break the parsing
        return '{"core_concepts": [], "key_operations": [], "dependencies": [], "potential_areas": [], "success_criteria": []}'
