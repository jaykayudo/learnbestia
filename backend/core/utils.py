import random
from typing import Any

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import slugify
from django.utils import timezone
from rest_framework import pagination
from rest_framework.response import Response


class CorePagination(pagination.PageNumberPagination):
    page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.page.next_page_number() if self.page.has_next() else None,
                "previous": (
                    self.page.previous_page_number()
                    if self.page.has_previous()
                    else None
                ),
                "count": self.page.paginator.count,
                "data": data,
            }
        )


class MessagePagination(CorePagination):
    page_size = 200


FILE_EXTENSIONS = {
    "video": ["mp4", "webm", "mkv"],
    "audio": ["mp3", "ogg", "wav"],
    "book": ["pdf", "epub"],
}


def chat_upload_path(instance, filename):
    # get the chat message
    pass


def append_chunk_to_file(file_path: str, chunk: bytes) -> dict[str, Any]:
    with open(file_path, "ab+") as file:
        file.write(chunk)
        pointer_size = len(file.read())

    return {"pointer_size": pointer_size}


def file_upload_logic(
    file: SimpleUploadedFile,
    file_path: str,
    type="VID",
    extension: str = ".jpg",
):
    """
    data
        - file: simple_uploaded_file
        - file_path?
    """
    if not file_path:
        random_string = str(random.randint(100000, 99999))
        time_stamp = timezone.now().strftime("%Y-%m-%d-%H-%M-%S")
        new_path = (
            settings.MEDIA_ROOT
            / f"temp/{type}_{time_stamp}_{random_string}.{extension}"
        )
        with open(new_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)
            pointer_size = file.size
        return {"path": new_path, "pointer_size": pointer_size}
    else:
        if not default_storage.exists(file_path):
            raise FileExistsError
        with open(file_path, "ab+") as f:
            f.write(chunk)
            pointer_size = file.size
        return {"path": file_path, "pointer_size": pointer_size}


def cleanup_temp_media_files():
    temp_path = settings.MEDIA_ROOT / "temp/"
    all_files = default_storage.listdir(temp_path)[1]

    deleted = 0
    for file in all_files:
        file_split_list = file.split("_")
        if len(file_split_list) == 3:
            date_string = file_split_list[1]
            date_time = timezone.datetime.strptime(date_string, "%Y-%m-%d-%H-%M-%S")
            if date_time + timezone.timedelta(hours=1) < timezone.now():
                default_storage.delete(temp_path / file)
                deleted += 1


# remove latter
def move_course_file(instance, file_path, type="video"):
    if not default_storage.exists(file_path):
        raise FileExistsError
    if type not in FILE_EXTENSIONS:
        raise TypeError(f"Invalid Type - {type}")
    ext = file_path.split(".")[-1]
    if ext not in FILE_EXTENSIONS[type]:
        raise TypeError("Invalid extension for file extension for type %s" % type)
    file = default_storage.open(file_path)

    new_file_name = f"{slugify(instance.title)}-{instance.id}.{ext}"
    instance.file = File(file.read(), new_file_name)
    instance.save()
    # delete duplicate
    default_storage.delete(file_path)


def get_course_channel_name(id: str):
    return "course_%s" % id
