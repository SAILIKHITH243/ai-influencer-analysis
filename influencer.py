# ============================================================
# AI INFLUENCER ANALYSIS & MARKETING INTELLIGENCE
# ============================================================

import os
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from textblob import TextBlob


# ============================================================
# 1. LOAD DATA
# ============================================================

def load_data():

    file_path = "influencer.csv"

    print("\n========================================")
    print("       AI INFLUENCER ANALYSIS")
    print("========================================")

    print("\nLoading dataset...")

    if not os.path.exists(file_path):

        print("\nERROR: influencer.csv not found!")
        print("Make sure influencer.csv is in the same folder.")
        return None

    df = pd.read_csv(file_path)

    print("Dataset loaded successfully!")
    print("Number of records:", len(df))
    print("Number of columns:", len(df.columns))

    return df


# ============================================================
# 2. CHECK DATASET
# ============================================================

def check_columns(df):

    required_columns = [
        "username",
        "platform",
        "followers",
        "following",
        "avg_likes",
        "avg_comments",
        "posts",
        "verified",
        "caption",
        "suitable"
    ]

    missing_columns = []

    for column in required_columns:

        if column not in df.columns:
            missing_columns.append(column)

    if len(missing_columns) > 0:

        print("\nERROR: Missing columns:")
        print(missing_columns)

        print("\nRequired columns:")
        print(required_columns)

        return False

    print("\nAll required columns are present.")

    return True


# ============================================================
# 3. CLEAN DATA
# ============================================================

def clean_data(df):

    print("\nCleaning data...")

    # Remove duplicate rows
    df = df.drop_duplicates()

    numeric_columns = [
        "followers",
        "following",
        "avg_likes",
        "avg_comments",
        "posts",
        "verified",
        "suitable"
    ]

    # Convert numeric columns
    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Fill missing numeric values
    for column in numeric_columns:

        df[column] = df[column].fillna(0)

    # Remove negative values
    for column in numeric_columns:

        if column not in ["verified", "suitable"]:

            df[column] = df[column].clip(lower=0)

    # Clean caption
    df["caption"] = (
        df["caption"]
        .fillna("")
        .astype(str)
    )

    print("Data cleaning completed.")

    return df


# ============================================================
# 4. SENTIMENT ANALYSIS
# ============================================================

def analyze_sentiment(df):

    print("\nPerforming NLP sentiment analysis...")

    def get_sentiment(text):

        polarity = TextBlob(text).sentiment.polarity

        if polarity > 0.1:

            return "Positive"

        elif polarity < -0.1:

            return "Negative"

        else:

            return "Neutral"


    def get_polarity(text):

        return TextBlob(text).sentiment.polarity


    # Sentiment category
    df["sentiment"] = df["caption"].apply(
        get_sentiment
    )


    # Sentiment polarity
    df["sentiment_polarity"] = df["caption"].apply(
        get_polarity
    )


    print("Sentiment analysis completed.")

    return df


# ============================================================
# 5. FEATURE ENGINEERING
# ============================================================

def create_features(df):

    print("\nCreating analytical features...")

    # --------------------------------------------------------
    # Total Engagement
    # --------------------------------------------------------

    df["total_engagement"] = (
        df["avg_likes"]
        + df["avg_comments"]
    )


    # --------------------------------------------------------
    # Engagement Rate
    # --------------------------------------------------------

    df["engagement_rate"] = (
        df["total_engagement"]
        / df["followers"].replace(0, 1)
    ) * 100


    # --------------------------------------------------------
    # Average Engagement Per Post
    # --------------------------------------------------------

    df["engagement_per_post"] = (
        df["total_engagement"]
        / df["posts"].replace(0, 1)
    )


    # --------------------------------------------------------
    # Follower / Following Ratio
    # --------------------------------------------------------

    df["follower_following_ratio"] = (
        df["followers"]
        / df["following"].replace(0, 1)
    )


    # --------------------------------------------------------
    # Estimated Reach
    # --------------------------------------------------------
    # This is an analytical estimate because the dataset
    # does not contain actual reach data.

    df["estimated_reach"] = (
        df["followers"]
        * (df["engagement_rate"] / 100)
    )


    # --------------------------------------------------------
    # Reach Rate
    # --------------------------------------------------------

    df["reach_rate"] = (
        df["estimated_reach"]
        / df["followers"].replace(0, 1)
    ) * 100


    print("Feature engineering completed.")

    return df


# ============================================================
# 6. AUTHENTICITY SCORE
# ============================================================

def calculate_authenticity(df):

    print("\nCalculating authenticity score...")

    # Start with 50 points
    df["authenticity_score"] = 50.0


    # Verified account bonus
    df.loc[
        df["verified"] == 1,
        "authenticity_score"
    ] += 20


    # Good follower/following ratio
    df.loc[
        df["follower_following_ratio"] >= 10,
        "authenticity_score"
    ] += 15


    # Good engagement
    df.loc[
        df["engagement_rate"] >= 3,
        "authenticity_score"
    ] += 15


    # Negative sentiment penalty
    df.loc[
        df["sentiment"] == "Negative",
        "authenticity_score"
    ] -= 15


    # Keep score between 0 and 100
    df["authenticity_score"] = (
        df["authenticity_score"]
        .clip(0, 100)
    )


    print("Authenticity score calculated.")

    return df


# ============================================================
# 7. INFLUENCER SCORE
# ============================================================

def calculate_influencer_score(df):

    print("\nCalculating influencer score...")

    # --------------------------------------------------------
    # Engagement Score
    # --------------------------------------------------------

    df["engagement_score"] = (
        df["engagement_rate"]
        .clip(0, 10)
        / 10
    ) * 100


    # --------------------------------------------------------
    # Sentiment Score
    # --------------------------------------------------------

    df["sentiment_score"] = (
        (df["sentiment_polarity"] + 1) / 2
    ) * 100


    # --------------------------------------------------------
    # Final Influencer Score
    # --------------------------------------------------------

    df["influencer_score"] = (

        df["engagement_score"] * 0.40

        + df["authenticity_score"] * 0.30

        + df["sentiment_score"] * 0.30
    )


    # Make sure score stays 0-100
    df["influencer_score"] = (
        df["influencer_score"]
        .clip(0, 100)
    )


    print("Influencer score calculated.")

    return df


# ============================================================
# 8. ESTIMATED CAMPAIGN COST
# ============================================================

def calculate_campaign_cost(df):

    print("\nEstimating campaign cost...")

    # This is a project-level estimation.
    # Actual influencer rates vary by platform,
    # niche, audience and campaign.

    df["estimated_campaign_cost"] = (
        df["followers"] * 0.10
    )


    return df


# ============================================================
# 9. ESTIMATED ROI
# ============================================================

def calculate_roi(df):

    print("\nCalculating estimated ROI...")

    # Estimated conversion rate
    conversion_rate = 0.02

    # Estimated value of each conversion
    value_per_conversion = 100


    # Estimated conversions
    df["estimated_conversions"] = (
        df["estimated_reach"]
        * conversion_rate
    )


    # Estimated revenue
    df["estimated_return"] = (
        df["estimated_conversions"]
        * value_per_conversion
    )


    # ROI
    df["roi"] = (

        (
            df["estimated_return"]
            - df["estimated_campaign_cost"]
        )

        / df["estimated_campaign_cost"].replace(0, 1)

    ) * 100


    print("Estimated ROI calculated.")

    return df


# ============================================================
# 10. MACHINE LEARNING
# ============================================================

def train_model(df):

    print("\n========================================")
    print("       MACHINE LEARNING MODEL")
    print("========================================")


    # Features used by ML
    features = [

        "followers",

        "following",

        "avg_likes",

        "avg_comments",

        "posts",

        "verified",

        "engagement_rate",

        "engagement_per_post",

        "follower_following_ratio",

        "sentiment_polarity"

    ]


    X = df[features]

    # Target from existing dataset
    y = df["suitable"]


    print("\nTarget distribution:")

    print(
        y.value_counts()
    )


    # Check if both classes exist
    if y.nunique() < 2:

        print(
            "\nERROR: Suitable column needs both 0 and 1."
        )

        return None, None


    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42,

        stratify=y
    )


    print("\nTraining Random Forest model...")


    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=100,

        random_state=42
    )


    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )


    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = accuracy_score(

        y_test,

        predictions
    )


    print("\n========================================")
    print("          MODEL EVALUATION")
    print("========================================")


    print(
        f"\nModel Accuracy: "
        f"{accuracy * 100:.2f}%"
    )


    print("\nClassification Report:")


    print(
        classification_report(

            y_test,

            predictions,

            zero_division=0
        )
    )


    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    joblib.dump(

        model,

        "influencer_model.pkl"
    )


    print(
        "\nModel saved as:"
        " influencer_model.pkl"
    )


    return model, accuracy


# ============================================================
# 11. DISPLAY TOP INFLUENCERS
# ============================================================

def display_results(df):

    print("\n========================================")
    print("       TOP INFLUENCERS")
    print("========================================")


    top_influencers = (

        df.sort_values(

            by="influencer_score",

            ascending=False

        )

        .head(10)
    )


    display_columns = [

        "username",

        "platform",

        "followers",

        "engagement_rate",

        "sentiment",

        "authenticity_score",

        "influencer_score",

        "roi"

    ]


    print(

        top_influencers[
            display_columns
        ].to_string(
            index=False
        )
    )


# ============================================================
# 12. SAVE RESULTS
# ============================================================

def save_results(df):

    output_file = (
        "influencer_analysis_results.csv"
    )


    df.to_csv(

        output_file,

        index=False
    )


    print(
        f"\nAnalysis results saved as:"
        f" {output_file}"
    )


# ============================================================
# 13. MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # STEP 1 - LOAD
    # --------------------------------------------------------

    df = load_data()


    if df is None:

        return


    # --------------------------------------------------------
    # STEP 2 - CHECK
    # --------------------------------------------------------

    if not check_columns(df):

        return


    # --------------------------------------------------------
    # STEP 3 - CLEAN
    # --------------------------------------------------------

    df = clean_data(df)


    # --------------------------------------------------------
    # STEP 4 - SENTIMENT
    # --------------------------------------------------------

    df = analyze_sentiment(df)


    # --------------------------------------------------------
    # STEP 5 - FEATURES
    # --------------------------------------------------------

    df = create_features(df)


    # --------------------------------------------------------
    # STEP 6 - AUTHENTICITY
    # --------------------------------------------------------

    df = calculate_authenticity(df)


    # --------------------------------------------------------
    # STEP 7 - INFLUENCER SCORE
    # --------------------------------------------------------

    df = calculate_influencer_score(df)


    # --------------------------------------------------------
    # STEP 8 - CAMPAIGN COST
    # --------------------------------------------------------

    df = calculate_campaign_cost(df)


    # --------------------------------------------------------
    # STEP 9 - ROI
    # --------------------------------------------------------

    df = calculate_roi(df)


    # --------------------------------------------------------
    # STEP 10 - MACHINE LEARNING
    # --------------------------------------------------------

    model, accuracy = train_model(df)


    # --------------------------------------------------------
    # STEP 11 - RESULTS
    # --------------------------------------------------------

    display_results(df)


    # --------------------------------------------------------
    # STEP 12 - SAVE
    # --------------------------------------------------------

    save_results(df)


    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n========================================")
    print("          PROJECT COMPLETED")
    print("========================================")


    if accuracy is not None:

        print(
            f"\nFINAL MODEL ACCURACY: "
            f"{accuracy * 100:.2f}%"
        )


    print(
        "\nGenerated files:"
    )

    print(
        "1. influencer_analysis_results.csv"
    )

    if model is not None:

        print(
            "2. influencer_model.pkl"
        )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()