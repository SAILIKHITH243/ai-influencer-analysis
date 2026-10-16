# AI Influencer Analysis

AI Influencer Analysis is a Python-based web application that helps users discover, analyze, and compare YouTube creators for product and brand marketing.

The application uses publicly available YouTube channel and video information to help users identify creators whose content may be relevant to a marketing campaign. It provides creator discovery, content relevance analysis, performance comparisons, interactive visualizations, and historical tracking when sufficient data is available.

## Project Links

- Live Website: https://ai-influencer-analysis-rgvaq8opmjuxtcbj4vgujj.streamlit.app/
- GitHub Repository: https://github.com/SAILIKHITH243/ai-influencer-analysis

## Project Overview

Influencer marketing helps brands reach potential customers through content creators. However, selecting a suitable creator requires more than comparing follower counts.

This project provides an interactive dashboard to explore relevant YouTube creators and compare their available public statistics. It is designed to support data-informed creator shortlisting and marketing research.

## Features

- Search for YouTube creators using a product or brand name.
- Retrieve available public channel and video statistics through YouTube Data API v3.
- Compare creators using subscriber counts and available video performance metrics.
- Analyze content relevance to a selected product or brand.
- View individual creator profiles and analytics.
- Analyze video views, likes, and comments where available.
- Visualize creator statistics using interactive charts.
- Store creator statistics as historical snapshots in an SQLite database.
- Review daily, weekly, monthly, and yearly trends when sufficient historical data is available.
- Explore creator comparisons through a Streamlit dashboard.

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Scikit-learn
- YouTube Data API v3
- SQLite
- Git and GitHub

## Project Structure

```text
ai-influencer-analysis/
├── app.py
├── youtube_api.py
├── influencers.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md
```

The application may also create a local SQLite database to store historical creator statistics. Local databases and secret configuration files should not be committed to GitHub.

## How It Works

### 1. Creator Discovery

The user enters a product or brand name. The application searches YouTube and retrieves relevant public video and channel information through the YouTube Data API.

### 2. Content Relevance Analysis

Available channel descriptions and video information are compared with the user's search query to estimate how relevant a creator may be to the selected product or brand.

### 3. Performance Analysis

Available public metrics, including subscriber counts, video views, likes, and comments, help users compare creators.

### 4. Creator Suitability Scoring

Content relevance and selected performance indicators are used to help users shortlist potential creators. The suitability score is a comparative indicator and does not guarantee sales, campaign success, or return on investment.

### 5. Historical Tracking

Creator statistics are stored as snapshots in an SQLite database. As additional snapshots are collected, the application can visualize changes in channel statistics over time.

Historical analysis depends on the previously collected data. Statistics from periods before tracking began cannot be reconstructed automatically.

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- A Google Cloud project with YouTube Data API v3 enabled
- A YouTube Data API key

### 1. Clone the Repository

```bash
git clone https://github.com/SAILIKHITH243/ai-influencer-analysis.git
cd ai-influencer-analysis
```

### 2. Create a Virtual Environment

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the YouTube API Key

Create a directory named `.streamlit` in the project folder if it does not already exist. Inside it, create a file named `secrets.toml`.

Add your own API key:

```toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

Replace the placeholder with your own YouTube Data API key.

Never publish your API key or upload `.streamlit/secrets.toml` to GitHub. For the deployed application, configure the key through the application's Streamlit Community Cloud Secrets settings.

### 5. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Deployment

The application is hosted on Streamlit Community Cloud.

Live Website:

https://ai-influencer-analysis-rgvaq8opmjuxtcbj4vgujj.streamlit.app/

The deployed application requires the appropriate API key to be configured securely through Streamlit's Secrets settings. Deployment and application functionality may depend on API availability and quota limits.

## Limitations

- Search results depend on the query and available YouTube API results.
- Public metrics vary depending on the information available for each channel and video.
- Suitability scores are comparative indicators, not predictions of campaign outcomes.
- Historical trends require previously collected statistics.
- Historical data is not available for periods before tracking began unless it was recorded separately.
- YouTube Data API quota limits may affect searches.
- Public YouTube data does not provide every creator's private audience demographics, watch time, or unique reach.
- The application cannot guarantee the accuracy of marketing decisions or campaign results.

## Future Improvements

- Scheduled collection of creator statistics.
- More advanced creator filtering and comparison.
- Expanded historical trend analysis.
- Improved brand-fit and campaign planning tools.
- More detailed creator performance reports.
- Support for additional social media platforms where suitable data access is available.

## Author

Sai Likhith

B.Tech in Computer Science and Engineering (IoT)

GitHub: https://github.com/SAILIKHITH243

## License

This project is available for educational and portfolio purposes. A formal open-source license can be added if the project is intended for public reuse.
