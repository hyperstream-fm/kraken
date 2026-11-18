from dataclasses import dataclass
import logging
from typing import Any, cast

from yt_dlp import YoutubeDL
from hyperstreamkraken.sugar.coalesce import coalesce


@dataclass(frozen=True)
class YoutubeSearch:
    url: str
    id: str


def search_on_youtube(query: str) -> YoutubeSearch:
    search_query: str = f"ytsearch1:{query}"

    yt_dlp_options: dict[str, Any] = {
        "extract_flat": True,
        "noplaylist": True,
        "quiet": True,
        "source_address": "0.0.0.0",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded"],
            }
        },
        "logger": logging.getLogger(__name__),
    }

    with YoutubeDL(yt_dlp_options) as ydl:  # pyright: ignore [reportArgumentType]
        info = ydl.extract_info(search_query, download=False)
        entries = coalesce(info.get("entries"), lambda: [])
        if not entries:
            raise RuntimeError(f"No YouTube results for '{query}'")

        video_info: dict[str, Any] = cast(dict[str, Any], entries[0])
        video_id: str | None = video_info.get("id")
        if not video_id:
            raise ValueError(f"No video ID found in YouTube search result: {video_info}")

        video_url: str = cast(
            str,
            video_info.get("webpage_url")
            or video_info.get("url")
            or f"https://youtube.com{video_id}",
        )

        return YoutubeSearch(url=video_url, id=video_id)
