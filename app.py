import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from youtube_api import search_youtube_influencers, YouTubeAPIError
from influencers import rank_influencers
from database import (
    initialize_database,
    save_channel_snapshot,
    get_channel_history,
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Creator Intelligence Pro",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Discover Influencers",
    "Creator Profile",
    "Dashboard Overview",
]

# =========================================================
# PREMIUM DARK THEME
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    .stApp {
        background: #0B1020;
        color: #E8ECF8;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 16, 32, 0.92);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #0E1426;
        border-right: 1px solid #27314D;
    }

    section[data-testid="stSidebar"] * {
        color: #E8ECF8;
    }

    .brand-mark {
        color: #22D3EE;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero {
        background: linear-gradient(
            125deg,
            #171D35 0%,
            #11182C 55%,
            #21133D 100%
        );
        border: 1px solid #303954;
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
    }

    .eyebrow {
        color: #22D3EE;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero h1 {
        font-size: clamp(30px, 4vw, 44px);
        font-weight: 800;
        color: #F8FAFF;
        letter-spacing: -1.5px;
        line-height: 1.12;
        margin: 0 0 13px 0;
    }

    .hero p {
        font-size: 15px;
        color: #AAB5D0;
        line-height: 1.7;
        max-width: 760px;
        margin: 0;
    }

    .section-heading {
        font-size: 23px;
        font-weight: 750;
        color: #F8FAFF;
        margin: 12px 0 5px;
    }

    .muted {
        color: #9AA7C4;
        font-size: 13px;
    }

    div[data-testid="stMetric"] {
        background: #151C30;
        border: 1px solid #2A3552;
        border-radius: 16px;
        padding: 17px;
    }

    div[data-testid="stMetricLabel"] {
        color: #AAB5D0;
        font-size: 12px;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFF;
        font-size: 25px;
        font-weight: 750;
    }

    div.stButton > button,
    div.stFormSubmitButton > button,
    div.stLinkButton > a {
        border-radius: 11px;
        font-weight: 650;
        min-height: 42px;
        transition: all 0.15s ease;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #8B5CF6;
        color: #FFFFFF;
        border: 1px solid #8B5CF6;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: #7C3AED;
        border-color: #7C3AED;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #12192B;
        border-color: #2A3552 !important;
        border-radius: 17px;
    }

    input, textarea {
        border-radius: 10px !important;
    }

    hr {
        border-color: #27314D;
    }

    a {
        color: #22D3EE;
    }

    .footer-text {
        color: #7F8CAB;
        font-size: 12px;
        text-align: center;
        padding: 20px 0 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_number(value):
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
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
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return f"{float(value):.1f}/100"

    except (TypeError, ValueError):
        return "N/A"


def format_percent(value):
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return f"{float(value):.2f}%"

    except (TypeError, ValueError):
        return "N/A"


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


def dark_chart(fig, height=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12192B",
        plot_bgcolor="#12192B",
        font=dict(
            family="Inter, Arial",
            color="#E8ECF8",
            size=12,
        ),
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis=dict(
            gridcolor="#27314D",
            zerolinecolor="#27314D",
        ),
        yaxis=dict(
            gridcolor="#27314D",
            zerolinecolor="#27314D",
        ),
    )

    if height:
        fig.update_layout(height=height)

    return fig


def select_creator(channel_id):
    st.session_state["selected_channel_id"] = channel_id
    st.session_state["page"] = "Creator Profile"


# =========================================================
# CREATOR RESULT CARD
# =========================================================

def show_creator_card(creator, videos):
    channel_id = safe_text(creator.get("channel_id"), "")
    name = safe_text(creator.get("channel_name"), "YouTube creator")

    with st.container(border=True):
        col_profile, col_score = st.columns([4, 1])

        with col_profile:
            st.markdown(
                f"### {creator.get('rank', '-')}. {name}"
            )

            st.caption(
                safe_text(
                    creator.get("description"),
                    "No public channel description available.",
                )[:240]
            )

        with col_score:
            st.metric(
                "Suitability",
                format_score(creator.get("suitability_score")),
            )

        a, b, c, d = st.columns(4)

        a.metric(
            "Subscribers",
            format_number(creator.get("subscriber_count")),
        )

        b.metric(
            "Average matched views",
            format_number(
                creator.get("average_matched_video_views")
            ),
        )

        c.metric(
            "Content match",
            format_score(creator.get("content_match_pct")),
        )

        d.metric(
            "Interactions / views",
            format_percent(
                creator.get("public_interactions_per_view_pct")
            ),
        )

        st.caption(
            safe_text(
                creator.get("recommendation_reason"),
                "Review the creator's content before contacting them.",
            )
        )

        col_button, col_youtube = st.columns([2, 1])

        with col_button:
            if channel_id:
                st.button(
                    "View full creator analysis →",
                    key=f"open_profile_{channel_id}",
                    use_container_width=True,
                    on_click=select_creator,
                    args=(channel_id,),
                )

        with col_youtube:
            channel_url = safe_text(
                creator.get("channel_url"), ""
            )

            if channel_url:
                st.link_button(
                    "Open YouTube ↗",
                    channel_url,
                    use_container_width=True,
                )

        if (
            videos is not None
            and not videos.empty
            and "channel_id" in videos.columns
            and channel_id
        ):
            creator_videos = videos[
                videos["channel_id"].astype(str) == channel_id
            ]

            if not creator_videos.empty:
                with st.expander("View matching videos"):
                    for _, video in creator_videos.head(5).iterrows():
                        st.markdown(
                            f"**{safe_text(video.get('video_title'), 'YouTube video')}**"
                        )

                        v1, v2, v3 = st.columns(3)

                        v1.caption(
                            f"Views: {format_number(video.get('views'))}"
                        )

                        v2.caption(
                            f"Likes: {format_number(video.get('likes'))}"
                        )

                        v3.caption(
                            f"Comments: {format_number(video.get('comments'))}"
                        )

                        video_url = safe_text(
                            video.get("video_url"), ""
                        )

                        if video_url:
                            st.markdown(
                                f"[Watch video ↗]({video_url})"
                            )

                        st.divider()


# =========================================================
# DATABASE AND SESSION STATE
# =========================================================

try:
    initialize_database()
except Exception as exc:
    st.error(f"Could not initialize the history database: {exc}")

defaults = {
    "page": "Discover Influencers",
    "ranked_creators": pd.DataFrame(),
    "matched_videos": pd.DataFrame(),
    "searched_product": "",
    "search_timestamp": "",
    "selected_channel_id": "",
}

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Prevent an old session from trying to open the deleted About page.
if st.session_state["page"] not in PAGES:
    st.session_state["page"] = "Discover Influencers"


# =========================================================
# SIDEBAR: ONLY THREE PAGES
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand-mark">CREATOR INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )

    st.markdown("## Creator Intelligence Pro")
    st.caption("YouTube Creator Analytics")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        PAGES,
        key="page",
    )

    st.divider()

    st.markdown("**PLATFORM**")
    st.write("▶ YouTube")

    st.caption(
        "Public YouTube data. Results depend on API availability and quota."
    )


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">CREATOR INTELLIGENCE PLATFORM</div>
        <h1>Discover creators.<br>Understand their growth.</h1>
        <p>
            Find creators for your product, compare their public
            performance, and explore individual creator analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DISCOVER INFLUENCERS
# =========================================================

if page == "Discover Influencers":

    st.markdown(
        '<div class="section-heading">Discover creators</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="muted">Search using a product, brand, or campaign topic.</p>',
        unsafe_allow_html=True,
    )

    with st.form("youtube_product_search"):
        product = st.text_input(
            "Product or brand",
            placeholder="e.g. wireless earbuds, skincare, smartphones",
        )

        col_search, col_results = st.columns([3, 1])

        with col_results:
            max_results = st.selectbox(
                "Videos to search",
                [10, 20, 25, 50],
                index=2,
            )

        with col_search:
            st.caption(
                "Finds product-related videos and analyzes the "
                "channels returned by YouTube."
            )

        submitted = st.form_submit_button(
            "Search YouTube creators →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not product.strip():
            st.warning("Please enter a product or brand first.")

        else:
            try:
                with st.spinner(
                    "Searching YouTube and analyzing creators..."
                ):
                    channels, videos = search_youtube_influencers(
                        product=product.strip(),
                        max_results=max_results,
                    )

                    ranked = rank_influencers(
                        product=product.strip(),
                        channels_df=channels,
                        videos_df=videos,
                    )

                st.session_state["ranked_creators"] = ranked
                st.session_state["matched_videos"] = videos
                st.session_state["searched_product"] = product.strip()
                st.session_state["search_timestamp"] = (
                    datetime.now().strftime("%d %b %Y, %I:%M %p")
                )

                # Store real public-statistics snapshots.
                snapshot_errors = 0

                for _, snapshot in ranked.iterrows():
                    try:
                        save_channel_snapshot(snapshot)
                    except Exception:
                        snapshot_errors += 1

                if snapshot_errors:
                    st.warning(
                        f"{snapshot_errors} creator snapshot(s) could not "
                        "be saved. Check database.py if the issue continues."
                    )

            except YouTubeAPIError as exc:
                st.error("YouTube API request failed.")
                st.exception(exc)

                st.info(
                    "Check that YouTube Data API v3 is enabled, "
                    "the API key is correct, and quota is available."
                )

            except Exception as exc:
                st.error("Something went wrong while analyzing creators.")
                st.exception(exc)

    ranked = st.session_state["ranked_creators"]
    videos = st.session_state["matched_videos"]
    searched_product = st.session_state["searched_product"]

    if searched_product:
        st.divider()
        st.markdown(f"### Results for: {searched_product}")

        if st.session_state["search_timestamp"]:
            st.caption(
                f"Retrieved at {st.session_state['search_timestamp']} · YouTube API"
            )

        if ranked.empty:
            st.info(
                "No matching channels were returned. Try a broader product term."
            )

        else:
            subs = pd.to_numeric(
                ranked.get("subscriber_count", pd.Series(dtype=float)),
                errors="coerce",
            ).dropna()

            views = pd.to_numeric(
                ranked.get(
                    "average_matched_video_views",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            ).dropna()

            scores = pd.to_numeric(
                ranked.get("suitability_score", pd.Series(dtype=float)),
                errors="coerce",
            ).dropna()

            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Creators found", f"{len(ranked):,}")

            m2.metric(
                "Median subscribers",
                format_number(subs.median()) if not subs.empty else "N/A",
            )

            m3.metric(
                "Average matched views",
                format_number(views.mean()) if not views.empty else "N/A",
            )

            m4.metric(
                "Average suitability",
                format_score(scores.mean()) if not scores.empty else "N/A",
            )

            st.divider()

            chart_col, info_col = st.columns([1.5, 1])

            with chart_col:
                st.markdown("#### Top creator matches")

                chart_df = ranked.head(10).copy()

                if "suitability_score" in chart_df.columns:
                    chart_df["suitability_score"] = pd.to_numeric(
                        chart_df["suitability_score"],
                        errors="coerce",
                    )

                    chart_df = chart_df.dropna(
                        subset=["suitability_score"]
                    ).sort_values("suitability_score")

                if not chart_df.empty:
                    fig = px.bar(
                        chart_df,
                        x="suitability_score",
                        y="channel_name",
                        orientation="h",
                        labels={
                            "suitability_score": "Suitability score / 100",
                            "channel_name": "",
                        },
                    )

                    fig.update_traces(
                        marker_color="#8B5CF6",
                        hovertemplate=(
                            "%{y}<br>Suitability: %{x:.1f}/100"
                            "<extra></extra>"
                        ),
                    )

                    fig.update_layout(
                        xaxis_range=[0, 100],
                        height=max(300, 40 * len(chart_df)),
                    )

                    st.plotly_chart(
                        dark_chart(fig),
                        use_container_width=True,
                    )

            with info_col:
                st.markdown("#### Creator comparison")

                st.write(
                    "**Content match** compares your product with "
                    "available channel and video text."
                )

                st.write(
                    "**Performance** compares public view, subscriber "
                    "and interaction indicators."
                )

                st.write(
                    "**Suitability** is a relative score to help you "
                    "shortlist creators."
                )

                st.info(
                    "The score does not guarantee audience fit, sales "
                    "or campaign ROI."
                )

            st.divider()
            st.markdown("#### Ranked influencer shortlist")

            for _, creator in ranked.iterrows():
                show_creator_card(creator, videos)

            with st.expander("View complete results table"):
                columns = [
                    c for c in [
                        "rank",
                        "channel_name",
                        "subscriber_count",
                        "average_matched_video_views",
                        "public_interactions_per_view_pct",
                        "content_match_pct",
                        "suitability_score",
                    ]
                    if c in ranked.columns
                ]

                display_df = ranked[columns].rename(
                    columns={
                        "rank": "Rank",
                        "channel_name": "Channel",
                        "subscriber_count": "Subscribers",
                        "average_matched_video_views": "Average matched views",
                        "public_interactions_per_view_pct": "Interactions / views (%)",
                        "content_match_pct": "Content match",
                        "suitability_score": "Suitability",
                    }
                )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                )


# =========================================================
# INDIVIDUAL CREATOR PROFILE
# =========================================================

elif page == "Creator Profile":

    ranked = st.session_state["ranked_creators"]
    videos = st.session_state["matched_videos"]
    selected_id = str(
        st.session_state.get("selected_channel_id", "")
    )

    st.markdown(
        '<div class="section-heading">Individual creator intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Explore channel statistics, video performance and saved growth history."
    )

    if ranked.empty:
        st.info(
            "Search for a product first, then click "
            "'View full creator analysis' on a creator card."
        )

    else:
        chosen = (
            ranked[ranked["channel_id"].astype(str) == selected_id]
            if selected_id and "channel_id" in ranked.columns
            else pd.DataFrame()
        )

        if chosen.empty:
            st.info("Select a creator to open their full profile.")

            creator_options = {
                (
                    f"{safe_text(row.get('channel_name'), 'Creator')} "
                    f"({safe_text(row.get('channel_id'), '')})"
                ): str(row.get("channel_id", ""))
                for _, row in ranked.iterrows()
            }

            selected_label = st.selectbox(
                "Choose a creator",
                list(creator_options.keys()),
            )

            selected_option_id = creator_options.get(selected_label, "")

            if selected_option_id:
                st.button(
                    "Open selected profile →",
                    type="primary",
                    on_click=select_creator,
                    args=(selected_option_id,),
                )

        else:
            creator = chosen.iloc[0]
            name = safe_text(
                creator.get("channel_name"),
                "YouTube creator",
            )

            st.markdown(f"## {name}")

            st.caption(
                safe_text(
                    creator.get("description"),
                    "No public channel description available.",
                )
            )

            channel_url = safe_text(
                creator.get("channel_url"), ""
            )

            if channel_url:
                st.link_button("Open YouTube channel ↗", channel_url)

            # ---------------------------------------------
            # PROFILE METRICS
            # ---------------------------------------------

            a, b, c, d = st.columns(4)

            a.metric(
                "Subscribers",
                format_number(creator.get("subscriber_count")),
            )

            b.metric(
                "Lifetime channel views",
                format_number(creator.get("total_channel_views")),
            )

            c.metric(
                "Channel videos",
                format_number(creator.get("total_channel_videos")),
            )

            d.metric(
                "AI suitability",
                format_score(creator.get("suitability_score")),
            )

            # ---------------------------------------------
            # HISTORICAL GROWTH
            # ---------------------------------------------

            st.markdown("### Growth history")

            period = st.selectbox(
                "Time period",
                [
                    "Daily",
                    "Weekly",
                    "Monthly",
                    "Yearly",
                    "All saved history",
                ],
                index=4,
                key="profile_period",
            )

            try:
                history = pd.DataFrame(
                    get_channel_history(selected_id)
                )
            except Exception as exc:
                history = pd.DataFrame()
                st.warning(f"Could not read saved history: {exc}")

            if history.empty:
                st.info(
                    "No snapshots have been saved for this creator yet. "
                    "Run searches over time to build the history."
                )

            else:
                history["recorded_at"] = pd.to_datetime(
                    history["recorded_at"],
                    errors="coerce",
                    utc=True,
                )

                history = history.dropna(
                    subset=["recorded_at"]
                ).sort_values("recorded_at")

                now = pd.Timestamp.now(tz="UTC")

                period_windows = {
                    "Daily": pd.Timedelta(days=1),
                    "Weekly": pd.Timedelta(days=7),
                    "Monthly": pd.Timedelta(days=30),
                    "Yearly": pd.Timedelta(days=365),
                }

                if period in period_windows:
                    history = history[
                        history["recorded_at"]
                        >= now - period_windows[period]
                    ]

                metric_map = {
                    "Subscribers": "subscriber_count",
                    "Lifetime channel views": "total_channel_views",
                    "Total channel videos": "total_channel_videos",
                    "Average matched video views": "average_matched_video_views",
                    "Public interactions / views (%)": "public_interactions_per_view_pct",
                }

                metric_label = st.selectbox(
                    "Graph metric",
                    list(metric_map.keys()),
                    key="profile_metric",
                )

                metric_col = metric_map[metric_label]

                if (
                    history.empty
                    or metric_col not in history.columns
                    or pd.to_numeric(
                        history[metric_col],
                        errors="coerce",
                    ).notna().sum() == 0
                ):
                    st.info(
                        "No snapshots exist for this metric in the selected "
                        "period. More historical data is needed."
                    )

                else:
                    history[metric_col] = pd.to_numeric(
                        history[metric_col],
                        errors="coerce",
                    )

                    fig = px.line(
                        history,
                        x="recorded_at",
                        y=metric_col,
                        markers=True,
                        title=f"{metric_label} over time",
                    )

                    fig.update_traces(
                        line_color="#22D3EE",
                        marker_color="#8B5CF6",
                        line_width=3,
                    )

                    fig.update_layout(
                        xaxis_title="Snapshot date (UTC)",
                        yaxis_title=metric_label,
                    )

                    st.plotly_chart(
                        dark_chart(fig),
                        use_container_width=True,
                    )

                    values = history[metric_col].dropna()

                    if not values.empty:
                        first = values.iloc[0]
                        latest = values.iloc[-1]
                        delta = latest - first

                        percent_change = (
                            delta / first * 100
                            if first else None
                        )

                        g1, g2, g3 = st.columns(3)

                        g1.metric(
                            "First saved value",
                            format_number(first),
                        )

                        g2.metric(
                            "Latest saved value",
                            format_number(latest),
                            delta=format_number(delta),
                        )

                        g3.metric(
                            "Change since first snapshot",
                            (
                                f"{percent_change:+.2f}%"
                                if percent_change is not None
                                else "N/A"
                            ),
                        )

                st.caption(
                    "Growth is measured from real snapshots collected by "
                    "this application. Missing historical data is not invented."
                )

            # ---------------------------------------------
            # VIDEO PERFORMANCE
            # ---------------------------------------------

            st.markdown("### Video performance")

            if (
                not videos.empty
                and "channel_id" in videos.columns
            ):
                creator_videos = videos[
                    videos["channel_id"].astype(str) == selected_id
                ].copy()
            else:
                creator_videos = pd.DataFrame()

            if creator_videos.empty:
                st.info(
                    "No matching videos are available for this creator "
                    "in the current search."
                )

            else:
                for col in [
                    "views",
                    "likes",
                    "comments",
                    "engagement_rate_pct",
                ]:
                    if col in creator_videos.columns:
                        creator_videos[col] = pd.to_numeric(
                            creator_videos[col],
                            errors="coerce",
                        )

                if "views" in creator_videos.columns:
                    top_videos = (
                        creator_videos.dropna(subset=["views"])
                        .sort_values("views", ascending=True)
                        .tail(10)
                    )

                    if not top_videos.empty:
                        fig = px.bar(
                            top_videos,
                            x="views",
                            y="video_title",
                            orientation="h",
                            title="Top matched videos by views",
                        )

                        fig.update_traces(
                            marker_color="#8B5CF6"
                        )

                        st.plotly_chart(
                            dark_chart(
                                fig,
                                height=max(350, len(top_videos) * 35),
                            ),
                            use_container_width=True,
                        )

                display_cols = [
                    c for c in [
                        "video_title",
                        "published_at",
                        "views",
                        "likes",
                        "comments",
                        "engagement_rate_pct",
                        "video_url",
                    ]
                    if c in creator_videos.columns
                ]

                st.dataframe(
                    creator_videos[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )

            # ---------------------------------------------
            # AI BRAND FIT
            # ---------------------------------------------

            st.markdown("### AI brand-fit analysis")

            x, y, z = st.columns(3)

            x.metric(
                "Content match",
                format_score(creator.get("content_match_pct")),
            )

            y.metric(
                "Performance score",
                format_score(creator.get("performance_score")),
            )

            z.metric(
                "Public interaction rate",
                format_percent(
                    creator.get("public_interactions_per_view_pct")
                ),
            )

            st.write(
                safe_text(
                    creator.get("recommendation_reason"),
                    "Review the creator's content before deciding on a collaboration.",
                )
            )

            st.caption(
                "Suitability is a heuristic, not a guarantee of audience fit, "
                "sales or campaign ROI. Private audience demographics require "
                "creator-authorized analytics access."
            )

            st.button(
                "← Back to creator discovery",
                on_click=lambda: st.session_state.update(
                    {"page": "Discover Influencers"}
                ),
            )


# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

elif page == "Dashboard Overview":

    st.markdown(
        '<div class="section-heading">Dashboard overview</div>',
        unsafe_allow_html=True,
    )

    ranked = st.session_state["ranked_creators"]

    if ranked.empty:
        st.info(
            "Search for a product in Discover Influencers "
            "to populate the dashboard."
        )

    else:
        scores = pd.to_numeric(
            ranked.get(
                "suitability_score",
                pd.Series(dtype=float),
            ),
            errors="coerce",
        ).dropna()

        views = pd.to_numeric(
            ranked.get(
                "average_matched_video_views",
                pd.Series(dtype=float),
            ),
            errors="coerce",
        ).dropna()

        subs = pd.to_numeric(
            ranked.get(
                "subscriber_count",
                pd.Series(dtype=float),
            ),
            errors="coerce",
        ).dropna()

        a, b, c, d = st.columns(4)

        a.metric("Creators analyzed", len(ranked))

        b.metric(
            "Average suitability",
            format_score(scores.mean()) if not scores.empty else "N/A",
        )

        c.metric(
            "Median subscribers",
            format_number(subs.median()) if not subs.empty else "N/A",
        )

        d.metric(
            "Average matched views",
            format_number(views.mean()) if not views.empty else "N/A",
        )

        st.markdown(
            f"#### Latest product: {st.session_state['searched_product']}"
        )

        columns = [
            c for c in [
                "rank",
                "channel_name",
                "subscriber_count",
                "content_match_pct",
                "suitability_score",
            ]
            if c in ranked.columns
        ]

        display_df = ranked[columns].rename(
            columns={
                "rank": "Rank",
                "channel_name": "YouTube channel",
                "subscriber_count": "Subscribers",
                "content_match_pct": "Content match",
                "suitability_score": "Suitability",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Creator suitability comparison")

        if (
            "channel_name" in ranked.columns
            and "suitability_score" in ranked.columns
        ):
            chart_df = ranked.copy()

            chart_df["suitability_score"] = pd.to_numeric(
                chart_df["suitability_score"],
                errors="coerce",
            )

            chart_df = chart_df.dropna(
                subset=["suitability_score"]
            ).sort_values("suitability_score", ascending=True).tail(15)

            if not chart_df.empty:
                fig = px.bar(
                    chart_df,
                    x="suitability_score",
                    y="channel_name",
                    orientation="h",
                    labels={
                        "suitability_score": "Suitability / 100",
                        "channel_name": "",
                    },
                )

                fig.update_traces(marker_color="#22D3EE")

                st.plotly_chart(
                    dark_chart(
                        fig,
                        height=max(350, len(chart_df) * 35),
                    ),
                    use_container_width=True,
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-text">
        Creator Intelligence Pro · YouTube Creator Analytics
        · Python · Streamlit · Plotly
    </div>
    """,
    unsafe_allow_html=True,
)