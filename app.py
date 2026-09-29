# ============================================================
# AI INFLUENCER ANALYSIS DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np

from textblob import TextBlob


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Influencer Analysis",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("influencer.csv")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


df = load_data()


# ============================================================
# CLEAN DATA
# ============================================================

numeric_columns = [
    "followers",
    "following",
    "avg_likes",
    "avg_comments",
    "posts"
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# ENGAGEMENT CALCULATION
# ============================================================

df["total_engagement"] = (
    df["avg_likes"]
    + df["avg_comments"]
)


df["engagement_rate"] = (
    df["total_engagement"]
    / df["followers"].replace(0, np.nan)
) * 100


df["engagement_rate"] = (
    df["engagement_rate"]
    .fillna(0)
)


# ============================================================
# FOLLOWER / FOLLOWING RATIO
# ============================================================

df["follower_following_ratio"] = (
    df["followers"]
    / df["following"].replace(0, np.nan)
)


df["follower_following_ratio"] = (
    df["follower_following_ratio"]
    .fillna(0)
)


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

def analyze_sentiment(text):

    try:

        polarity = TextBlob(
            str(text)
        ).sentiment.polarity

        if polarity > 0.1:

            return "Positive"

        elif polarity < -0.1:

            return "Negative"

        else:

            return "Neutral"

    except:

        return "Neutral"


df["sentiment"] = (
    df["caption"]
    .apply(analyze_sentiment)
)


# ============================================================
# SENTIMENT SCORE
# ============================================================

sentiment_map = {
    "Positive": 100,
    "Neutral": 50,
    "Negative": 0
}


df["sentiment_score"] = (
    df["sentiment"]
    .map(sentiment_map)
    .fillna(50)
)


# ============================================================
# VERIFIED SCORE
# ============================================================

def verified_score(value):

    value = str(value).lower().strip()

    if value in [
        "true",
        "yes",
        "1",
        "verified"
    ]:

        return 100

    return 0


df["verified_score"] = (
    df["verified"]
    .apply(verified_score)
)


# ============================================================
# SUITABILITY SCORE
# ============================================================

def suitability_score(value):

    value = str(value).lower().strip()

    if value in [
        "true",
        "yes",
        "1",
        "suitable"
    ]:

        return 100

    return 0


df["suitability_score"] = (
    df["suitable"]
    .apply(suitability_score)
)


# ============================================================
# ENGAGEMENT SCORE
# ============================================================

df["engagement_score"] = (
    df["engagement_rate"]
    .clip(0, 20)
    / 20
) * 100


# ============================================================
# INFLUENCER PERFORMANCE SCORE
# ============================================================

df["influencer_score"] = (

    df["engagement_score"] * 0.40

    + df["sentiment_score"] * 0.20

    + df["verified_score"] * 0.20

    + df["suitability_score"] * 0.20
)


df["influencer_score"] = (
    df["influencer_score"]
    .clip(0, 100)
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 AI Influencer Analysis")

st.markdown(
    "### Social Media Influencer Performance & Marketing Intelligence"
)

st.write(
    "Analyze influencer engagement, content sentiment, "
    "verification status and campaign suitability."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔍 Dashboard Filters")


# Platform filter

platforms = sorted(
    df["platform"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_platform = st.sidebar.selectbox(
    "Select Platform",
    ["All Platforms"] + platforms
)


if selected_platform == "All Platforms":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["platform"].astype(str)
        == selected_platform
    ].copy()


# ============================================================
# SEARCH
# ============================================================

search = st.sidebar.text_input(
    "Search Influencer"
)


if search:

    filtered_df = filtered_df[
        filtered_df["username"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📊 Key Performance Indicators")


col1, col2, col3, col4 = st.columns(4)


# Total influencers

with col1:

    st.metric(
        "Total Influencers",
        len(filtered_df)
    )


# Average engagement

with col2:

    avg_engagement = (
        filtered_df["engagement_rate"]
        .mean()
    )

    st.metric(
        "Avg Engagement",
        f"{avg_engagement:.2f}%"
    )


# Average followers

with col3:

    avg_followers = (
        filtered_df["followers"]
        .mean()
    )

    st.metric(
        "Avg Followers",
        f"{avg_followers:,.0f}"
    )


# Average score

with col4:

    avg_score = (
        filtered_df["influencer_score"]
        .mean()
    )

    st.metric(
        "Avg Influencer Score",
        f"{avg_score:.2f}"
    )


st.divider()


# ============================================================
# PERFORMANCE TABLE
# ============================================================

st.subheader("📋 Influencer Performance")


performance_table = filtered_df[
    [
        "username",
        "platform",
        "followers",
        "avg_likes",
        "avg_comments",
        "engagement_rate",
        "verified",
        "sentiment",
        "suitable",
        "influencer_score"
    ]
].copy()


performance_table.rename(
    columns={
        "username": "Influencer",
        "platform": "Platform",
        "followers": "Followers",
        "avg_likes": "Avg Likes",
        "avg_comments": "Avg Comments",
        "engagement_rate": "Engagement %",
        "verified": "Verified",
        "sentiment": "Sentiment",
        "suitable": "Suitable",
        "influencer_score": "Score"
    },
    inplace=True
)


performance_table["Engagement %"] = (
    performance_table["Engagement %"]
    .round(2)
)


performance_table["Score"] = (
    performance_table["Score"]
    .round(2)
)


st.dataframe(
    performance_table,
    width="stretch",
    hide_index=True
)


st.divider()


# ============================================================
# INFLUENCER SCORE CHART
# ============================================================

st.subheader("🏆 Influencer Performance Score")


score_df = (
    filtered_df
    .sort_values(
        "influencer_score",
        ascending=False
    )
    .head(10)
)


score_chart = (
    score_df
    .set_index("username")
    ["influencer_score"]
)


st.bar_chart(
    score_chart,
    width="stretch"
)


st.divider()


# ============================================================
# ENGAGEMENT CHART
# ============================================================

st.subheader("📈 Engagement Rate Analysis")


engagement_df = (
    filtered_df
    .sort_values(
        "engagement_rate",
        ascending=False
    )
    .head(10)
)


engagement_chart = (
    engagement_df
    .set_index("username")
    ["engagement_rate"]
)


st.bar_chart(
    engagement_chart,
    width="stretch"
)


st.divider()


# ============================================================
# FOLLOWER CHART
# ============================================================

st.subheader("👥 Follower Analysis")


follower_df = (
    filtered_df
    .sort_values(
        "followers",
        ascending=False
    )
    .head(10)
)


follower_chart = (
    follower_df
    .set_index("username")
    ["followers"]
)


st.bar_chart(
    follower_chart,
    width="stretch"
)


st.divider()


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

st.subheader("💬 Content Sentiment")


sentiment_counts = (
    filtered_df["sentiment"]
    .value_counts()
)


st.bar_chart(
    sentiment_counts,
    width="stretch"
)


st.divider()


# ============================================================
# PLATFORM ANALYSIS
# ============================================================

st.subheader("🌐 Platform Distribution")


platform_counts = (
    filtered_df["platform"]
    .value_counts()
)


st.bar_chart(
    platform_counts,
    width="stretch"
)


st.divider()


# ============================================================
# SUITABILITY ANALYSIS
# ============================================================

st.subheader("🎯 Campaign Suitability")


suitable_counts = (
    filtered_df["suitable"]
    .astype(str)
    .value_counts()
)


st.bar_chart(
    suitable_counts,
    width="stretch"
)


st.divider()


# ============================================================
# INDIVIDUAL INFLUENCER
# ============================================================

st.subheader("🔎 Individual Influencer Analysis")


if len(filtered_df) > 0:

    influencer_list = (
        filtered_df["username"]
        .astype(str)
        .tolist()
    )


    selected_influencer = st.selectbox(
        "Select Influencer",
        influencer_list
    )


    selected_data = filtered_df[
        filtered_df["username"].astype(str)
        == selected_influencer
    ].iloc[0]


    st.markdown(
        f"## 👤 {selected_influencer}"
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Followers",
            f"{int(selected_data['followers']):,}"
        )


    with c2:

        st.metric(
            "Engagement",
            f"{selected_data['engagement_rate']:.2f}%"
        )


    with c3:

        st.metric(
            "Avg Likes",
            f"{int(selected_data['avg_likes']):,}"
        )


    with c4:

        st.metric(
            "Influencer Score",
            f"{selected_data['influencer_score']:.2f}"
        )


    st.write("### Influencer Details")


    details = pd.DataFrame(
        {
            "Metric": [
                "Platform",
                "Followers",
                "Following",
                "Average Likes",
                "Average Comments",
                "Posts",
                "Verified",
                "Sentiment",
                "Campaign Suitable",
                "Engagement Rate",
                "Influencer Score"
            ],

            "Value": [
                selected_data["platform"],
                int(selected_data["followers"]),
                int(selected_data["following"]),
                int(selected_data["avg_likes"]),
                int(selected_data["avg_comments"]),
                int(selected_data["posts"]),
                selected_data["verified"],
                selected_data["sentiment"],
                selected_data["suitable"],
                f"{selected_data['engagement_rate']:.2f}%",
                f"{selected_data['influencer_score']:.2f}"
            ]
        }
    )


    st.dataframe(
        details,
        width="stretch",
        hide_index=True
    )


    st.write("### Caption")

    st.info(
        str(selected_data["caption"])
    )


# ============================================================
# ROI INFORMATION
# ============================================================

st.divider()

st.subheader("💰 Campaign ROI")


st.info(
    "ROI is not calculated in this version because the "
    "dataset does not contain campaign cost, conversions "
    "or revenue data. Adding these fields would allow "
    "actual campaign ROI analysis."
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Influencer Analysis | "
    "Python • Pandas • TextBlob • Streamlit"
)

st.caption(
    "Influencer Score is a project-defined analytical score "
    "based on engagement, sentiment, verification and "
    "campaign suitability."
)