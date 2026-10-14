"""Secure and memory-aware file loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

from dashboard.config import CONFIG
from dashboard.exceptions import FileValidationError


def validate_upload(file: BinaryIO, filename: str, size: int | None = None) -> str:
    """Validate uploaded file metadata before parsing.

    Args:
        file: Uploaded file object.
        filename: Original uploaded filename.
        size: Optional file size in bytes.

    Returns:
        Lowercase file extension without leading dot.

    Raises:
        FileValidationError: If extension or size is invalid.
    """

    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in CONFIG.allowed_extensions:
        allowed = "، ".join(CONFIG.allowed_extensions)
        raise FileValidationError(f"فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: {allowed}")

    file.seek(0, 2)
    actual_size = file.tell()
    file.seek(0)
    effective_size = max(actual_size, size or 0)
    if effective_size > CONFIG.max_file_size_mb * 1024 * 1024:
        raise FileValidationError(
            f"حجم فایل نباید بیشتر از {CONFIG.max_file_size_mb} مگابایت باشد."
        )

    return extension


def load_dataframe(file: BinaryIO, filename: str, size: int | None = None) -> pd.DataFrame:
    """Load CSV or Excel content into a pandas DataFrame.

    The function keeps parsing strict and normalizes empty column names so the UI
    can safely address every column.
    """

    extension = validate_upload(file=file, filename=filename, size=size)
    if file.read(1) == b"":
        raise FileValidationError("فایل خالی است.")
    file.seek(0)

    try:
        if extension == "csv":
            dataframe = pd.read_csv(file, encoding="utf-8-sig")
        else:
            engine = "xlrd" if extension == "xls" else "openpyxl"
            dataframe = pd.read_excel(file, engine=engine)
    except UnicodeDecodeError as exc:
        file.seek(0)
        try:
            dataframe = pd.read_csv(file, encoding="cp1256")
        except Exception as fallback_exc:
            raise FileValidationError("کدگذاری فایل CSV قابل خواندن نیست.") from fallback_exc
    except Exception as exc:
        raise FileValidationError("فایل قابل خواندن نیست یا ساختار معتبری ندارد.") from exc

    if dataframe.empty:
        raise FileValidationError("فایل داده‌ای برای نمایش ندارد.")

    dataframe.columns = _normalize_columns(dataframe.columns)
    return dataframe.convert_dtypes()


def _normalize_columns(columns: pd.Index) -> list[str]:
    """Return unique, display-safe column names."""

    normalized: list[str] = []
    used: set[str] = set()
    next_suffix: dict[str, int] = {}
    for index, column in enumerate(columns, start=1):
        name = str(column).strip() if str(column).strip() else f"ستون {index}"
        candidate = name
        suffix = next_suffix.get(name, 2)
        while candidate in used:
            candidate = f"{name}_{suffix}"
            suffix += 1
        next_suffix[name] = suffix
        used.add(candidate)
        normalized.append(candidate)
    return normalized
