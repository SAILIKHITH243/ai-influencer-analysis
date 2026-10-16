# Creator Intelligence Pro

**YouTube Creator Discovery, Comparison, and Performance Analytics**

Creator Intelligence Pro is a Python-based web application that helps users discover YouTube creators relevant to a product or campaign, evaluate publicly available performance metrics, compare potential collaborators, and maintain a shortlist for further analysis.

The application combines the YouTube Data API v3, text-similarity analysis, relative performance scoring, interactive visualisations, and SQLite-based historical tracking in a single dashboard.

The platform is designed to support creator research and shortlisting. Its scores are comparative indicators rather than predictions of audience fit, sales, or campaign return on investment.

## Project Links

- **GitHub Repository:** [SAILIKHITH243/ai-influencer-analysis](https://github.com/SAILIKHITH243/ai-influencer-analysis)
- **Live Application:** [Creator Intelligence Pro](https://ai-influencer-analysis-rgvaq8opmjuxtcbj4vgujj.streamlit.app/)

## Table of Contents

1. [Project Overview](#project-overview)
2. [Objectives](#objectives)
3. [Key Features](#key-features)
4. [Application Architecture](#application-architecture)
5. [Application Workflow](#application-workflow)
6. [Scoring Methodology](#scoring-methodology)
7. [Technology Stack](#technology-stack)
8. [Project Structure](#project-structure)
9. [Prerequisites](#prerequisites)
10. [Installation and Setup](#installation-and-setup)
11. [YouTube API Configuration](#youtube-api-configuration)
12. [Running the Application](#running-the-application)
13. [Using the Dashboard](#using-the-dashboard)
14. [Historical Tracking](#historical-tracking)
15. [Data Limitations](#data-limitations)
16. [Security and Configuration](#security-and-configuration)
17. [Testing and Troubleshooting](#testing-and-troubleshooting)
18. [Deployment](#deployment)
19. [Future Improvements](#future-improvements)
20. [Author](#author)
21. [License](#license)

---

## Project Overview

Influencer marketing requires more than comparing subscriber counts. A useful creator-shortlisting process also considers the relevance of published content, the performance of available videos, the size of the channel, and the evidence supporting a potential collaboration.

Creator Intelligence Pro brings these research activities together in an interactive dashboard.

Users enter a product, brand, or campaign topic. The application searches YouTube for related public videos, retrieves available video and channel statistics, calculates content relevance and relative performance scores, and ranks the discovered channels for review.

Users can then inspect individual creator profiles, compare multiple channels, save potential collaborators, analyse matching videos, export reports, and track changes in public channel statistics as new snapshots are collected.

The current application focuses exclusively on YouTube and uses publicly available information returned by the YouTube Data API v3.

## Objectives

The main objectives of this project are to:

- Simplify product-based YouTube creator discovery.
- Support data-informed comparison of potential collaborators.
- Measure textual relevance between a campaign topic and available creator content.
- Present the evidence behind creator-suitability scores.
- Maintain saved creator shortlists for campaign research.
- Analyse performance indicators from matching videos.
- Record public channel statistics over time for historical comparison.
- Provide downloadable reports for further analysis.

## Key Features

### 1. Product-Based Creator Discovery

The discovery module identifies YouTube channels associated with videos matching a supplied product or campaign query.

Capabilities include:

- Search using product names, brand names, or campaign topics.
- Retrieve available public video and channel statistics.
- Display channel names, descriptions, thumbnails, and profile links.
- Rank discovered channels by the calculated suitability score.
- Filter creators by name and minimum content-match score.
- Sort results by suitability, subscriber count, matched-video views, content relevance, or public interaction rate.
- Export the resulting creator shortlist as CSV.

### 2. Creator Comparison Studio

The comparison module supports side-by-side evaluation of two to five creators.

Available comparison metrics may include:

- Subscriber count.
- Lifetime channel views.
- Published video count.
- Average and median views for matched videos.
- Public interactions per view.
- Content-relevance score.
- Relative performance score.
- Final suitability score.

Users can select a metric for visual comparison and export the comparison table for further analysis.

### 3. Explainable Brand-Fit Scoring

The scoring module presents content relevance and public performance as separate components.

It explains:

- How the content-match score is calculated.
- Which performance indicators are available.
- How the performance components contribute to the relative score.
- When missing inputs affect score calculation.
- Why a creator may receive a particular text-relevance classification.

The resulting suitability score is a comparative shortlisting heuristic. It is not a trained model that predicts campaign performance.

### 4. Saved Creator Shortlist

The shortlist module allows users to preserve potential collaborators for further review.

Capabilities include:

- Save and remove creators.
- Associate a creator with a product or campaign tag.
- Filter saved creators by campaign tag.
- Persist saved entries locally using SQLite.
- Open a saved creator's analysis.
- Export shortlist records as CSV.

### 5. Video Performance Intelligence

The video-analysis module examines publicly available statistics for videos returned by the current product or topic search.

Capabilities include:

- Average and median matched-video views.
- Available view, like, and comment counts.
- Public interactions-per-view indicators.
- Top matched videos by view count.
- Upload-date analysis within the returned search sample.
- Exploratory analysis of recurring words in video titles.
- Creator-level filtering.
- CSV export of video-level results.

These metrics describe the retrieved search sample rather than a guaranteed complete inventory of every video published by a channel.

### 6. Creator Profile and Historical Tracking

The creator profile provides a detailed view of an individual YouTube channel.

It can display:

- Channel description and profile link.
- Subscriber count.
- Lifetime channel views.
- Published video count.
- Channel age when the publication date is available.
- Content relevance and performance scores.
- Matching-video statistics.
- Historical channel-statistic snapshots.
- Downloadable history and video reports.

Daily, weekly, monthly, yearly, and all-time views are derived from historical snapshots recorded by the application.

### 7. Dashboard Overview and Reporting

The dashboard overview summarises the active search and stored creator records.

Reporting capabilities include:

- Current creator-search summaries.
- Suitability and public-performance comparisons.
- Latest saved channel snapshots.
- CSV exports of creator results, comparisons, video samples, and saved shortlists.

The interface uses a dark navy background, charcoal cards, violet accents, and cyan highlights.

## Application Architecture

The application uses a modular design that separates data retrieval, ranking, persistence, and presentation.

| Component | Responsibility |
|---|---|
| Streamlit dashboard | User interface, navigation, filters, charts, and reports |
| YouTube API module | YouTube Data API requests and response parsing |
| Ranking module | Text relevance, performance normalisation, and suitability scoring |
| Database module | Historical snapshots and saved creator records |
| SQLite database | Local persistence of collected records |
| Plotly visualisations | Interactive comparison and performance charts |

### Architecture Diagram

```text
                 User Product or Campaign Query
                              |
                              v
                    Streamlit Dashboard
                              |
                              v
                     YouTube API Module
                              |
                              v
                YouTube Data API v3 Endpoints
                              |
                              v
                  Public Video and Channel Data
                              |
                              v
                     Ranking and Analysis
                     /                \
                    v                  v
          Text Relevance        Performance Metrics
                    \                  /
                     v                v
                    Creator Suitability Scores
                              |
               +--------------+--------------+
               |              |              |
               v              v              v
         Creator Profile   Comparison    Video Analysis
               |              |              |
               +--------------+--------------+
                              |
                              v
                  SQLite Persistence Layer
                              |
                              v
                  Historical Data and Exports
```

## Application Workflow

The typical workflow is:

1. Enter a product, brand, or campaign topic.
2. Search YouTube for matching public videos.
3. Retrieve available video and channel statistics.
4. Prepare the retrieved records for analysis.
5. Compare the search query with available channel and video text.
6. Normalise available public performance metrics.
7. Rank the discovered creators.
8. Inspect individual creator profiles and matching videos.
9. Compare potential collaborators and save the preferred candidates.
10. Export reports and collect additional snapshots for historical analysis.

## Scoring Methodology

The suitability score is designed to support transparent creator shortlisting. It must not be interpreted as a guarantee of campaign performance.

### Content-Relevance Component

Content relevance is calculated using TF-IDF text vectorisation and cosine similarity.

The search phrase is compared with available information such as:

- Channel names.
- Channel descriptions.
- Matching video titles.
- Matching video descriptions.

The text-similarity result is scaled to a 0–100 range for presentation.

This component measures textual similarity in the available search results. It does not independently establish audience demographics, audience authenticity, brand safety, purchase intent, or commercial suitability.

### Relative Performance Component

When the required metrics are available, the performance component combines normalised values from the current search-result set.

| Performance Metric | Base Weight |
|---|---:|
| Matched-video views | 55% |
| Public interactions per view | 25% |
| Subscriber count | 20% |

Views and subscriber counts use logarithmic scaling before normalisation. When an input is unavailable, the available component weights are renormalised proportionally.

The normalised values are relative to the creators included in the current result set, rather than fixed industry benchmarks.

### Final Suitability Score

When a performance score is available, the calculation is:

`Suitability Score = (0.70 × Content Match) + (0.30 × Performance Score)`

When performance inputs are unavailable, the final score falls back to the content-match score.

A score from one search may not be directly comparable with a score from another search because the available channels and normalisation baseline can differ.

The suitability score does not guarantee audience fit, sales, conversions, or campaign return on investment.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and metric calculations |
| Streamlit | Interactive web dashboard |
| YouTube Data API v3 | Public video and channel data retrieval |
| Pandas | Data preparation, filtering, and aggregation |
| NumPy | Numerical operations |
| Scikit-learn | TF-IDF vectorisation and cosine similarity |
| Plotly Express | Interactive charts and visual analysis |
| SQLite | Local historical tracking and shortlist persistence |
| Requests | HTTP requests to the YouTube API |
| Git and GitHub | Source control and project versioning |

## Project Structure

```text
ai-influencer-analysis/
|
|-- app.py
|-- youtube_api.py
|-- influencers.py
|-- database.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- .streamlit/
|   |-- config.toml
|   |-- secrets.toml
```

### Module Responsibilities

**`app.py`**

Implements the Streamlit user interface, dashboard navigation, creator discovery, creator profiles, comparisons, video analytics, score explanations, and CSV exports.

**`youtube_api.py`**

Handles requests to the YouTube Data API v3 and prepares available public video and channel statistics.

**`influencers.py`**

Calculates text relevance, normalises performance metrics, creates explainable score components, and ranks creators.

**`database.py`**

Creates and migrates SQLite tables, saves channel snapshots, and manages saved creator shortlist records.

**`requirements.txt`**

Lists the Python packages required to run the application.

**`.streamlit/secrets.toml`**

Contains the locally configured YouTube API key. It is private configuration and must not be committed to GitHub.

**`influencer_history.db`**

The application creates this local database when historical tracking is initialised. The file should not be committed to source control.

## Prerequisites

Before running the project, ensure that the following are available:

- Python 3.10 or later.
- Git for repository operations.
- A Google account.
- A Google Cloud project.
- YouTube Data API v3 enabled in the selected Google Cloud project.
- A valid YouTube Data API key.

## Installation and Setup

### Step 1: Clone the Repository

```powershell
git clone https://github.com/SAILIKHITH243/ai-influencer-analysis.git
cd ai-influencer-analysis
```

If you already have a working project folder, do not clone over it. Open the intended repository folder in VS Code instead.

### Step 2: Create a Virtual Environment

```powershell
python -m venv .venv
```

On Windows, activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This avoids needing to change the system execution policy.

### Step 3: Install Dependencies

When the virtual environment is activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## YouTube API Configuration

The application requires a YouTube Data API v3 key to retrieve live public data.

### Create an API Key

1. Open the Google Cloud Console.
2. Select the project intended for the application.
3. Enable YouTube Data API v3.
4. Open the project's Credentials page.
5. Create an API key.
6. Restrict the key to YouTube Data API v3 where possible.

Google Cloud resources:

- [Google Cloud Console](https://console.cloud.google.com/)
- [YouTube Data API v3 documentation](https://developers.google.com/youtube/v3)

### Store the Key Locally

Create the `.streamlit` directory in the project root if it does not exist. Inside the directory, create `secrets.toml`.

Add the following configuration:

```toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

Replace the placeholder with the actual key locally.

Never put the real key into Python source code, README content, public screenshots, or GitHub commits.

## Running the Application

### Check Python Syntax

From the project root:

```powershell
python -m py_compile app.py database.py influencers.py youtube_api.py
```

If the virtual environment is not activated:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py database.py influencers.py youtube_api.py
```

### Start Streamlit

With the environment activated:

```powershell
python -m streamlit run app.py
```

Or use the environment's Python executable:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the Local URL printed in the terminal. The default port is commonly `8501`, but Streamlit may select a different port when the default is already occupied.

Keep the terminal open while using the local dashboard.

## Using the Dashboard

### Discover Influencers

Enter a product or brand, run the YouTube search, apply the available filters, and inspect the ranked creator results.

### Creator Profile

Select a creator to view public channel statistics, score components, matching-video analysis, and saved history.

### Compare Creators

Select two to five creators, choose the metric for comparison, review the chart and table, and export the results.

### Saved Shortlist

Save creators from the discovery or profile pages. Filter saved entries by campaign tag, open creator analyses, remove entries, or export the shortlist.

### Video Performance

Review performance metrics from the active search sample, inspect top matched videos, explore title-keyword signals, and export video data.

### Dashboard Overview

Review current search statistics and the latest locally saved channel snapshots.

## Historical Tracking

When a successful search returns a channel, the application can save a snapshot of selected public statistics.

Supported historical views group collected snapshots into:

- Daily periods.
- Weekly periods.
- Monthly periods.
- Yearly periods.
- All available saved history.

Historical growth requires multiple observations of the same channel. A single snapshot cannot establish a trend.

Historical values from before tracking began cannot be reconstructed automatically. The recorded history represents the observations collected by the application.

Local database files should be backed up if the stored history is important.

## Data and Methodology Limitations

The application is subject to the following limitations:

- YouTube search returns a sample of matching videos, not necessarily every video uploaded by a channel.
- Average and median matched-video views describe the videos returned by the current search.
- Public interaction rates use available statistics and may be unavailable when likes, comments, or views are hidden.
- The application does not obtain arbitrary creators' private audience demographics, watch time, retention, or unique reach through this public-data workflow.
- Performance scores are relative to the current search-result set.
- Search results and available metrics depend on API access, quota, query relevance, and data returned by YouTube.
- Historical tracking only covers observations collected after the application starts recording them.
- Text similarity does not prove that a creator's audience is appropriate for a product.
- The application does not verify follower authenticity or predict guaranteed commercial results.

## Security and Configuration

The project uses a local secrets file for API credentials.

Security recommendations:

- Keep `.streamlit/secrets.toml` private.
- Never commit API keys, tokens, or `.env` files.
- Restrict the API key through Google Cloud where practical.
- Rotate the key if it is accidentally exposed.
- Do not commit local databases or confidential exports.
- Keep virtual environments out of source control.

The project's `.gitignore` should contain at least:

```gitignore
.streamlit/secrets.toml
.env
.env.*
*.db
*.sqlite
*.sqlite3
__pycache__/
.venv/
venv/
```

## Testing and Troubleshooting

### Syntax or Import Errors

Run:

```powershell
python -m py_compile app.py database.py influencers.py youtube_api.py
```

If an import error identifies a missing function, confirm that the corresponding module file is the intended version and contains that function.

### API Key Not Found

Check that `.streamlit/secrets.toml` exists in the project directory from which Streamlit is running and contains the exact setting:

```toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

Do not share the key to troubleshoot this issue.

### API Request or Quota Errors

Check that YouTube Data API v3 is enabled, the API key is valid, and quota remains available in Google Cloud Console.

### No Creator Results

Try a broader product phrase and check whether YouTube returns matching public videos for the search.

### Empty Historical Charts

Historical charts require snapshots collected over time. They cannot generate historical data retroactively.

### Port Already in Use

Use the Local URL printed in the terminal. If the preferred port is already occupied, run Streamlit with another available port.

## Deployment

The application can be deployed through Streamlit Community Cloud.

Recommended deployment workflow:

1. Verify the project locally.
2. Commit and push the intended source files to GitHub.
3. Connect the intended repository and branch to Streamlit Community Cloud.
4. Configure `YOUTUBE_API_KEY` in the deployment's Secrets settings.
5. Confirm that the app starts and a YouTube search succeeds.
6. Test creator comparison, shortlist persistence, exports, and history.

Do not assume local SQLite data will persist across every hosting restart or redeployment. A production deployment may require a persistent database and a backup strategy.

## Future Improvements

Potential future work includes:

- Scheduled collection of channel snapshots.
- Additional creator discovery and comparison filters.
- Automated tests for database migrations and dashboard workflows.
- Campaign-specific reporting templates.
- Persistent database hosting for multi-user deployments.
- Improved text classification with a documented evaluation methodology.
- Better data-quality indicators for missing or limited public metrics.

## Author

**Sai Likhith**

GitHub: [SAILIKHITH243](https://github.com/SAILIKHITH243)

## License

No formal open-source license is currently specified in this repository. Reuse, redistribution, and modification permissions should not be assumed until a license is added.