import os
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
load_dotenv()
VECTORIZE_RETRIEVAL_ENDPOINT = "https://api.vectorize.io/v1/org/e6ae581f-f84b-4a61-a5d3-6577191030a4/pipelines/aip098f7-e353-4183-a2f6-6d3d35c98192/retrieval"
VECTORIZE_API_TOKEN = os.environ.get("VECTORIZE_API_TOKEN", "<token>")


class RagServices:
    default_prompt = """
            Tu sei un assistente esperto del Salento nel periodo alto-medioevale. 
            Rispondi alla seguente domanda utilizzando solo le informazioni fornite nel contesto.
            Se le informazioni nel contesto non sono sufficienti per rispondere alla domanda, dillo chiaramente.
            """
    prompt_1 = """
            Tu sei una guida turistica esperto del Salento nel periodo alto-medioevale. 
            Rispondi alla seguente domanda utilizzando solo le informazioni fornite nel contesto.
            Se le informazioni nel contesto non sono sufficienti per rispondere alla domanda, dillo chiaramente.
    """
    prompt_2 = """
            Tu sei un professore esperto del Salento nel periodo alto-medioevale. 
            Rispondi alla seguente domanda utilizzando solo le informazioni fornite nel contesto.
            Se le informazioni nel contesto non sono sufficienti per rispondere alla domanda, dillo chiaramente.
    """

    def __init__(self):
        self.base_prompt = self.default_prompt
        self.full_prompt = self.default_prompt
        self.question = ""

    def set_prompt(self, prompt: int):
        if prompt == 1:
            self.base_prompt = self.prompt_1
        elif prompt == 2:
            self.base_prompt = self.prompt_2
        else:
            self.base_prompt = self.default_prompt

    def get_prompt(self):
        return self.base_prompt

    def query_vectorize(self, num_results: int = 5) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': VECTORIZE_API_TOKEN
        }
        data = {
            "question": self.question,
            "numResults": num_results,
            "rerank": True
        }
        try:
            response = requests.post(VECTORIZE_RETRIEVAL_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()
            response = response.json()
            chunks_text = ""
            for i, chunk in enumerate(response["documents"]):
                source_id = chunk.get("chunk_id", str(i + 1))
                similarity = chunk.get("similarity", 0)
                chunks_text += f"[source={source_id}&relevance={similarity:.2f}]\n{chunk.get('text', '').strip()}\n\n"

            self.full_prompt = self.base_prompt + f"""
                           Contesto:
                           {chunks_text}

                           Domanda: {self.question}

                           Risposta:
                           """
        except requests.exceptions.RequestException as e:
            logging.error(f"Errore nella richiesta a Vectorize: {e}")
            return {"error": str(e)}

    async def query_llm_llama(self, question: str):
        try:
            import ollama
            self.question = question
            self.query_vectorize()
            response = ollama.chat(
                model="llama3.1:8b",
                messages=[{'role': 'user', 'content': self.full_prompt}],
            )
            return response['message']['content']

        except Exception as e:
            logging.error(f"Errore nella chiamata all'LLM: {e}")
            return "Mi dispiace, si è verificato un errore nell'elaborazione della risposta."

    async def query_llm_openai(self, question: str):
        try:
            import openai
            self.question = question
            self.query_vectorize()
            openai.api_key = os.environ.get("OPENAI_API_KEY", "")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sei un assistente esperto sul salento nel periodo dell'alto-medeoevo"
                    },
                    {"role": "user", "content": self.full_prompt}
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Errore nella chiamata all'LLM: {e}")
        return "Mi dispiace, si è verificato un errore nell'elaborazione della risposta."