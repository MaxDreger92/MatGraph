from matgraph.models.metadata import File
from neomodel import DateTimeProperty

def store_file(file_obj):
    """Store the uploaded file and return the file record."""
    try:
        file_name = file_obj.name
        file_record = File(
            name=file_name, date_added=DateTimeProperty(default_now=True)
        )
        file_record.file = file_obj
        file_record.save()
        return file_record
    except Exception as e:
        raise ValueError(f"File storage failed: {e}")