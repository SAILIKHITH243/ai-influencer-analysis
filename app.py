import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from youtube_api import search_youtube_influencers, YouTubeAPIError
from influencers import rank_influencers

from database import (
    DB_PATH,
    initialize_database,
    save_channel_snapshot,
    get_channel_history,
    get_latest_channel_snapshots,
    get_tracking_summary,
    save_creator_to_shortlist,
    remove_creator_from_shortlist,
    get_saved_creators,
    get_shortlist_campaigns,
)

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Creator Intelligence Pro",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Discover Influencers",
    "Compare Creators",
    "Saved Shortlist",
    "Creator Profile",
    "Video Performance",
    "Dashboard Overview",
]

# ============================================================
# APPLE-INSPIRED DARK UI
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --primary-color:#8B5CF6; --background-color:#0B1020; --secondary-background-color:#151C30; --text-color:#F3F6FC; }
    html, body, [class*="css"] { font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    .stApp,[data-testid="stAppViewContainer"] { background:#0B1020 !important; color:#F3F6FC !important; }
    .stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,.stApp [data-testid="stMarkdownContainer"] { color:#E7ECF7; }
    [data-testid="stHeader"] { background:rgba(11,16,32,.95) !important; border-bottom:1px solid #27314A; }
    [data-testid="stToolbar"] { color:#E7ECF7 !important; }
    .block-container { max-width:1500px; padding-top:1.4rem; padding-bottom:3rem; }
    section[data-testid="stSidebar"] { background:#0E1426 !important; border-right:1px solid #27314A; }
    section[data-testid="stSidebar"] * { color:#DCE4F4; }
    .brand-mark { color:#22D3EE !important; font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }
    .hero { background:radial-gradient(circle at 88% 18%,rgba(34,211,238,.12),transparent 24%),radial-gradient(circle at 72% 85%,rgba(139,92,246,.15),transparent 30%),linear-gradient(125deg,#151C30 0%,#11182B 58%,#1A1733 100%); border:1px solid #2B3652; border-radius:24px; padding:30px; margin-bottom:24px; box-shadow:0 18px 48px rgba(0,0,0,.18); }
    .eyebrow { color:#22D3EE !important; font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px; }
    .hero h1 { font-size:clamp(30px,4vw,44px); font-weight:800; color:#F8FAFF !important; letter-spacing:-1.4px; line-height:1.12; margin:0 0 12px; }
    .hero p { font-size:15px; color:#AEB9D0 !important; line-height:1.7; max-width:800px; margin:0; }
    .section-heading { font-size:23px; font-weight:750; color:#F4F7FD !important; margin:12px 0 5px; }
    .muted { color:#A7B3C9 !important; font-size:13px; }
    div[data-testid="stMetric"] { background:#151C30 !important; border:1px solid #2A3551 !important; border-radius:16px; padding:16px; box-shadow:0 8px 24px rgba(0,0,0,.10); }
    div[data-testid="stMetricLabel"],div[data-testid="stMetricLabel"] * { color:#AAB6CE !important; font-size:12px; }
    div[data-testid="stMetricValue"],div[data-testid="stMetricValue"] * { color:#F8FAFF !important; font-size:24px; font-weight:750; }
    div[data-testid="stMetricDelta"] { color:#B4C0D5 !important; }
    div[data-testid="stButton"]>button,div[data-testid="stLinkButton"]>a,div[data-testid="stDownloadButton"]>button,div[data-testid="stFormSubmitButton"]>button { border-radius:11px !important; font-weight:650 !important; min-height:42px; border:1px solid #303C59 !important; background:#1A2238 !important; color:#F3F6FC !important; transition:all .16s ease; }
    div[data-testid="stButton"]>button *,div[data-testid="stLinkButton"]>a *,div[data-testid="stDownloadButton"]>button *,div[data-testid="stFormSubmitButton"]>button * { color:inherit !important; }
    div[data-testid="stButton"]>button[kind="primary"],div[data-testid="stButton"]>button[data-testid="stBaseButton-primary"],div[data-testid="stFormSubmitButton"]>button[kind="primary"] { background:#7657E8 !important; color:#FFFFFF !important; border-color:#7657E8 !important; box-shadow:0 5px 18px rgba(118,87,232,.18); }
    div[data-testid="stButton"]>button[kind="primary"] *,div[data-testid="stButton"]>button[data-testid="stBaseButton-primary"] *,div[data-testid="stFormSubmitButton"]>button[kind="primary"] * { color:#FFFFFF !important; }
    div[data-testid="stButton"]>button:hover,div[data-testid="stLinkButton"]>a:hover,div[data-testid="stDownloadButton"]>button:hover { border-color:#22D3EE !important; }
    [data-baseweb="input"] input,[data-baseweb="textarea"] textarea,[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input { background:#11182B !important; color:#F3F6FC !important; border-radius:10px !important; border-color:#303C59 !important; caret-color:#22D3EE !important; }
    [data-baseweb="select"]>div { background:#11182B !important; color:#F3F6FC !important; border-color:#303C59 !important; border-radius:10px !important; }
    [data-baseweb="select"] *,[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,[data-testid="stMultiSelect"] label,[data-testid="stForm"] label { color:#DCE4F4 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:#12192B !important; border-color:#2A3551 !important; border-radius:17px; }
    [data-testid="stDataFrame"] { border:1px solid #2A3551; border-radius:12px; overflow:hidden; }
    [data-testid="stAlert"] { border-radius:12px; }
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color:#203047 !important; }
    [data-testid="stExpander"] { border-color:#2A3551 !important; border-radius:12px !important; }
    hr { border-color:#27314A; }
    .stApp a { color:#22D3EE; }
    .footer-text { color:#8794B0 !important; font-size:12px; text-align:center; padding:20px 0 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================
def safe_text(value, default="Not available"):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    value = str(value).strip()
    return value if value else default


def format_number(value):
    try:
        if value is None or pd.isna(value):
            return "N/A"
        value = float(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def format_score(value):
    try:
        return "N/A" if value is None or pd.isna(value) else f"{float(value):.1f}/100"
    except (TypeError, ValueError):
        return "N/A"


def format_percent(value):
    try:
        return "N/A" if value is None or pd.isna(value) else f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def numeric_series(frame, column):
    if column not in frame.columns:
        return pd.Series(index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def dark_chart(fig, height=None):
    axis_style = {
        "gridcolor": "#27314A",
        "zerolinecolor": "#34415E",
        "linecolor": "#34415E",
        "tickfont": {"color": "#C5CEE0", "size": 11},
        "title": {"font": {"color": "#DCE4F4", "size": 12}},
    }
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12192B",
        plot_bgcolor="#12192B",
        font={"family": "Inter, Arial", "color": "#E7ECF7", "size": 12},
        title={"font": {"color": "#F4F7FD", "size": 17}},
        legend={"font": {"color": "#DCE4F4"}},
        margin={"l": 18, "r": 18, "t": 56, "b": 18},
        xaxis=axis_style,
        yaxis=axis_style,
        hoverlabel={"bgcolor": "#0B1020", "font": {"color": "#FFFFFF"}},
    )
    if height:
        fig.update_layout(height=height)
    return fig


def select_creator(channel_id):
    cid = str(channel_id)
    st.session_state["selected_channel_id"] = cid
    st.session_state["page"] = "Creator Profile"
    # Keep the profile selector in sync when a creator name is clicked.
    if "profile_creator_select" in st.session_state:
        st.session_state["profile_creator_select"] = cid


def select_page(page_name):
    st.session_state["page"] = page_name


def add_video_sample_metrics(creators, videos):
    """Add video sample-derived metrics; these describe current search results only."""
    result = creators.copy()
    for col in [
        "median_matched_video_views",
        "matched_video_count",
        "recent_matched_videos_30d",
        "recent_matched_videos_90d",
    ]:
        result[col] = pd.NA

    if creators.empty or videos is None or videos.empty or "channel_id" not in videos.columns:
        return result

    sample = videos.copy()
    sample["views"] = pd.to_numeric(sample.get("views"), errors="coerce")

    if "published_at" in sample.columns:
        sample["published_at_dt"] = pd.to_datetime(
            sample["published_at"], errors="coerce", utc=True
        )
    else:
        sample["published_at_dt"] = pd.NaT

    now = pd.Timestamp.now(tz="UTC")

    for idx, creator in result.iterrows():
        cid = str(creator.get("channel_id", ""))
        group = sample[sample["channel_id"].astype(str) == cid]
        result.at[idx, "matched_video_count"] = int(len(group))

        view_values = (
            group["views"].dropna()
            if "views" in group
            else pd.Series(dtype=float)
        )

        if not view_values.empty:
            result.at[idx, "median_matched_video_views"] = float(view_values.median())

        dates = group["published_at_dt"].dropna()
        result.at[idx, "recent_matched_videos_30d"] = int(
            (dates >= now - pd.Timedelta(days=30)).sum()
        )
        result.at[idx, "recent_matched_videos_90d"] = int(
            (dates >= now - pd.Timedelta(days=90)).sum()
        )

    return result


def creator_catalog(active_results, saved_results):
    frames = []

    if active_results is not None and not active_results.empty:
        frames.append(active_results.copy())

    if saved_results is not None and not saved_results.empty:
        frames.append(saved_results.copy())

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True, sort=False)

    if "channel_id" not in combined:
        return pd.DataFrame()

    combined["channel_id"] = combined["channel_id"].astype(str)
    combined = combined[combined["channel_id"].str.strip().ne("")]

    return combined.drop_duplicates("channel_id", keep="first").reset_index(drop=True)


def creator_label_map(creators):
    labels = {}

    for _, row in creators.iterrows():
        cid = str(row.get("channel_id", ""))
        name = safe_text(row.get("channel_name"), "YouTube creator")
        labels[cid] = f"{name} · {cid[-8:]}"

    return labels


def save_flash(message):
    st.session_state["flash_message"] = message


def display_score_breakdown(creator):
    st.markdown("#### Explainable brand-fit score")

    content_score = pd.to_numeric(
        pd.Series([creator.get("content_match_pct")]), errors="coerce"
    ).iloc[0]
    perf_score = pd.to_numeric(
        pd.Series([creator.get("performance_score")]), errors="coerce"
    ).iloc[0]
    suitability = pd.to_numeric(
        pd.Series([creator.get("suitability_score")]), errors="coerce"
    ).iloc[0]

    perf_inputs = safe_text(
        creator.get("performance_inputs_used"), "Available performance inputs"
    )

    st.metric("Final suitability", format_score(suitability))

    parts = []

    if pd.notna(content_score):
        parts.append(
            {
                "Component": "Content relevance (TF-IDF text similarity)",
                "Component score": float(content_score),
                "Final weight": "70%",
                "Final contribution": (
                    float(content_score) * 0.70
                    if pd.notna(perf_score)
                    else float(content_score)
                ),
            }
        )

    if pd.notna(perf_score):
        parts.append(
            {
                "Component": "Relative performance score",
                "Component score": float(perf_score),
                "Final weight": "30%",
                "Final contribution": float(perf_score) * 0.30,
            }
        )

    if parts:
        st.dataframe(pd.DataFrame(parts), use_container_width=True, hide_index=True)

    if pd.notna(perf_score):
        subparts = [
            ("Matched-video views", creator.get("performance_view_score"), 0.55),
            ("Public interactions / views", creator.get("performance_engagement_score"), 0.25),
            ("Subscribers", creator.get("performance_subscriber_score"), 0.20),
        ]

        details = []
        present_weight = 0.0

        for label, value, weight in subparts:
            try:
                score = float(value) if value is not None and pd.notna(value) else None
            except (TypeError, ValueError):
                score = None

            if score is not None:
                present_weight += weight
                details.append(
                    {
                        "Performance input": label,
                        "Relative score / 100": score,
                        "Base weight": f"{int(weight * 100)}%",
                    }
                )

        with st.expander("How the performance score is calculated"):
            if details:
                st.dataframe(pd.DataFrame(details), use_container_width=True, hide_index=True)

            st.write("Available inputs used: " + perf_inputs)

            if present_weight < 0.999:
                st.caption(
                    "When a metric is missing, available component weights "
                    "are renormalised proportionally."
                )

            st.caption(
                "Scores are normalised against creators in this search result "
                "set; values are relative, not industry benchmarks."
            )

    else:
        st.info(
            "Performance inputs were unavailable, so the suitability score "
            "falls back to content similarity only."
        )

    st.caption(
        "This score is an explainable shortlist heuristic, not a trained "
        "prediction model. It does not guarantee audience fit, sales or campaign ROI."
    )


def show_creator_card(creator, videos, saved_ids, campaign_tag):
    cid = str(creator.get("channel_id", ""))
    name = safe_text(creator.get("channel_name"), "YouTube creator")
    thumbnail = safe_text(creator.get("thumbnail_url"), "")

    with st.container(border=True):
        image_col, main_col, score_col = st.columns([0.8, 4.3, 1.1])

        with image_col:
            if thumbnail.startswith("http"):
                st.image(thumbnail, width=78)
            else:
                st.markdown("### ▶️")

        with main_col:
            st.button(
                f"{creator.get('rank', '•')}. {name}  ↗",
                key=f"profile_{cid}",
                type="primary",
                use_container_width=True,
                on_click=select_creator,
                args=(cid,),
                help="Open detailed creator profile",
            )

            st.caption(
                safe_text(
                    creator.get("description"),
                    "No public channel description available.",
                )[:220]
            )

        with score_col:
            st.metric("Suitability", format_score(creator.get("suitability_score")))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Subscribers", format_number(creator.get("subscriber_count")))
        c2.metric("Median matched views", format_number(creator.get("median_matched_video_views")))
        c3.metric("Content match", format_score(creator.get("content_match_pct")))
        c4.metric(
            "Interactions / views",
            format_percent(creator.get("public_interactions_per_view_pct")),
        )

        st.caption(
            safe_text(
                creator.get("recommendation_reason"),
                "Review videos and brand fit before contacting this creator.",
            )
        )

        action_col, link_col = st.columns([1.5, 1])

        with action_col:
            if cid in saved_ids:
                if st.button(
                    "★ Saved · remove",
                    key=f"unsave_{cid}",
                    use_container_width=True,
                ):
                    remove_creator_from_shortlist(cid)
                    save_flash(f"Removed {name} from your saved shortlist.")
                    st.rerun()
            else:
                if st.button(
                    "☆ Save to shortlist",
                    key=f"save_{cid}",
                    use_container_width=True,
                ):
                    save_creator_to_shortlist(
                        creator.to_dict() if hasattr(creator, "to_dict") else dict(creator),
                        campaign_tag or "General",
                    )
                    save_flash(f"Saved {name} to your shortlist.")
                    st.rerun()

        with link_col:
            url = safe_text(creator.get("channel_url"), "")
            if url:
                st.link_button("Open YouTube ↗", url, use_container_width=True)

        if videos is not None and not videos.empty and "channel_id" in videos.columns:
            matching = videos[videos["channel_id"].astype(str) == cid]

            if not matching.empty:
                with st.expander("Top matching videos"):
                    top = matching.copy()
                    top["views"] = pd.to_numeric(top.get("views"), errors="coerce")
                    top = top.sort_values("views", ascending=False, na_position="last").head(4)

                    for _, video in top.iterrows():
                        thumb_url = safe_text(video.get("thumbnail_url"), "")
                        a, b = st.columns([1, 4])

                        with a:
                            if thumb_url.startswith("http"):
                                st.image(thumb_url, use_container_width=True)

                        with b:
                            st.markdown(
                                f"**{safe_text(video.get('video_title'), 'YouTube video')}**"
                            )
                            st.caption(
                                f"Views {format_number(video.get('views'))} · "
                                f"Likes {format_number(video.get('likes'))} · "
                                f"Comments {format_number(video.get('comments'))}"
                            )
                            video_url = safe_text(video.get("video_url"), "")
                            if video_url:
                                st.markdown(f"[Watch video ↗]({video_url})")


def make_keyword_performance(videos):
    """Aggregate video title keywords over the current search sample."""
    if videos is None or videos.empty or "video_title" not in videos.columns:
        return pd.DataFrame()

    common = {
        "the", "and", "for", "with", "from", "this", "that", "you", "your",
        "are", "was", "how", "what", "why", "new", "best", "top", "review",
        "reviews", "official", "full", "video", "shorts", "short", "in", "on",
        "to", "of", "a", "an", "is", "it", "my", "our", "vs", "2024", "2025", "2026",
    }

    rows = []
    sample = videos.copy()
    sample["views"] = pd.to_numeric(sample.get("views"), errors="coerce")

    for _, row in sample.iterrows():
        title = safe_text(row.get("video_title"), "")
        tokens = set(
            re.findall(r"[a-zA-Z][a-zA-Z0-9+#-]{2,}", title.lower())
        ) - common

        views = row.get("views")

        for token in tokens:
            rows.append({"Keyword": token, "Video title": title, "Views": views})

    if not rows:
        return pd.DataFrame()

    words = pd.DataFrame(rows)
    out = words.groupby("Keyword", as_index=False).agg(
        Videos=("Video title", "nunique"),
        Median_views=("Views", "median"),
        Average_views=("Views", "mean"),
    )

    return out.sort_values(
        ["Median_views", "Videos"],
        ascending=False,
        na_position="last",
    ).head(20)


# ============================================================
# INITIALISATION AND SESSION STATE
# ============================================================
try:
    initialize_database()
except Exception as exc:
    st.error(f"Could not initialize the local database: {exc}")

DEFAULTS = {
    "page": PAGES[0],
    "ranked_creators": pd.DataFrame(),
    "matched_videos": pd.DataFrame(),
    "searched_product": "",
    "search_timestamp": "",
    "selected_channel_id": "",
    "flash_message": "",
}

for key, default in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state["page"] not in PAGES:
    st.session_state["page"] = PAGES[0]

ranked_active = st.session_state["ranked_creators"]
videos_active = st.session_state["matched_videos"]
saved_rows = get_saved_creators()
saved_df = pd.DataFrame(saved_rows)
catalog = creator_catalog(ranked_active, saved_df)

saved_ids = (
    set(saved_df["channel_id"].astype(str))
    if not saved_df.empty and "channel_id" in saved_df
    else set()
)

with st.sidebar:
    st.markdown(
        '<div class="brand-mark">CREATOR INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )
    st.markdown("## Creator Intelligence Pro")
    st.caption("YouTube Creator Analytics")
    st.divider()
    st.radio("WORKSPACE", PAGES, key="page")
    st.divider()
    st.markdown("**PLATFORM**")
    st.write("▶️ YouTube Data API v3")
    st.caption(
        "Public channel and video statistics only. API access and quota limit results."
    )
    st.divider()
    st.caption(f"Saved shortlist: {len(saved_ids)} creator(s)")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">YOUTUBE CREATOR INTELLIGENCE</div>
      <h1>Find the right creators.<br>Compare the evidence.</h1>
      <p>Discover channels for a product, compare creator performance, save a shortlist, and explore explainable brand-fit scores.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("flash_message"):
    st.success(st.session_state["flash_message"])
    st.session_state["flash_message"] = ""

# ============================================================
# DISCOVER INFLUENCERS
# ============================================================
if st.session_state["page"] == "Discover Influencers":
    st.markdown(
        '<div class="section-heading">Discover creators</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Search by product, brand or campaign topic. Results are based on "
        "public videos returned by YouTube search."
    )

    with st.form("youtube_product_search", clear_on_submit=False):
        product = st.text_input(
            "Product or brand",
            placeholder="e.g. running shoes, skincare, smartphones",
        )

        left, right = st.columns([3, 1])

        with right:
            max_results = st.selectbox(
                "Videos to search",
                [10, 20, 25, 50],
                index=2,
            )

        with left:
            st.caption(
                "More results can help discover additional creators, "
                "but API quota is limited."
            )

        submitted = st.form_submit_button(
            "Search YouTube creators →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not product.strip():
            st.warning("Enter a product or brand first.")
        else:
            try:
                with st.spinner(
                    "Searching public YouTube videos and analysing channels…"
                ):
                    channels, videos = search_youtube_influencers(
                        product.strip(),
                        max_results=max_results,
                    )
                    ranked_now = rank_influencers(product.strip(), channels, videos)
                    ranked_now = add_video_sample_metrics(ranked_now, videos)

                st.session_state["ranked_creators"] = ranked_now
                st.session_state["matched_videos"] = videos
                st.session_state["searched_product"] = product.strip()
                st.session_state["search_timestamp"] = datetime.now().strftime(
                    "%d %b %Y, %I:%M %p"
                )
                st.session_state["selected_channel_id"] = ""
                st.session_state.pop("compare_channel_ids", None)

                errors = 0
                for _, creator in ranked_now.iterrows():
                    try:
                        save_channel_snapshot(creator)
                    except Exception:
                        errors += 1

                if errors:
                    st.warning(
                        f"{errors} snapshot(s) could not be saved; "
                        "check the local database."
                    )

                if ranked_now.empty:
                    st.info("No channels found for that phrase. Try a broader search term.")

                st.rerun()

            except YouTubeAPIError as exc:
                st.error(f"YouTube API request failed: {exc}")
                st.info(
                    "Check YouTube Data API v3, the YOUTUBE_API_KEY in "
                    ".streamlit/secrets.toml, and available quota."
                )

            except Exception as exc:
                st.error(f"Creator analysis failed: {exc}")

    ranked_active = st.session_state["ranked_creators"]
    videos_active = st.session_state["matched_videos"]

    if not ranked_active.empty:
        st.divider()
        st.markdown(
            f"### Results for: {safe_text(st.session_state['searched_product'])}"
        )
        st.caption(
            f"Retrieved {safe_text(st.session_state['search_timestamp'])} · "
            "public YouTube API data"
        )

        subs = numeric_series(ranked_active, "subscriber_count").dropna()
        med_views = numeric_series(ranked_active, "median_matched_video_views").dropna()
        scores = numeric_series(ranked_active, "suitability_score").dropna()

        a, b, c, d = st.columns(4)
        a.metric("Creators found", f"{len(ranked_active):,}")
        b.metric(
            "Median subscribers",
            format_number(subs.median()) if not subs.empty else "N/A",
        )
        c.metric(
            "Median matched-video views",
            format_number(med_views.median()) if not med_views.empty else "N/A",
        )
        d.metric(
            "Average suitability",
            format_score(scores.mean()) if not scores.empty else "N/A",
        )

        chart_col, explanation_col = st.columns([1.5, 1])

        with chart_col:
            st.markdown("#### Highest suitability scores")
            chart = ranked_active.copy()
            chart["suitability_score"] = pd.to_numeric(
                chart.get("suitability_score"), errors="coerce"
            )
            chart = (
                chart.dropna(subset=["suitability_score"])
                .nlargest(10, "suitability_score")
                .sort_values("suitability_score")
            )

            if not chart.empty:
                fig = px.bar(
                    chart,
                    x="suitability_score",
                    y="channel_name",
                    orientation="h",
                    labels={
                        "suitability_score": "Suitability / 100",
                        "channel_name": "",
                    },
                )
                fig.update_traces(
                    marker_color="#8B5CF6",
                    hovertemplate="%{y}<br>Suitability: %{x:.1f}/100<extra></extra>",
                )
                fig.update_xaxes(range=[0, 100])
                st.plotly_chart(
                    dark_chart(fig, max(300, len(chart) * 36)),
                    use_container_width=True,
                )

        with explanation_col:
            st.markdown("#### Scoring at a glance")
            st.write("**70% content match** + **30% relative performance**, when performance inputs exist.")
            st.write(
                "Performance uses matched-video views (55%), public interactions/views (25%) "
                "and subscribers (20%), with available weights renormalised if a field is missing."
            )
            st.caption(
                "Scores are relative to the current search sample, not industry benchmarks "
                "or a trained prediction model."
            )

        st.divider()
        st.markdown("### Ranked creator shortlist")
        filter_col, sort_col, min_col, download_col = st.columns([2, 1.6, 1.5, 1.15])

        with filter_col:
            name_filter = st.text_input(
                "Filter by creator name",
                placeholder="Type a channel name…",
                key="discover_filter",
            ).strip().lower()

        with sort_col:
            sort_label = st.selectbox(
                "Sort by",
                [
                    "Best suitability",
                    "Subscribers",
                    "Median views",
                    "Content match",
                    "Interactions / views",
                ],
                key="discover_sort",
            )

        with min_col:
            min_match = st.slider(
                "Min content match",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                key="min_content_match",
            )

        sort_map = {
            "Best suitability": "suitability_score",
            "Subscribers": "subscriber_count",
            "Median views": "median_matched_video_views",
            "Content match": "content_match_pct",
            "Interactions / views": "public_interactions_per_view_pct",
        }

        display_creators = ranked_active.copy()

        if name_filter:
            display_creators = display_creators[
                display_creators["channel_name"].astype(str).str.lower().str.contains(
                    name_filter, na=False
                )
            ]

        display_creators = display_creators[
            pd.to_numeric(
                display_creators["content_match_pct"], errors="coerce"
            ).fillna(0) >= min_match
        ]

        sort_column = sort_map[sort_label]

        if sort_column in display_creators.columns:
            display_creators[sort_column] = pd.to_numeric(
                display_creators[sort_column], errors="coerce"
            )
            display_creators = display_creators.sort_values(
                sort_column, ascending=False, na_position="last"
            )

        with download_col:
            st.write("")
            st.download_button(
                "Export CSV",
                data=display_creators.to_csv(index=False).encode("utf-8-sig"),
                file_name="youtube_creator_shortlist.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.caption(
            f"Showing {len(display_creators)} of {len(ranked_active)} creators. "
            "Click a creator name to open the detailed profile."
        )

        if display_creators.empty:
            st.info(
                "No creators match these filters. Lower the minimum content match "
                "or clear the name filter."
            )
        else:
            saved_now = get_saved_creators()
            current_saved_ids = {str(item["channel_id"]) for item in saved_now}

            for _, creator in display_creators.iterrows():
                show_creator_card(
                    creator,
                    videos_active,
                    current_saved_ids,
                    st.session_state.get("searched_product") or "General",
                )

        with st.expander("View complete creator data table"):
            table_cols = [
                c for c in [
                    "rank", "channel_name", "subscriber_count",
                    "average_matched_video_views", "median_matched_video_views",
                    "recent_matched_videos_30d", "public_interactions_per_view_pct",
                    "content_match_pct", "performance_score", "suitability_score",
                ]
                if c in display_creators.columns
            ]

            st.dataframe(
                display_creators[table_cols].rename(
                    columns={
                        "rank": "Rank",
                        "channel_name": "Creator",
                        "subscriber_count": "Subscribers",
                        "average_matched_video_views": "Average matched views",
                        "median_matched_video_views": "Median matched views",
                        "recent_matched_videos_30d": "Matched uploads in 30 days",
                        "public_interactions_per_view_pct": "Interactions / views %",
                        "content_match_pct": "Content match / 100",
                        "performance_score": "Performance / 100",
                        "suitability_score": "Suitability / 100",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

# ============================================================
# COMPARE CREATORS
# ============================================================
elif st.session_state["page"] == "Compare Creators":
    st.markdown(
        '<div class="section-heading">Creator Comparison Studio</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Compare 2–5 current or saved creators using the same metrics "
        "and a transparent score breakdown."
    )

    saved_df = pd.DataFrame(get_saved_creators())
    catalog = creator_catalog(st.session_state["ranked_creators"], saved_df)

    if catalog.empty:
        st.info("Run a YouTube search or save creators to your shortlist before comparing.")
        st.button(
            "Go to discovery",
            type="primary",
            on_click=select_page,
            args=("Discover Influencers",),
        )
    else:
        label_map = creator_label_map(catalog)
        available_ids = list(label_map.keys())

        prior = st.session_state.get("compare_channel_ids", [])
        valid_prior = [cid for cid in prior if cid in available_ids]
        default_ids = valid_prior or available_ids[:min(3, len(available_ids))]

        selected_ids = st.multiselect(
            "Select up to 5 creators",
            options=available_ids,
            default=default_ids,
            max_selections=5,
            format_func=lambda cid: label_map.get(cid, cid),
            key="compare_channel_ids",
        )

        selected = catalog[
            catalog["channel_id"].astype(str).isin([str(x) for x in selected_ids])
        ].copy()
        selected["channel_id"] = selected["channel_id"].astype(str)

        if not selected.empty:
            selected = selected.set_index("channel_id").loc[
                [x for x in selected_ids if x in selected.set_index("channel_id").index]
            ].reset_index()

        if len(selected) < 2:
            st.info("Select at least two creators to show a comparison.")
        else:
            st.markdown("### Side-by-side creator metrics")

            cols = [
                c for c in [
                    "channel_name", "subscriber_count", "total_channel_views",
                    "total_channel_videos", "average_matched_video_views",
                    "median_matched_video_views", "public_interactions_per_view_pct",
                    "content_match_pct", "performance_score", "suitability_score",
                ]
                if c in selected.columns
            ]

            comparison = selected[cols].rename(
                columns={
                    "channel_name": "Creator",
                    "subscriber_count": "Subscribers",
                    "total_channel_views": "Lifetime views",
                    "total_channel_videos": "Videos",
                    "average_matched_video_views": "Average matched views",
                    "median_matched_video_views": "Median matched views",
                    "public_interactions_per_view_pct": "Interactions / views %",
                    "content_match_pct": "Content match / 100",
                    "performance_score": "Performance / 100",
                    "suitability_score": "Suitability / 100",
                }
            )
            st.dataframe(comparison, use_container_width=True, hide_index=True)

            metric_labels = {
                "Suitability score": ("suitability_score", "Score / 100"),
                "Content match": ("content_match_pct", "Score / 100"),
                "Performance score": ("performance_score", "Score / 100"),
                "Subscribers": ("subscriber_count", "Subscribers"),
                "Median matched-video views": ("median_matched_video_views", "Views"),
                "Public interactions / views": ("public_interactions_per_view_pct", "Percent"),
                "Lifetime channel views": ("total_channel_views", "Views"),
            }

            metric_choice = st.selectbox(
                "Metric to visualise",
                list(metric_labels.keys()),
                key="compare_metric",
            )
            metric_col, metric_axis = metric_labels[metric_choice]

            if metric_col in selected.columns:
                selected[metric_col] = pd.to_numeric(
                    selected[metric_col], errors="coerce"
                )
                chart = selected.dropna(subset=[metric_col]).copy()

                if not chart.empty:
                    fig = px.bar(
                        chart,
                        x=metric_col,
                        y="channel_name",
                        orientation="h",
                        title=f"Comparison: {metric_choice}",
                        labels={metric_col: metric_axis, "channel_name": "Creator"},
                    )
                    fig.update_traces(
                        marker_color="#8B5CF6",
                        texttemplate="%{x:,.2f}",
                        textposition="outside",
                        cliponaxis=False,
                    )

                    if metric_choice in (
                        "Suitability score", "Content match", "Performance score"
                    ):
                        fig.update_xaxes(range=[0, 110])

                    st.plotly_chart(
                        dark_chart(fig, max(340, len(chart) * 55)),
                        use_container_width=True,
                    )
                else:
                    st.info(f"{metric_choice} is not available for these selected creators.")

            st.markdown("### Compare scoring evidence")
            score_rows = []

            for _, row in selected.iterrows():
                score_rows.append(
                    {
                        "Creator": safe_text(row.get("channel_name")),
                        "Content match": row.get("content_match_pct"),
                        "Views component": row.get("performance_view_score"),
                        "Interactions component": row.get("performance_engagement_score"),
                        "Subscriber component": row.get("performance_subscriber_score"),
                        "Performance score": row.get("performance_score"),
                        "Final suitability": row.get("suitability_score"),
                        "Formula used": safe_text(
                            row.get("score_formula"),
                            "Saved score; inspect data availability",
                        ),
                    }
                )

            st.dataframe(pd.DataFrame(score_rows), use_container_width=True, hide_index=True)
            st.caption(
                "Normalised component scores are relative to the current search set. "
                "Saved creators from older searches may have been scored against a different group."
            )
            st.download_button(
                "Download creator comparison CSV",
                data=comparison.to_csv(index=False).encode("utf-8-sig"),
                file_name="creator_comparison.csv",
                mime="text/csv",
            )

# ============================================================
# SAVED SHORTLIST
# ============================================================
elif st.session_state["page"] == "Saved Shortlist":
    st.markdown(
        '<div class="section-heading">Saved Creator Shortlist</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Favorites persist in your local SQLite database. Saving from discovery "
        "tags the creator with the searched product/topic."
    )

    saved_items = get_saved_creators()

    if not saved_items:
        st.info(
            "No saved creators yet. Go to Discover Influencers and click "
            "☆ Save to shortlist on a creator card."
        )
        st.button(
            "Open discovery",
            type="primary",
            on_click=select_page,
            args=("Discover Influencers",),
        )
    else:
        saved_frame = pd.DataFrame(saved_items)
        campaigns = ["All campaigns"] + get_shortlist_campaigns()

        campaign_filter = st.selectbox(
            "Filter by campaign / search topic",
            campaigns,
            key="saved_campaign_filter",
        )

        if campaign_filter != "All campaigns":
            visible = saved_frame[
                saved_frame["campaign_tag"] == campaign_filter
            ].copy()
        else:
            visible = saved_frame.copy()

        a, b, c = st.columns(3)
        a.metric("Saved creators", len(visible))
        b.metric(
            "Campaign tags",
            visible["campaign_tag"].nunique() if "campaign_tag" in visible else 0,
        )
        c.metric(
            "High suitability (≥70)",
            int(
                (
                    pd.to_numeric(visible["suitability_score"], errors="coerce") >= 70
                ).sum()
            ) if "suitability_score" in visible else 0,
        )

        export_cols = [
            c for c in [
                "channel_name", "campaign_tag", "subscriber_count",
                "average_matched_video_views", "median_matched_video_views",
                "public_interactions_per_view_pct", "content_match_pct",
                "performance_score", "suitability_score", "channel_url", "saved_at",
            ]
            if c in visible.columns
        ]

        st.dataframe(
            visible[export_cols].rename(
                columns={
                    "channel_name": "Creator",
                    "campaign_tag": "Campaign tag",
                    "subscriber_count": "Subscribers",
                    "average_matched_video_views": "Average matched views",
                    "median_matched_video_views": "Median matched views",
                    "public_interactions_per_view_pct": "Interactions / views %",
                    "content_match_pct": "Content match / 100",
                    "performance_score": "Performance / 100",
                    "suitability_score": "Suitability / 100",
                    "channel_url": "Channel URL",
                    "saved_at": "Saved at",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Export saved shortlist CSV",
            data=visible.to_csv(index=False).encode("utf-8-sig"),
            file_name="saved_creator_shortlist.csv",
            mime="text/csv",
        )

        st.markdown("### Manage saved creators")

        for _, saved_creator in visible.iterrows():
            cid = str(saved_creator.get("channel_id", ""))
            name = safe_text(saved_creator.get("channel_name"), "YouTube creator")

            with st.container(border=True):
                name_col, campaign_col, actions_col = st.columns([2.4, 1.5, 1.8])

                with name_col:
                    st.markdown(f"**{name}**")
                    st.caption(
                        f"Subscribers: {format_number(saved_creator.get('subscriber_count'))} · "
                        f"Suitability: {format_score(saved_creator.get('suitability_score'))}"
                    )

                with campaign_col:
                    st.caption("Campaign / tag")
                    st.write(safe_text(saved_creator.get("campaign_tag"), "General"))

                with actions_col:
                    st.button(
                        "Open analysis",
                        key=f"saved_open_{cid}",
                        use_container_width=True,
                        on_click=select_creator,
                        args=(cid,),
                    )

                    if st.button("Remove", key=f"saved_remove_{cid}", use_container_width=True):
                        remove_creator_from_shortlist(cid)
                        save_flash(f"Removed {name} from the shortlist.")
                        st.rerun()

# ============================================================
# CREATOR PROFILE
# ============================================================
elif st.session_state["page"] == "Creator Profile":
    st.markdown(
        '<div class="section-heading">Creator intelligence profile</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Public channel overview, explainable brand fit, search-sample video "
        "performance and locally saved history."
    )

    saved_frame = pd.DataFrame(get_saved_creators())
    active = st.session_state["ranked_creators"]
    all_creators = creator_catalog(active, saved_frame)

    if all_creators.empty:
        st.info(
            "Search for a product or save a creator first, then come back here "
            "to view channel analysis."
        )
        st.button(
            "← Go to discovery",
            type="primary",
            on_click=select_page,
            args=("Discover Influencers",),
        )
    else:
        labels = creator_label_map(all_creators)
        ids = list(labels)
        current_id = str(st.session_state.get("selected_channel_id", ""))
        default_label = current_id if current_id in ids else ids[0]

        chosen_id = st.selectbox(
            "Choose a channel to analyse",
            ids,
            index=ids.index(default_label),
            format_func=lambda cid: labels.get(cid, cid),
            key="profile_creator_select",
        )

        st.session_state["selected_channel_id"] = chosen_id
        selected = all_creators[
            all_creators["channel_id"].astype(str) == chosen_id
        ]

        if selected.empty:
            st.error(
                "This channel is no longer available. Please refresh your search or shortlist."
            )
        else:
            creator = selected.iloc[0]
            name = safe_text(creator.get("channel_name"), "YouTube creator")
            thumbnail = safe_text(creator.get("thumbnail_url"), "")

            img_col, title_col = st.columns([0.8, 5])

            with img_col:
                if thumbnail.startswith("http"):
                    st.image(thumbnail, width=105)
                else:
                    st.markdown("## ▶️")

            with title_col:
                st.markdown(f"## {name}")
                st.caption(
                    safe_text(
                        creator.get("description"),
                        "No public channel description available.",
                    )
                )

                url = safe_text(creator.get("channel_url"), "")
                if url:
                    st.link_button("Open YouTube channel ↗", url)

                if chosen_id in saved_ids:
                    st.caption("★ Saved to your shortlist")
                else:
                    if st.button(
                        "☆ Save this creator",
                        key=f"profile_save_{chosen_id}",
                    ):
                        save_creator_to_shortlist(
                            creator.to_dict(),
                            st.session_state.get("searched_product") or "General",
                        )
                        save_flash(f"Saved {name} to your shortlist.")
                        st.rerun()

            st.divider()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Subscribers", format_number(creator.get("subscriber_count")))
            m2.metric("Lifetime channel views", format_number(creator.get("total_channel_views")))
            m3.metric("Total channel videos", format_number(creator.get("total_channel_videos")))
            m4.metric("Suitability / 100", format_score(creator.get("suitability_score")))

            pub = pd.to_datetime(
                creator.get("published_at"), utc=True, errors="coerce"
            )
            channel_age = "Not available"

            if pd.notna(pub):
                days = max(0, (pd.Timestamp.now(tz="UTC") - pub).days)
                channel_age = f"{days // 365} years, {(days % 365) // 30} months"

            age_col, match_col, median_col, recent_col = st.columns(4)
            age_col.metric("Channel age", channel_age)
            match_col.metric("Content match", format_score(creator.get("content_match_pct")))
            median_col.metric("Median matched views", format_number(creator.get("median_matched_video_views")))
            recent_col.metric("Matched uploads · 30d", format_number(creator.get("recent_matched_videos_30d")))

            with st.expander("Explain the suitability score", expanded=True):
                display_score_breakdown(creator)

            st.markdown("### Growth analytics")
            period = st.selectbox(
                "History period",
                [
                    "Daily · last 30 days",
                    "Weekly · last 12 weeks",
                    "Monthly · last 12 months",
                    "Yearly · last 5 years",
                    "All saved history",
                ],
                key="profile_history_period",
            )

            periods = {
                "Daily · last 30 days": (30, "daily"),
                "Weekly · last 12 weeks": (84, "weekly"),
                "Monthly · last 12 months": (366, "monthly"),
                "Yearly · last 5 years": (1826, "yearly"),
                "All saved history": (None, "all"),
            }

            days_back, cadence = periods[period]

            try:
                history = pd.DataFrame(get_channel_history(chosen_id))
            except Exception as exc:
                history = pd.DataFrame()
                st.warning(f"Could not read history: {exc}")

            if history.empty:
                st.info(
                    "No snapshots have been saved for this creator yet. "
                    "Successful searches over time will build real history."
                )
            else:
                history["recorded_at"] = pd.to_datetime(
                    history["recorded_at"], errors="coerce", utc=True
                )
                history = history.dropna(
                    subset=["recorded_at"]
                ).sort_values("recorded_at").copy()

                if days_back is not None:
                    cutoff = (
                        pd.Timestamp.now(tz="UTC")
                        - pd.Timedelta(days=days_back)
                    )
                    history = history[history["recorded_at"] >= cutoff].copy()

                metric_map = {
                    "Subscribers": "subscriber_count",
                    "Lifetime views": "total_channel_views",
                    "Channel videos": "total_channel_videos",
                    "Average matched views": "average_matched_video_views",
                    "Public interactions / views (%)": "public_interactions_per_view_pct",
                }

                metric_name = st.selectbox(
                    "Growth metric",
                    list(metric_map),
                    key="profile_growth_metric",
                )
                metric = metric_map[metric_name]

                if (
                    history.empty
                    or metric not in history.columns
                    or pd.to_numeric(
                        history.get(metric), errors="coerce"
                    ).notna().sum() == 0
                ):
                    st.info(
                        "No saved values for this metric in the selected period. "
                        "More snapshots are needed."
                    )
                else:
                    history[metric] = pd.to_numeric(
                        history[metric], errors="coerce"
                    )
                    plotted = history.copy()
                    dates = plotted["recorded_at"].dt.tz_localize(None)

                    if cadence == "daily":
                        plotted["chart_date"] = dates.dt.floor("D")
                    elif cadence == "weekly":
                        plotted["chart_date"] = (
                            dates.dt.to_period("W-SUN").dt.start_time
                        )
                    elif cadence == "monthly":
                        plotted["chart_date"] = (
                            dates.dt.to_period("M").dt.start_time
                        )
                    elif cadence == "yearly":
                        plotted["chart_date"] = (
                            dates.dt.to_period("Y").dt.start_time
                        )
                    else:
                        plotted["chart_date"] = dates

                    if cadence != "all":
                        plotted = plotted.drop_duplicates(
                            "chart_date", keep="last"
                        )

                    plotted = plotted.dropna(
                        subset=[metric]
                    ).sort_values("chart_date")

                    if not plotted.empty:
                        fig = px.line(
                            plotted,
                            x="chart_date",
                            y=metric,
                            markers=True,
                            title=f"{metric_name} over time",
                            labels={"chart_date": "Date", metric: metric_name},
                        )
                        fig.update_traces(
                            line_color="#22D3EE",
                            marker_color="#8B5CF6",
                            line_width=3,
                        )
                        st.plotly_chart(
                            dark_chart(fig, 360),
                            use_container_width=True,
                        )

                        first, last = (
                            float(plotted[metric].iloc[0]),
                            float(plotted[metric].iloc[-1]),
                        )
                        delta = last - first
                        pct = delta / first * 100 if first else None

                        g1, g2, g3 = st.columns(3)
                        g1.metric("First saved value", format_number(first))
                        g2.metric("Latest saved value", format_number(last), delta=format_number(delta))
                        g3.metric(
                            "Change across period",
                            f"{pct:+.2f}%" if pct is not None else "N/A",
                        )

                        if len(plotted) < 2:
                            st.info(
                                "One snapshot is not enough to calculate growth. "
                                "Use the app over time to add more snapshots."
                            )

                    st.download_button(
                        "Export history CSV",
                        data=history.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"creator_history_{chosen_id}.csv",
                        mime="text/csv",
                    )

            st.markdown("### Video performance in this search sample")
            all_videos = st.session_state["matched_videos"]

            if (
                all_videos is None
                or all_videos.empty
                or "channel_id" not in all_videos.columns
            ):
                creator_videos = pd.DataFrame()
            else:
                creator_videos = all_videos[
                    all_videos["channel_id"].astype(str) == chosen_id
                ].copy()

            if creator_videos.empty:
                st.info(
                    "No matched videos for this saved creator are in the active search. "
                    "Start a search with a relevant topic to populate this section."
                )
            else:
                creator_videos["views"] = pd.to_numeric(
                    creator_videos.get("views"), errors="coerce"
                )
                published = pd.to_datetime(
                    creator_videos.get("published_at"), errors="coerce", utc=True
                )
                now = pd.Timestamp.now(tz="UTC")

                v1, v2, v3, v4 = st.columns(4)
                v1.metric("Videos in sample", len(creator_videos))
                v2.metric("Median views", format_number(creator_videos["views"].median()))
                v3.metric("Average views", format_number(creator_videos["views"].mean()))
                v4.metric(
                    "Matched uploads · 90d",
                    int((published >= now - pd.Timedelta(days=90)).sum()),
                )

                st.caption(
                    "This is a product/topic search sample returned by YouTube, "
                    "not every upload on the channel."
                )

                top = (
                    creator_videos.dropna(subset=["views"])
                    .nlargest(10, "views")
                    .sort_values("views")
                )

                if not top.empty:
                    fig = px.bar(
                        top,
                        x="views",
                        y="video_title",
                        orientation="h",
                        title="Top matched videos by views",
                        labels={"views": "Views", "video_title": "Video"},
                    )
                    fig.update_traces(marker_color="#7657E8")
                    st.plotly_chart(
                        dark_chart(fig, max(320, len(top) * 34)),
                        use_container_width=True,
                    )

                cols = [
                    c for c in [
                        "video_title", "published_at", "views", "likes",
                        "comments", "engagement_rate_pct", "video_url",
                    ]
                    if c in creator_videos.columns
                ]

                cfg = (
                    {"video_url": st.column_config.LinkColumn("Video", display_text="Watch ↗")}
                    if "video_url" in cols else {}
                )

                st.dataframe(
                    creator_videos[cols],
                    column_config=cfg,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Export this creator's video sample",
                    data=creator_videos.to_csv(index=False).encode("utf-8-sig"),
                    file_name=f"creator_videos_{chosen_id}.csv",
                    mime="text/csv",
                )

            st.caption(
                "Private audience demographics, watch time and unique reach "
                "are not available through this public-data workflow."
            )

# ============================================================
# VIDEO PERFORMANCE INTELLIGENCE
# ============================================================
elif st.session_state["page"] == "Video Performance":
    st.markdown(
        '<div class="section-heading">Video Performance Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Performance statistics below are calculated only from videos "
        "returned by your current product/topic search."
    )

    videos = st.session_state["matched_videos"]

    if videos is None or videos.empty:
        st.info("Search a product in Discover Influencers first to populate video analytics.")
        st.button(
            "Open creator discovery",
            type="primary",
            on_click=select_page,
            args=("Discover Influencers",),
        )
    else:
        sample = videos.copy()
        sample["views"] = pd.to_numeric(sample.get("views"), errors="coerce")
        sample["likes"] = pd.to_numeric(sample.get("likes"), errors="coerce")
        sample["comments"] = pd.to_numeric(sample.get("comments"), errors="coerce")
        sample["published_at_dt"] = pd.to_datetime(
            sample.get("published_at"), errors="coerce", utc=True
        )

        now = pd.Timestamp.now(tz="UTC")
        last30 = sample[
            sample["published_at_dt"] >= now - pd.Timedelta(days=30)
        ]
        last90 = sample[
            sample["published_at_dt"] >= now - pd.Timedelta(days=90)
        ]

        i1, i2, i3, i4, i5 = st.columns(5)
        i1.metric("Videos in search sample", len(sample))
        i2.metric("Median views", format_number(sample["views"].median()))
        i3.metric("Average views", format_number(sample["views"].mean()))
        i4.metric("Matched uploads · 30d", len(last30))
        i5.metric("Matched uploads · 90d", len(last90))

        st.caption(
            "Upload counts here count matching videos returned by the current "
            "search, not a complete list of recent uploads for every channel."
        )

        creator_lookup = creator_label_map(st.session_state["ranked_creators"])
        channel_ids = list(creator_lookup)

        if channel_ids:
            selected_channel = st.selectbox(
                "Focus on creator",
                ["All creators"] + channel_ids,
                format_func=lambda x: (
                    "All creators" if x == "All creators"
                    else creator_lookup.get(x, x)
                ),
                key="video_page_creator",
            )

            if selected_channel != "All creators":
                sample = sample[
                    sample["channel_id"].astype(str) == selected_channel
                ].copy()

        if sample.empty:
            st.info("No videos match the selected creator in this search sample.")
        else:
            top = (
                sample.dropna(subset=["views"])
                .nlargest(15, "views")
                .sort_values("views")
            )

            if not top.empty:
                fig = px.bar(
                    top,
                    x="views",
                    y="video_title",
                    orientation="h",
                    title="Top-performing videos in this search sample",
                    labels={"views": "Views", "video_title": "Video title"},
                )
                fig.update_traces(marker_color="#8B5CF6")
                st.plotly_chart(
                    dark_chart(fig, max(400, len(top) * 31)),
                    use_container_width=True,
                )

            st.markdown("### Video-level metrics")

            display = [
                c for c in [
                    "channel_title", "video_title", "published_at",
                    "views", "likes", "comments", "engagement_rate_pct", "video_url",
                ]
                if c in sample.columns
            ]

            cfg = (
                {"video_url": st.column_config.LinkColumn("Video", display_text="Watch ↗")}
                if "video_url" in display else {}
            )

            st.dataframe(
                sample[display].sort_values(
                    "views", ascending=False, na_position="last"
                ),
                column_config=cfg,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Export video performance CSV",
                data=sample.drop(
                    columns=["published_at_dt"], errors="ignore"
                ).to_csv(index=False).encode("utf-8-sig"),
                file_name="video_performance_intelligence.csv",
                mime="text/csv",
            )

            keywords = make_keyword_performance(sample)

            if not keywords.empty:
                st.markdown("### Title-keyword performance signals")
                st.caption(
                    "Keywords are extracted from titles in this search sample. "
                    "They are exploratory signals, not definitive audience-interest labels."
                )

                st.dataframe(
                    keywords.rename(
                        columns={
                            "Median_views": "Median views",
                            "Average_views": "Average views",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                keyword_chart = keywords.head(12).sort_values(
                    "Median_views", ascending=True
                )

                fig = px.bar(
                    keyword_chart,
                    x="Median_views",
                    y="Keyword",
                    orientation="h",
                    title="Median views by title keyword",
                    labels={
                        "Median_views": "Median views",
                        "Keyword": "Title keyword",
                    },
                )

                fig.update_traces(marker_color="#22D3EE")
                st.plotly_chart(
                    dark_chart(fig, max(330, len(keyword_chart) * 28)),
                    use_container_width=True,
                )

# ============================================================
# DASHBOARD OVERVIEW
# ============================================================
elif st.session_state["page"] == "Dashboard Overview":
    st.markdown(
        '<div class="section-heading">Dashboard overview</div>',
        unsafe_allow_html=True,
    )

    ranked = st.session_state["ranked_creators"]
    saved = pd.DataFrame(get_saved_creators())
    tracking = get_tracking_summary()

    a, b, c, d = st.columns(4)
    a.metric("Saved creators", len(saved))
    b.metric("Tracked channels", int(tracking.get("tracked_channels", 0)))
    c.metric("Snapshots saved", int(tracking.get("snapshot_count", 0)))
    d.metric("Current search results", len(ranked))

    if not ranked.empty:
        st.markdown(
            f"### Current search: {safe_text(st.session_state['searched_product'])}"
        )

        score = numeric_series(ranked, "suitability_score")
        subs = numeric_series(ranked, "subscriber_count")
        views = numeric_series(ranked, "median_matched_video_views")

        x1, x2, x3 = st.columns(3)
        x1.metric(
            "Average suitability",
            format_score(score.mean()) if score.notna().any() else "N/A",
        )
        x2.metric(
            "Median subscribers",
            format_number(subs.median()) if subs.notna().any() else "N/A",
        )
        x3.metric(
            "Median matched views",
            format_number(views.median()) if views.notna().any() else "N/A",
        )

        cols = [
            c for c in [
                "rank", "channel_name", "subscriber_count",
                "median_matched_video_views", "content_match_pct",
                "performance_score", "suitability_score",
            ]
            if c in ranked.columns
        ]

        st.dataframe(
            ranked[cols].rename(
                columns={
                    "rank": "Rank",
                    "channel_name": "Creator",
                    "subscriber_count": "Subscribers",
                    "median_matched_video_views": "Median matched views",
                    "content_match_pct": "Content match / 100",
                    "performance_score": "Performance / 100",
                    "suitability_score": "Suitability / 100",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Export overview CSV",
            data=ranked.to_csv(index=False).encode("utf-8-sig"),
            file_name="creator_dashboard_overview.csv",
            mime="text/csv",
        )
    else:
        st.info(
            "Run a search to see current creator analytics. Your saved shortlist "
            "and snapshot totals remain available across app restarts."
        )

    latest = pd.DataFrame(get_latest_channel_snapshots())

    if not latest.empty:
        st.markdown("### Latest saved public-statistic snapshots")

        cols = [
            c for c in [
                "channel_name", "subscriber_count", "total_channel_views",
                "total_channel_videos", "recorded_at",
            ]
            if c in latest.columns
        ]

        st.dataframe(
            latest[cols].rename(
                columns={
                    "channel_name": "Creator",
                    "subscriber_count": "Subscribers",
                    "total_channel_views": "Lifetime views",
                    "total_channel_videos": "Videos",
                    "recorded_at": "Last snapshot",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Export snapshot history overview",
            data=latest.to_csv(index=False).encode("utf-8-sig"),
            file_name="latest_creator_snapshots.csv",
            mime="text/csv",
        )

        st.caption(
            f"Tracking began: {safe_text(tracking.get('first_recorded_at'), 'Not recorded')}"
        )

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer-text">
      Creator Intelligence Pro · YouTube-only creator analytics · Streamlit · Plotly · SQLite<br>
      Public-data shortlist heuristic only. No guarantee of audience fit, sales or campaign ROI.
    </div>
    """,
    unsafe_allow_html=True,
)