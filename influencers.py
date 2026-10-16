"""Explainable scoring for YouTube creator discovery."""

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
    """Normalise available values to a relative 0–100 score."""
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
    Rank YouTube creators using content relevance and public performance.

    Content relevance:
        TF-IDF text similarity between the product query and available
        channel/video titles and descriptions.

    Performance:
        Matched-video views: 55%
        Public interactions/views: 25%
        Subscribers: 20%

    Final suitability:
        Content relevance: 70%
        Performance score: 30%

    If performance information is unavailable, suitability falls back
    to content relevance alone.

    All performance values are relative to the current search result set.
    They are not industry benchmarks or guaranteed outcome predictions.
    """
    product = _text(product)

    if not product:
        raise ValueError("Enter a product name.")

    if channels_df is None or channels_df.empty:
        return pd.DataFrame()

    results = channels_df.copy().reset_index(drop=True)

    required_text_columns = [
        "channel_name",
        "channel_id",
        "description",
        "matched_video_titles",
    ]

    for column in required_text_columns:
        if column not in results.columns:
            results[column] = ""

    # Build the text document used for relevance comparison.
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
            matching_videos = videos_df[
                videos_df["channel_id"].astype(str) == channel_id
            ]

            for _, video in matching_videos.iterrows():
                parts.append(_text(video.get("video_title")))
                parts.append(_text(video.get("video_description")))

        documents.append(" ".join(part for part in parts if part))

    # Calculate text similarity.
    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            stop_words="english",
            ngram_range=(1, 2),
        )

        matrix = vectorizer.fit_transform([product] + documents)

        relevance = (
            cosine_similarity(matrix[0:1], matrix[1:]).flatten()
            * 100
        )

    except ValueError:
        relevance = np.zeros(len(results))

    results["content_match_pct"] = np.round(relevance, 2)
    results["content_component_score"] = results["content_match_pct"]

    # Relative performance components.
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

    views_score = _normalise(views, log_scale=True)
    engagement_score = _normalise(engagement)
    subscriber_score = _normalise(subscribers, log_scale=True)

    results["performance_view_score"] = views_score.round(2)
    results["performance_engagement_score"] = engagement_score.round(2)
    results["performance_subscriber_score"] = subscriber_score.round(2)

    # Renormalise weights if some performance inputs are unavailable.
    performance_scores = []
    performance_inputs_used = []

    components = [
        (views_score, 0.55, "matched-video views"),
        (engagement_score, 0.25, "public interactions/views"),
        (subscriber_score, 0.20, "subscribers"),
    ]

    for index in results.index:
        weighted_total = 0.0
        available_weight = 0.0
        available_names = []

        for component, weight, label in components:
            value = component.loc[index]

            if pd.notna(value):
                weighted_total += float(value) * weight
                available_weight += weight
                available_names.append(label)

        if available_weight > 0:
            score = weighted_total / available_weight
        else:
            score = np.nan

        performance_scores.append(score)
        performance_inputs_used.append(
            ", ".join(available_names)
            if available_names
            else "No performance inputs available"
        )

    results["performance_score"] = np.round(
        performance_scores, 2
    )
    results["performance_inputs_used"] = performance_inputs_used

    # Final suitability score and explanation of the formula used.
    suitability_scores = []
    score_formulas = []

    for _, row in results.iterrows():
        relevance_score = float(row["content_match_pct"])
        performance_score = row["performance_score"]

        if pd.notna(performance_score):
            final_score = (
                0.70 * relevance_score
                + 0.30 * float(performance_score)
            )
            formula = "70% content match + 30% relative performance"
        else:
            final_score = relevance_score
            formula = (
                "Content match only; performance inputs unavailable"
            )

        suitability_scores.append(round(final_score, 2))
        score_formulas.append(formula)

    results["suitability_score"] = suitability_scores
    results["score_formula"] = score_formulas

    # Explain the text match without overstating what it means.
    def explain_match(row):
        score = float(row["content_match_pct"])

        if score >= 40:
            return (
                "Strong text similarity in the available search sample; "
                "review recent videos manually."
            )

        if score >= 15:
            return (
                "Some text similarity in the available search sample; "
                "verify topic and audience fit manually."
            )

        return (
            "Limited text similarity in the available search sample; "
            "review manually before shortlisting."
        )

    results["recommendation_reason"] = results.apply(
        explain_match,
        axis=1,
    )

    # Rank the creators.
    results = results.sort_values(
        ["suitability_score", "content_match_pct"],
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    results.insert(0, "rank", range(1, len(results) + 1))

    return results