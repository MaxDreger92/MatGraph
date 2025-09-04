from importing.models import ImportProcess
from tasks.models import ProcessStatus
from django.utils import timezone

def create_import_process(process_id, user_id, file_id, context, callback_url):
    try:
        new_process = ImportProcess.objects.create(
            process_id=process_id,
            user_id=user_id,
            callback_url=callback_url,
            file_id=file_id,
            context=context,
            status=ProcessStatus.READY,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
    except Exception as e:
        print(f"Error occurred during process creation: {e}")
        raise
    return new_process