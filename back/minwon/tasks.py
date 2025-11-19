import logging
from django.utils import timezone
from celery import shared_task
from minwon.ai.rag.rag_minwon import get_complaint_analysis
from .models import Complaint

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_complaint_with_ai(self, complaint_id):
    """민원 생성 후 AI로부터 응답과 위험도를 한 번에 받아서 저장"""
    try:
        complaint = Complaint.objects.get(id=complaint_id)

        ai_response, ai_risk_detect = get_complaint_analysis(complaint)

        complaint.ai_response = {
            'content': ai_response,
            'generatedAt': timezone.now().isoformat()
        }

        complaint.ai_risk_detect = {
            **ai_risk_detect,
            'generatedAt': timezone.now().isoformat()
        }

        complaint.ai_response_complete()
        complaint.save()

        saved = Complaint.objects.get(id=complaint_id)

        return {
            'status': 'success',
            'complaint_id': complaint_id,
            'message': 'AI processing completed and saved'
        }

    except Complaint.DoesNotExist:
        logger.error(f"[ERROR] Complaint {complaint_id} not found")
        return {
            'status': 'error',
            'complaint_id': complaint_id,
            'message': 'Complaint not found'
        }

    except Exception as exc:
        logger.error(f"[ERROR] Failed to process complaint {complaint_id}: {str(exc)}", exc_info=True)

        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            logger.error(f"[ERROR] Max retries exceeded for complaint {complaint_id}")
            return {
                'status': 'error',
                'complaint_id': complaint_id,
                'message': f'Failed after max retries: {str(exc)}'
            }
