import json

from minwon.ai.common import chat


def review_complaint_reply(complaint_text: str, reply_text: str) -> str:
    system_prompt = """
    너는 '초등학교 민원 처리 시스템'에서 사용하는 AI 답변 검토 모델이다.

    역할:
    1) 교무실/학교가 작성한 민원 답변 문안을 검토한다.
    2) 표현 수위가 적절한지, 불필요하게 방어적이거나 공격적인 부분은 없는지 확인한다.
    3) 법적·정책적 리스크가 있어 보이는 표현(책임 인정, 약속 남발, 개인정보 노출 등)을 지적한다.
    4) 민원인의 질문에 핵심적으로 답하고 있는지, 빠진 부분은 없는지 점검한다.
    5) 교사가 존중받을 수 있도록 하되, 민원인에게는 정중하고 신뢰감을 주는 답변이 되도록 돕는다.
    6) 결과는 반드시 JSON 형식으로만 출력한다.

    주의사항:
    - 감정적으로 보일 수 있는 표현(짜증, 비꼼, 책임 회피처럼 보이는 문장)을 특히 주의해서 살펴본다.
    - 학교 정책이나 규정을 설명할 때는, 너무 단호하게 '안 됩니다'라고만 쓰기보다, 이유와 대안을 함께 안내하는 것을 권장한다.
    - 필요하다면 답변 문안을 더 부드럽고 명확하게 다듬은 'suggested_reply'를 제안한다.
    - 확실하지 않은 부분은 "uncertain"이라고 표기하고, 사람 검토가 필요하다고 표시한다.
    """.strip()

    # complaint_text + reply_text를 하나의 user 메시지로 합쳐서 보냄
    user_content = f"""
    [민원 원문]
    {complaint_text}

    [교사가 작성한 답변 문안]
    {reply_text}
    """.strip()

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "complaint_reply_review_result",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "is_appropriate": {
                        "type": "boolean",
                        "description": "전체적으로 민원인에게 보내도 될 만큼 적절한 답변인지 여부"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "법적·정책적·감정적 리스크 수준",
                        "enum": ["LOW", "MEDIUM", "HIGH"]
                    },
                    "tone": {
                        "type": "string",
                        "description": "답변의 어조 평가",
                        "enum": ["too_harsh", "appropriate", "too_soft", "unclear"]
                    },
                    "missing_points": {
                        "type": "array",
                        "description": "민원인이 제기했지만 답변에서 충분히 다루지 못한 쟁점 목록",
                        "items": {"type": "string"}
                    },
                    "warnings": {
                        "type": "array",
                        "description": "위험하거나 오해를 부를 수 있는 표현 및 그 이유",
                        "items": {"type": "string"}
                    },
                    "suggested_improvements": {
                        "type": "array",
                        "description": "답변을 개선하기 위한 구체적인 수정/보완 제안",
                        "items": {"type": "string"}
                    },
                    "needs_human_review": {
                        "type": "boolean",
                        "description": "관리자(교감/교장/행정실 등) 추가 검토가 필요한지 여부"
                    },
                    "summary_for_staff": {
                        "type": "string",
                        "description": "교사가 참고하기 위한 전체적인 평가 요약 (교내 공유용)"
                    },
                    "suggested_reply": {
                        "type": "string",
                        "description": "수정/보완을 반영하여 AI가 제안하는 답변 문안 전체 (없으면 원문을 기반으로 약간 수정한 버전이라도 제안)"
                    }
                },
                "required": [
                    "is_appropriate",
                    "risk_level",
                    "tone",
                    "missing_points",
                    "warnings",
                    "suggested_improvements",
                    "needs_human_review",
                    "summary_for_staff",
                    "suggested_reply"
                ]
            }
        }
    }

    return chat(system_prompt, user_content, response_format)


def review_staff_response(complaint, comment):
    """
    교무실의 댓글/답변을 AI가 검토하고 피드백을 JSON 형식으로 반환

    Args:
        complaint: Complaint 객체
        comment: Comment 객체 (교무실 댓글)

    Returns:
        str: AI 리뷰 내용 (JSON 형식)
    """
    complaint_text = f"""
    카테고리: {', '.join(complaint.categories) if complaint.categories else '미분류'}
    제목: {complaint.title}

    내용:
    {complaint.content}
    """.strip()

    reply_text = comment.content

    # AI 리뷰 생성
    review_json_str = review_complaint_reply(complaint_text, reply_text)

    # JSON 파싱 및 포맷팅
    try:
        review_data = json.loads(review_json_str)

        # 사람이 읽을 수 있는 형식으로 포맷팅
        formatted_review = f"""
🤖 AI 리뷰 결과:

【적절성】
{review_data.get('is_appropriate', 'N/A')} - {"전송 가능한 수준" if review_data.get('is_appropriate') else "수정 권장"}

【위험도】
{review_data.get('risk_level', 'N/A')} - {"낮음" if review_data.get('risk_level') == 'LOW' else "중간" if review_data.get('risk_level') == 'MEDIUM' else "높음"}

【톤앤매너】
{review_data.get('tone', 'N/A')}

【누락된 쟁점】
{chr(10).join('• ' + item for item in review_data.get('missing_points', [])) if review_data.get('missing_points') else '없음'}

【주의사항】
{chr(10).join('⚠️ ' + item for item in review_data.get('warnings', [])) if review_data.get('warnings') else '없음'}

【개선 제안】
{chr(10).join('✓ ' + item for item in review_data.get('suggested_improvements', [])) if review_data.get('suggested_improvements') else '없음'}

【담당자 요약】
{review_data.get('summary_for_staff', 'N/A')}

【제안 수정안】
{review_data.get('suggested_reply', 'N/A')}

【추가 검토 필요】
{review_data.get('needs_human_review', False)}
        """.strip()

        return formatted_review

    except json.JSONDecodeError as e:
        return f"AI 리뷰 결과:\n{review_json_str}"
