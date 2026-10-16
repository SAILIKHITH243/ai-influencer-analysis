
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _text(value):
    """Convert missing values safely to text."""
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def _normalise(values, log_scale=False):
    """Scale available values from 0 to 100."""
    values = pd.to_numeric(values, errors="coerce")
    values = values.where(values >= 0)

    if log_scale:
        values = np.log1p(values)

    scores = pd.Series(np.nan, index=values.index, dtype=float)
    valid = values.dropna()

    if valid.empty:
        return scores

    minimum = valid.min()
    maximum = valid.max()

    if maximum == minimum:
        scores.loc[valid.index] = 50.0
    else:
        scores.loc[valid.index] = (
            (valid - minimum) / (maximum - minimum) * 100
        )

    return scores


def rank_influencers(product, channels_df, videos_df=None):
    """
    Rank YouTube channels by content relevance and available
    public performance indicators.

    Returns a DataFrame with content_match_pct,
    performance_score and suitability_score.
    """

    product = _text(product)

    if not product:
        raise ValueError("Enter a product name.")

    if channels_df is None or channels_df.empty:
        return pd.DataFrame()

    results = channels_df.copy().reset_index(drop=True)

    # Ensure required text columns exist.
    text_columns = [
        "channel_name",
        "channel_id",
        "description",
        "matched_video_titles",
    ]

    for column in text_columns:
        if column not in results.columns:
            results[column] = ""

    # Build a text document for each channel.
    documents = []

    for _, channel in results.iterrows():
        parts = [
            _text(channel.get("channel_name")),
            _text(channel.get("description")),
            _text(channel.get("matched_video_titles")),
        ]

        channel_id = _text(channel.get("channel_id"))

        if (
            videos_df is not None
            and not videos_df.empty
            and "channel_id" in videos_df.columns
        ):
            matched_videos = videos_df[
                videos_df["channel_id"].astype(str) == channel_id
            ]

            for _, video in matched_videos.iterrows():
                parts.append(_text(video.get("video_title")))
                parts.append(_text(video.get("video_description")))

        documents.append(" ".join(part for part in parts if part))

    # TF-IDF calculates text similarity; it is not a trained
    # prediction model.
    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            stop_words="english",
            ngram_range=(1, 2),
        )

        matrix = vectorizer.fit_transform([product] + documents)

        relevance = cosine_similarity(
            matrix[0:1],
            matrix[1:],
        ).flatten() * 100

    except ValueError:
        relevance = np.zeros(len(results))

    results["content_match_pct"] = np.round(relevance, 2)

    # Retrieve available performance indicators.
    views = results.get(
        "average_matched_video_views",
        pd.Series(np.nan, index=results.index),
    )

    subscribers = results.get(
        "subscriber_count",
        pd.Series(np.nan, index=results.index),
    )

    engagement = results.get(
        "public_interactions_per_view_pct",
        pd.Series(np.nan, index=results.index),
    )

    # Normalize each metric within this search result set.
    performance_components = [
        (_normalise(views, log_scale=True), 0.55),
        (_normalise(engagement), 0.25),
        (_normalise(subscribers, log_scale=True), 0.20),
    ]

    performance_scores = []

    for index in results.index:
        weighted_total = 0.0
        available_weight = 0.0

        for component, weight in performance_components:
            value = component.loc[index]

            if pd.notna(value):
                weighted_total += float(value) * weight
                available_weight += weight

        if available_weight:
            performance_scores.append(
                weighted_total / available_weight
            )
        else:
            performance_scores.append(np.nan)

    results["performance_score"] = np.round(
        performance_scores, 2
    )

    # Final score: 70% content relevance + 30% performance,
    # or relevance alone if performance data is unavailable.
    suitability_scores = []

    for _, row in results.iterrows():
        relevance_score = float(row["content_match_pct"])
        performance_score = row["performance_score"]

        if pd.notna(performance_score):
            final_score = (
                0.70 * relevance_score
                + 0.30 * float(performance_score)
            )
        else:
            final_score = relevance_score

        suitability_scores.append(round(final_score, 2))

    results["suitability_score"] = suitability_scores

    def explain_match(row):
        relevance_score = row["content_match_pct"]

        if relevance_score >= 40:
            return "Strong text similarity; review the videos."
        elif relevance_score >= 15:
            return "Some relevant content; verify product fit."
        else:
            return "Limited text similarity; check manually."

    results["recommendation_reason"] = results.apply(
        explain_match,
        axis=1,
    )

    # Rank creators within the current search results.
    results = results.sort_values(
        ["suitability_score", "content_match_pct"],
        ascending=False,
    ).reset_index(drop=True)

    results.insert(0, "rank", range(1, len(results) + 1))

    return results
