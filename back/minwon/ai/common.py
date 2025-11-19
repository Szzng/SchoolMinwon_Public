# pip install openai chromadb  numpy
import os
from openai import OpenAI
import chromadb
from chromadb.config import Settings

API_KEY = os.getenv("UPSTAGE_API_KEY", "")
MODEL_CHAT = "solar-pro2"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.upstage.ai/v1",
)


def chat(system_prompt: str, user_prompt: str, response_format=None) -> str:
    payload = {
        "model": MODEL_CHAT,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    }

    if response_format:
        payload["response_format"] = response_format

    response = client.chat.completions.create(**payload)
    return response.choices[0].message.content.strip()


def get_chroma():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chroma_path = os.path.join(current_dir, "../../chroma_db")
    chroma_path = os.path.abspath(chroma_path)

    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )
    return client.get_or_create_collection("notice_wip")
