from matching.models import ExtractProcess
from tasks.models import ProcessStatus
from django.utils import timezone

def create_extract_process(process_id, user_id, graph):
    try:
        new_process = ExtractProcess.objects.create(
            process_id=process_id,
            user_id=user_id,
            graph=graph,
            status=ProcessStatus.READY,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
    except Exception as e:
        print(f"Error occurred during process creation: {e}")
        raise
    return new_process