"""Central configuration for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT_DIR / "assets"
LOG_DIR = ROOT_DIR / "logs"


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime settings used by the UI and data layer."""

    app_name: str = "داشبورد مدیریتی تحلیل داده"
    max_file_size_mb: int = 200
    preview_rows: int = 1_000
    chart_sample_rows: int = 50_000
    allowed_extensions: tuple[str, ...] = ("csv", "xlsx", "xls")
    css_file: Path = ASSETS_DIR / "styles.css"


CONFIG = AppConfig()
