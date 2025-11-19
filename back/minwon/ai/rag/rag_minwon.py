import json
from minwon.ai.common import chat, client, get_chroma


def embed_query(text: str):
    result = client.embeddings.create(
        model="embedding-query",
        input=text,
    )
    return result.data[0].embedding


def search_in_chroma(query: str, k: int = 3, max_distance: float | None = None):
    col = get_chroma()
    q_emb = embed_query(query)

    result = col.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas", "distances"],  # ★ 점수 포함해서 받기
    )

    ids = result["ids"][0]
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    dists = result["distances"][0]  # 코사인 거리(기본 설정일 때)

    items = []
    for i, d, m, dist in zip(ids, docs, metas, dists):
        if max_distance is not None and dist > max_distance:
            continue

        items.append(
            {
                "id": i,
                "summary": d,
                "meta": m,
                "distance": dist,  # 디버깅/튜닝용으로 같이 넣어두면 좋음
            }
        )

    return items


common_rag_system_prompt = """
너는 초등학교의 '학교 민원 처리 AI 챗봇'이다.

[운영 원칙]
- 모든 민원은 1단계에서 AI 챗봇(너)이 응답한다.
- 명확히 답변할 수 없거나 추가 확인이 필요하거나 민원인이 요청할 경우 [2단계] 교무실로 이관한다.
- 교사는 어떤 경우에도 민원인에게 직접 노출되지 않는다. 모든 응대는 AI 챗봇 또는 교무실을 통해 이루어진다.
- 답변은 공공기관의 공식 문체로 정중하고 신뢰감 있게 작성한다.
- 항상 사실 기반의 중립적 태도를 유지하며, 감정적·추측적·단정적 표현을 사용하지 않는다.
- 불확실하거나 규정이 학교별로 다를 수 있는 경우, “정확한 안내를 위해 교무실 확인이 필요하다”고 안내한다.

[교사 표현 필터 규칙]
- 교사를 민원 대응 주체로 언급하지 않는다.
- 교사 관련 내용은 내부 절차 협조자로만 언급한다.
- ‘면담’, ‘연락’, ‘설명’, ‘안내’ 등의 행위 주체는 항상 교무실 또는 학교 행정 절차로 제한한다.
- 교사 실명·직함은 포함하지 않는다.

[연락 안내 제한 규칙]
- “교무실로 연락 주시면”, “전화드리겠습니다”, “02-XXX-XXXX로 문의 주세요” 등 
  연락·문의 안내 문구는 생성하지 않는다.
- 이 시스템은 자동 이관 구조이므로, 
  학부모가 별도로 교무실에 연락할 필요가 있다는 안내는 하지 않는다.
- 대신 “교무실에서 확인 후 절차에 따라 안내 예정입니다.” 등의 문장으로 마무리한다.

[응답 구성 및 형식]
- 답변은 2~4개의 짧은 문단으로 구성하고 문단 사이에 한 줄 공백을 둔다.
- 첫 문단은 민원 내용을 요약하는 내용으로 시작한다.
- 중간 문단은 관련 절차나 근거를 제시하고, 교무실 중심의 처리 과정을 설명한다.
- 마지막 문단은 후속 조치 계획이나 안내 방식을 요약한다.
- 필요 시 번호 목록을 사용하되, 문장 간 간격을 유지한다.

[교무실 참고용 요약(notes_for_staff)]
- 민원 요지: 핵심 불만 또는 요청
- 감정/위험: 학부모 정서 및 위협 수준
- 카테고리: ATTENDANCE/MEAL/.../ETC
- 조치 제안: 담당 부서·확인 포인트·예상 리스크
- 주의점: 민감 표현·법적 위험·대응 톤

출력은 반드시 상위 시스템에서 지정한 JSON 스키마를 준수해야 하며, 불필요한 자연어 설명은 포함하지 않는다.
""".strip()


def rag_get_prompt_with_context(summary, question):
    system_prompt = (
            common_rag_system_prompt
            + "\n\n[참고 지침]\n- 제공된 가정통신문 요약을 우선 근거로 삼되, 범위를 넘는 단정은 피한다.\n"
              "- 필요 시 교무실 확인 절차를 명시한다."
    )
    user_prompt = f"""
                    학부모 질문:
                    {question}
                    
                    사용 가능한 가정통신문 요약:
                    {summary}
                    """.strip()
    return system_prompt, user_prompt


def rag_get_prompt_without_context(question):
    system_prompt = (
            common_rag_system_prompt
            + "\n\n[참고 지침]\n- 관련 가정통신문이 없으므로, 일반적인 학교 운영 절차를 근거로 보수적으로 안내하라.\n"
              "- 불확실하거나 학교별로 상이할 수 있는 내용은 교무실 확인을 안내한다."
    )
    user_prompt = f"""
                    학부모 질문:
                    {question}
                    
                    관련된 가정통신문 요약 정보는 현재 없다.
                    """.strip()
    return system_prompt, user_prompt


RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "complaint_analysis_result",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "학부모에게 전달할 정중하고 중립적인 답변"
                },
                "sentiment": {
                    "type": "string",
                    "enum": ["very_negative", "negative", "neutral", "positive"]
                },
                "toxicity_score": {"type": "number"},
                "reasons": {"type": "array", "items": {"type": "string"}},
                "category": {
                    "type": "string",
                    "enum": ["ATTENDANCE", "MEAL", "AFTER_SCHOOL", "SAFETY",
                             "FACILITY", "ACADEMIC", "ADMIN", "COMMUNICATION", "SYSTEM", "ETC"]
                },
                "needs_human_review": {"type": "boolean"},
                "notes_for_staff": {"type": "string"}
            },
            "required": ["response", "sentiment", "toxicity_score",
                         "reasons", "category", "needs_human_review", "notes_for_staff"]
        }
    }
}


def get_complaint_analysis(complaint):
    category = (complaint.categories[0].upper() if complaint.categories else "ETC")
    allowed = {"ATTENDANCE", "MEAL", "AFTER_SCHOOL", "SAFETY", "FACILITY",
               "ACADEMIC", "ADMIN", "COMMUNICATION", "SYSTEM", "ETC"}
    if category not in allowed:
        category = "ETC"

    query = f"카테고리 : {category}\n제목 : {complaint.title}\n내용 : {complaint.content}"

    # RAG 검색
    results = search_in_chroma(query, k=3, max_distance=1.2)
    has_context = bool(results)
    context_summary = results[0]["summary"] if has_context else None
    context_meta = results[0]["meta"] if has_context else None

    if has_context:
        system_prompt, user_prompt = rag_get_prompt_with_context(context_summary, query)
    else:
        system_prompt, user_prompt = rag_get_prompt_without_context(query)

    # 모델 호출
    result_str = chat(system_prompt, user_prompt, RESPONSE_FORMAT)
    result = json.loads(result_str)

    ai_response = result.pop("response")
    risk_detect = result

    # 휴리스틱 기반 위험 감지 (보조)
    danger_signals = [
        "폭력", "학대", "자살", "자해", "실종", "협박", "고소", "고발", "언론", "녹음",
        "명예훼손", "유출", "소송", "법적", "변호사", "금품", "청탁"
    ]
    text = f"{complaint.title} {complaint.content}"
    if any(keyword in text for keyword in danger_signals):
        risk_detect["needs_human_review"] = True
        if "SAFETY" in (complaint.categories or []):
            risk_detect["category"] = "SAFETY"

    # 가정통신문 출처 표기
    if has_context and context_meta:
        info = "\n".join(
            f"{k}: {v}"
            for k, v in {
                "제목": context_meta.get("title"),
                "발행일": context_meta.get("published_at"),
                "문서번호": context_meta.get("notice_no"),
                "대상": context_meta.get("target"),
                "파일명": context_meta.get("filename"),
            }.items() if v
        )
        if info:
            ai_response += f"\n\n[참고한 가정통신문 정보]\n{info}"

    return ai_response, risk_detect
