from typing import Optional
from pathlib import Path
import os
import datetime
import platform

__all__ = ["get_file_creation_time", "get_file_age_in_days", "get_last_modified_time"]


def get_file_creation_time(path_to_file: Path) -> Optional[datetime.datetime]:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """

    if not path_to_file.is_file():
        return None

    if platform.system() == "Windows":
        return datetime.datetime.fromtimestamp(os.path.getctime(path_to_file))
    stat = os.stat(path_to_file)
    try:
        return datetime.datetime.fromtimestamp(stat.st_birthtime)
    except AttributeError:
        # Linux -> using last modified.
        return datetime.datetime.fromtimestamp(stat.st_mtime)


def get_file_age_in_days(path_to_file: Path) -> Optional[int]:
    if not path_to_file.is_file():
        return None
    creation_time = get_file_creation_time(path_to_file)
    if creation_time is None:
        return None
    today = datetime.datetime.now().date()
    return (today - creation_time.date()).days


def get_last_modified_time(path_to_file_or_dir: Path) -> Optional[datetime.datetime]:
    if not (path_to_file_or_dir.is_file() or path_to_file_or_dir.is_dir()):
        return None
    stat = os.stat(path_to_file_or_dir)
    return datetime.datetime.fromtimestamp(stat.st_mtime)
