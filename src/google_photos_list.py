#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-auth-oauthlib>=1.2.0",
#     "google-auth-httplib2>=0.2.0",
#     "requests>=2.31.0",
#     "tqdm>=4.67.1",
# ]
# ///
"""
Google Photos Lister - Lista fotos e vídeos da conta Google Photos.

Pré-requisitos:
  1. Acesse https://console.cloud.google.com/
  2. Crie um projeto e ative a "Google Photos Library API"
  3. Em "APIs & Services > Credentials", crie um OAuth 2.0 Client ID (tipo: Desktop app)
  4. Baixe o JSON e salve como 'credentials.json' na raiz do projeto
  5. Execute: uv run src/google_photos_list.py

Na primeira execução, abrirá o browser para autorizar o acesso.
O token é salvo em 'token.json' e reutilizado nas próximas execuções.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from tqdm import tqdm

SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
CREDENTIALS_FILE = Path("credentials\client_secret_278313848519-uv3nr9rnqa9lq074q1pav07ue3nho3j8.apps.googleusercontent.com.json")
TOKEN_FILE = Path("token.json")
PHOTOS_API_BASE = "https://photoslibrary.googleapis.com/v1"


def get_credentials() -> Credentials | None:
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"\n❌ Arquivo '{CREDENTIALS_FILE}' não encontrado!\n")
                print("Para configurar as credenciais:")
                print("  1. Acesse https://console.cloud.google.com/")
                print("  2. Crie um projeto e ative a 'Google Photos Library API'")
                print("  3. Em APIs & Services > Credentials, crie um OAuth 2.0 Client ID (Desktop app)")
                print(f"  4. Baixe o JSON e salve como '{CREDENTIALS_FILE}' na raiz do projeto")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds


def list_media_items(creds: Credentials) -> list[dict]:
    headers = {"Authorization": f"Bearer {creds.token}"}
    all_items: list[dict] = []
    page_token: str | None = None

    print("\nBuscando itens do Google Photos...")

    with tqdm(desc="Páginas", unit=" pág") as pbar:
        while True:
            params: dict = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(f"{PHOTOS_API_BASE}/mediaItems", headers=headers, params=params, timeout=30)

            if response.status_code == 401:
                creds.refresh(Request())
                headers["Authorization"] = f"Bearer {creds.token}"
                continue

            response.raise_for_status()
            data = response.json()

            items = data.get("mediaItems", [])
            all_items.extend(items)
            pbar.update(1)
            pbar.set_postfix({"total": len(all_items)})

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    return all_items


def save_csv(items: list[dict], path: Path) -> None:
    fieldnames = [
        "filename",
        "type",
        "mime_type",
        "creation_time",
        "width",
        "height",
        "duration_seconds",
        "camera_make",
        "camera_model",
        "id",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            meta = item.get("mediaMetadata", {})
            photo = meta.get("photo", {})
            video = meta.get("video", {})
            mime = item.get("mimeType", "")

            media_type = "VIDEO" if "video" in mime else "PHOTO" if "image" in mime else "OTHER"

            duration_raw = video.get("videoDuration", "")
            duration_sec = ""
            if duration_raw:
                duration_sec = duration_raw.rstrip("s")

            writer.writerow(
                {
                    "filename": item.get("filename", ""),
                    "type": media_type,
                    "mime_type": mime,
                    "creation_time": meta.get("creationTime", ""),
                    "width": meta.get("width", ""),
                    "height": meta.get("height", ""),
                    "duration_seconds": duration_sec,
                    "camera_make": photo.get("cameraMake") or video.get("cameraMake", ""),
                    "camera_model": photo.get("cameraModel") or video.get("cameraModel", ""),
                    "id": item.get("id", ""),
                }
            )


def print_summary(items: list[dict]) -> None:
    photos = sum(1 for i in items if "image" in i.get("mimeType", ""))
    videos = sum(1 for i in items if "video" in i.get("mimeType", ""))
    other = len(items) - photos - videos

    print(f"\nResumo:")
    print(f"  Total : {len(items)}")
    print(f"  Fotos : {photos}")
    print(f"  Videos: {videos}")
    if other:
        print(f"  Outros: {other}")


def main() -> None:
    print("Google Photos Lister")
    print("=" * 40)

    creds = get_credentials()
    if not creds:
        return

    items = list_media_items(creds)
    print_summary(items)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = Path(f"google_photos_{stamp}.csv")
    json_path = Path(f"google_photos_{stamp}.json")

    save_csv(items, csv_path)
    json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nArquivos gerados:")
    print(f"  {csv_path}  (planilha)")
    print(f"  {json_path} (dados completos)")


if __name__ == "__main__":
    main()
