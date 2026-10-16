import os

import pandas as pd
import requests
import streamlit as st


API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(Exception):
    """Readable errors from YouTube API requests."""


def get_api_key():
    """Read the API key from Streamlit secrets."""

    try:
        key = st.secrets.get("YOUTUBE_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass

    key = os.getenv("YOUTUBE_API_KEY", "").strip()

    if not key:
        raise YouTubeAPIError(
            "API key not found. Check .streamlit/secrets.toml."
        )

    return key


def api_get(endpoint, params):
    """Call a YouTube Data API endpoint."""

    request_params = dict(params)
    request_params["key"] = get_api_key()

    try:
        response = requests.get(
            f"{API_BASE}/{endpoint}",
            params=request_params,
            timeout=25,
        )
    except requests.RequestException as exc:
        raise YouTubeAPIError(
            f"Network connection failed: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise YouTubeAPIError(
            "YouTube returned an invalid response."
        ) from exc

    if not response.ok:
        error = data.get("error", {})
        message = error.get("message", "YouTube API request failed.")
        errors = error.get("errors", [])
        reason = errors[0].get("reason", "") if errors else ""

        if reason in ("quotaExceeded", "dailyLimitExceeded"):
            message = "YouTube API quota exceeded. Check Google Cloud quotas."
        elif reason in ("keyInvalid", "API_KEY_INVALID"):
            message = "Invalid API key. Check secrets.toml."
        elif reason == "accessNotConfigured":
            message = "Enable YouTube Data API v3 in Google Cloud."

        raise YouTubeAPIError(message)

    return data


def to_number(value):
    """Convert an API statistic to an integer when available."""

    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def search_youtube_influencers(product, max_results=25):
    """
    Search public YouTube videos related to a product.

    Returns:
        channels_df: channel-level data
        videos_df: matching video-level data
    """

    product = str(product).strip()

    if not product:
        raise YouTubeAPIError("Enter a product name first.")

    max_results = int(max_results)

    if not 1 <= max_results <= 50:
        raise YouTubeAPIError("Choose between 1 and 50 search results.")

    # Search YouTube videos related to the product.
    search_data = api_get(
        "search",
        {
            "part": "snippet",
            "q": product,
            "type": "video",
            "order": "relevance",
            "maxResults": max_results,
        },
    )

    search_items = search_data.get("items", [])

    if not search_items:
        return pd.DataFrame(), pd.DataFrame()

    video_ids = [
        item.get("id", {}).get("videoId")
        for item in search_items
        if item.get("id", {}).get("videoId")
    ]

    if not video_ids:
        return pd.DataFrame(), pd.DataFrame()

    # Retrieve public statistics for those videos.
    video_data = api_get(
        "videos",
        {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
        },
    )

    video_map = {
        item["id"]: item
        for item in video_data.get("items", [])
    }

    video_rows = []
    channel_ids = []

    for result in search_items:
        video_id = result.get("id", {}).get("videoId")

        if not video_id:
            continue

        detail = video_map.get(video_id, {})
        search_snippet = result.get("snippet", {})
        snippet = detail.get("snippet") or search_snippet
        stats = detail.get("statistics", {})

        channel_id = snippet.get("channelId") or search_snippet.get(
            "channelId"
        )

        if not channel_id:
            continue

        if channel_id not in channel_ids:
            channel_ids.append(channel_id)

        views = to_number(stats.get("viewCount"))
        likes = to_number(stats.get("likeCount"))
        comments = to_number(stats.get("commentCount"))

        if (
            views and views > 0
            and (likes is not None or comments is not None)
        ):
            interactions = (likes or 0) + (comments or 0)
            interaction_rate = interactions / views * 100
        else:
            interaction_rate = None

        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
        )

        video_rows.append({
            "video_id": video_id,
            "video_title": snippet.get("title", ""),
            "video_description": snippet.get("description", ""),
            "channel_id": channel_id,
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate_pct": interaction_rate,
            "thumbnail_url": thumbnail_url,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
        })

    videos_df = pd.DataFrame(video_rows)

    if not channel_ids:
        return pd.DataFrame(), videos_df

    # Retrieve statistics for discovered channels.
    channel_map = {}

    for start in range(0, len(channel_ids), 50):
        batch = channel_ids[start:start + 50]

        channel_data = api_get(
            "channels",
            {
                "part": "snippet,statistics",
                "id": ",".join(batch),
            },
        )

        for channel in channel_data.get("items", []):
            channel_map[channel["id"]] = channel

    # Summarise each channel and its matching videos.
    channel_rows = []

    for channel_id in channel_ids:
        channel = channel_map.get(channel_id, {})
        snippet = channel.get("snippet", {})
        stats = channel.get("statistics", {})

        matched = [
            row for row in video_rows
            if row["channel_id"] == channel_id
        ]

        valid_views = [
            row["views"] for row in matched
            if row["views"] is not None
        ]

        valid_interactions = [
            row for row in matched
            if row["views"] is not None
            and row["views"] > 0
            and (
                row["likes"] is not None
                or row["comments"] is not None
            )
        ]

        if valid_interactions:
            total_views = sum(
                row["views"] for row in valid_interactions
            )
            total_interactions = sum(
                (row["likes"] or 0) + (row["comments"] or 0)
                for row in valid_interactions
            )
            interaction_rate = total_interactions / total_views * 100
        else:
            interaction_rate = None

        custom_url = snippet.get("customUrl")
        channel_url = (
            f"https://www.youtube.com/{custom_url}"
            if custom_url
            else f"https://www.youtube.com/channel/{channel_id}"
        )

        channel_rows.append({
            "channel_id": channel_id,
            "channel_name": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail_url": (
                snippet.get("thumbnails", {})
                .get("medium", {})
                .get("url")
            ),
            "channel_url": channel_url,
            "subscriber_count": (
                None
                if stats.get("hiddenSubscriberCount", False)
                else to_number(stats.get("subscriberCount"))
            ),
            "total_channel_views": to_number(stats.get("viewCount")),
            "total_channel_videos": to_number(stats.get("videoCount")),
            "matched_video_count": len(matched),
            "average_matched_video_views": (
                round(sum(valid_views) / len(valid_views))
                if valid_views else None
            ),
            "public_interactions_per_view_pct": (
                round(interaction_rate, 2)
                if interaction_rate is not None else None
            ),
            "matched_video_titles": " | ".join(
                row["video_title"] for row in matched[:5]
            ),
        })

    channels_df = pd.DataFrame(channel_rows)

    if not channels_df.empty:
        channels_df = channels_df.sort_values(
            "average_matched_video_views",
            ascending=False,
            na_position="last",
        ).reset_index(drop=True)

    return channels_df, videos_df