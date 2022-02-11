from typing import Optional, Any
from pathlib import Path
import os
import datetime
import platform
import pickle

__all__ = [
    "get_file_creation_time",
    "get_file_age_in_days",
    "get_last_modified_time",
    "match_search_str_in_dir",
    "save_structure",
    "load_structure",
]


def match_search_str_in_dir(search_str: str, dir: Path) -> Path:
    matching_files = [f for f in os.listdir(dir) if (dir / f).is_file() and search_str in f]
    if len(matching_files) > 1:
        raise ValueError(f"More than one match found for search string {search_str}.")
    if not matching_files:
        raise ValueError(f"No matches found for search string {search_str} (looking in {dir}).")

    return matching_files[0]


def save_structure(obj: Any, name: str, path: Path, overwrite: bool = True) -> None:
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{name}.pickle"

    if file_path.is_file() and not overwrite:
        print(f"Not saving {file_path}!")
        return
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

    print(f"{file_path} saved.")


def load_structure(name: str, path: Path) -> None:
    with open(path / match_search_str_in_dir(name, path), "rb") as f:
        return pickle.load(f)


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
