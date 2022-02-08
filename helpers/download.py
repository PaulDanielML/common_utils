from typing import Dict
import asyncio
import httpx
from pathlib import Path

import pandas as pd
from loguru import logger
from PIL import Image, UnidentifiedImageError

__all__ = ["download_images_from_df"]


async def download_images_from_df(
    df: pd.DataFrame,
    download_dir: Path,
    url_column_name: str = "url",
    file_column_name: str = "image_file",
    semaphore_counter: int = 50,
) -> pd.DataFrame:
    """
    Method for asynchronous download of all images specified in a pandas Dataframe.
    """

    _df = df.copy(deep=True)
    coroutines = [
        cor_download_single(
            r,
            download_dir,
            url_column_name,
            file_column_name,
        )
        for _, r in _df.iterrows()
    ]
    sem = asyncio.Semaphore(semaphore_counter)

    async def _sem_wrap(coro):
        async with sem:
            return await coro

    results = await asyncio.gather(*[_sem_wrap(c) for c in coroutines])
    return pd.DataFrame(results)


async def cor_download_single(
    row: pd.Series,
    download_dir: Path,
    url_column_name: str = "url",
    file_column_name: str = "image_file",
) -> Dict:
    row["downloaded"] = False
    row["correct_tag"] = True

    accommodation_code = (
        row["accommodation_code"] if "accommodation_code" in row else "Unknown"
    )
    file_name = row[file_column_name]

    # simple way to retry failed downloads
    for i in range(3):
        if row["downloaded"]:
            break
        if i > 0:
            logger.info(f"{accommodation_code}: Download round {i+1}")

        _pth = download_dir.joinpath(file_name)
        if _pth.is_file():
            row["downloaded"] = True
            return row.to_dict()
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(row[url_column_name], timeout=2)
                with open(_pth, "wb") as f:
                    f.write(r.content)
            row["downloaded"] = True
        except httpx.RequestError:
            logger.info(f"{accommodation_code}, {file_name}: Request Error")
            await asyncio.sleep(0.3)
            continue
        except TypeError:
            logger.info(f"Found invalid url type: {row[url_column_name]}")
            return row.to_dict()

        # verify correct download
        try:
            Image.open(_pth).verify()
        except UnidentifiedImageError:
            row["downloaded"] = False
            _pth.unlink()
            logger.info(f"Bad downloaded imgage found and deleted.")
    return row.to_dict()
