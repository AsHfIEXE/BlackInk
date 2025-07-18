from llama_cpp import Llama

# Download a model like https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
# and place it in the project root directory.

class AIManager:
    def __init__(self, model_path="mistral-7b-instruct-v0.2.Q4_K_M.gguf"):
        self.llm = Llama(model_path=model_path)

    def get_assistance(self, prompt):
        output = self.llm(prompt, max_tokens=100)
        return output['choices'][0]['text']
