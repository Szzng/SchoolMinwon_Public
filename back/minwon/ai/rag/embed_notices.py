import os
import json
import requests

from minwon.ai.common import (
    API_KEY,
    client,
    chat,
    get_chroma,

)


def call_document_parse(input_file):
    response = requests.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {API_KEY}"},
        data={"base64_encoding": "['figure']", "output_formats": "['html']", "model": "document-parse"},
        files={"document": open(input_file, "rb")}, )

    if response.status_code == 200:
        return response.json()['content']['html']
    else:
        raise ValueError(f"Unexpected status code {response.status_code}.")


def create_embedding_summary(text: str) -> str:
    system_prompt = """너는 초등학교 가정통신문 요약 전문가야.
    가정통신문 html을 보고, 벡터검색용 요약으로 만들어줘.
    정보 밀도를 높이고, 주제/대상/날짜/핵심 전달 사항 등 중요한 요소를 빠짐없이 포함해야 해.
    또한 가정통신문의 제목, 발행일, 문서번호, 대상 정보를 별도로 추출해줘.
    """.strip()

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "notice_meta",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "가정통신문의 벡터검색용 요약문",
                    },
                    "title": {
                        "type": "string",
                        "description": "가정통신문의 제목(상단 굵게 쓰인 제목).",
                    },
                    "published_at": {
                        "type": "string",
                        "description": "가정통신문 발행일. 예: '2025-11-05' 또는 '2025. 11. 5.'",
                    },
                    "notice_no": {
                        "type": "string",
                        "description": "가정통신문 문서번호 전체 문장.",
                    },
                    "target": {
                        "type": "string",
                        "description": "가정통신문의 대상 학년/학생/보호자 설명.",
                    },
                },
                "required": [
                    "summary",
                    "title",
                    "published_at",
                    "notice_no",
                    "target",
                ],
            },
        },
    }

    return chat(system_prompt, text, response_format)


def embed_passage(text: str):
    result = client.embeddings.create(
        model="embedding-passage",
        input=text,
    )
    return result.data[0].embedding


def save_to_chroma(id: str, summary: str, embedding, meta: dict):
    col = get_chroma()
    col.add(
        ids=[id],
        embeddings=[embedding],
        documents=[summary],
        metadatas=[meta],
    )


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(current_dir, "notices")

    pdf_paths = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for pdf_path in pdf_paths:
        parsed_html = call_document_parse(pdf_path)
        summarized_dict = json.loads(create_embedding_summary(parsed_html))
        summary = summarized_dict.get("summary")
        meta = {k: v for k, v in summarized_dict.items() if k != "summary"}

        emb = embed_passage(summary)
        save_to_chroma(
            id=meta["notice_no"] or os.path.basename(pdf_path),
            summary=summary,
            embedding=emb,
            meta=meta,
        )
