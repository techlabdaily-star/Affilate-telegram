from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_FILE = Path("credentials.txt")


@dataclass
class AppConfig:
    api_id: int
    api_hash: str
    phone_number: str
    string_session: str | None
    session_name: str
    db_path: str
    chats_output_file: str
    forward_media: bool
    forward_only_with_links: bool
    include_category_hint: bool


def _as_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def read_credentials_file() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if not CREDENTIALS_FILE.exists():
        return None, None, None

    lines = CREDENTIALS_FILE.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3:
        return None, None, None

    return lines[0].strip(), lines[1].strip(), lines[2].strip()


def save_credentials_file(api_id: int, api_hash: str, phone_number: str) -> None:
    CREDENTIALS_FILE.write_text(f"{api_id}\n{api_hash}\n{phone_number}\n", encoding="utf-8")


def _read_or_prompt_credentials() -> tuple[int, str, str]:
    api_id_raw = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone_number = os.getenv("TELEGRAM_PHONE_NUMBER")

    if not api_id_raw or not api_hash or not phone_number:
        file_api_id, file_api_hash, file_phone = read_credentials_file()
        api_id_raw = api_id_raw or file_api_id
        api_hash = api_hash or file_api_hash
        phone_number = phone_number or file_phone

    if not api_id_raw:
        api_id_raw = input("Enter TELEGRAM_API_ID: ").strip()
    if not api_hash:
        api_hash = input("Enter TELEGRAM_API_HASH: ").strip()
    if not phone_number:
        phone_number = input("Enter TELEGRAM_PHONE_NUMBER (with country code): ").strip()

    try:
        api_id = int(api_id_raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("TELEGRAM_API_ID must be an integer") from exc

    if not api_hash or not phone_number:
        raise RuntimeError("TELEGRAM_API_HASH and TELEGRAM_PHONE_NUMBER are required")

    return api_id, api_hash, phone_number


def load_config() -> AppConfig:
    api_id, api_hash, phone_number = _read_or_prompt_credentials()

    string_session = os.getenv("TELEGRAM_STRING_SESSION") or None
    session_name = os.getenv("TELEGRAM_SESSION_NAME", f"session_{phone_number}")
    db_path = os.getenv("DEDUPE_DB_PATH", "forwarder.db")
    chats_output_file = os.getenv("CHATS_OUTPUT_FILE", f"chats_of_{phone_number}.txt")

    return AppConfig(
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
        string_session=string_session,
        session_name=session_name,
        db_path=db_path,
        chats_output_file=chats_output_file,
        forward_media=_as_bool(os.getenv("FORWARD_MEDIA"), default=True),
        forward_only_with_links=_as_bool(os.getenv("FORWARD_ONLY_WITH_LINKS"), default=False),
        include_category_hint=_as_bool(os.getenv("INCLUDE_CATEGORY_HINT"), default=False),
    )
