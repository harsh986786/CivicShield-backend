# 🎯 Social Media Analytics Backend

**AI-Driven Social Media Intelligence Framework** for the Smart India Hackathon (SIH)

An advanced backend system that processes raw social media data to extract deep, actionable audience insights through sentiment analysis, demographic profiling, trend detection, and network analysis.

---

## 📋 Project Overview

This solution addresses the **SIH Problem Statement 26152** by implementing a multi-dimensional analytics platform that combines:

- **Sentiment Analysis**: Detect emotions and sentiments in posts/comments (anger, joy, sarcasm, etc.)
- **Demographic Profiling**: Infer age, location, and interests from user profiles
- **Trend Detection**: Identify and rank trending topics with velocity tracking
- **Network Analysis**: Map influencer networks and information propagation
- **Timeline Management**: Structured, time-stamped database for conversation chronology

---

## 🏗️ Tech Stack

### Backend Framework
- **FastAPI** `^0.110.0` - Modern async web framework
- **Uvicorn** `^0.28.0` - ASGI application server

### Database & ORM
- **PostgreSQL** - Primary database
- **SQLAlchemy** `^2.0.0` - SQL toolkit and ORM
- **Psycopg2** `^2.9.0` - PostgreSQL adapter

### Machine Learning & NLP
- **HuggingFace Transformers** - Pre-trained NLP models
  - BERT for emotion detection (`bhadresh-savani/bert-base-uncased-emotion`)
  - RoBERTa for sentiment analysis (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
- **NetworkX** `^3.2.0` - Graph analysis and algorithms
- **NumPy** `^1.26.0` - Numerical computing
- **SciPy** `^1.12.0` - Scientific computing

### Utilities
- **Pydantic** `^2.6.0` - Data validation
- **Pydantic Settings** `^2.2.0` - Configuration management
- **Python-dotenv** `^1.0.0` - Environment variables
- **HTTPX** `^0.27.0` - Async HTTP client

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Virtual Environment (recommended)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Hyperion147/social-analytics-backend-26.git
cd social-analytics-backend-26

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Initialize database
python scripts/init_db.py

# 6. Run server
uvicorn app.main:app --reload
```

**API Documentation**: http://localhost:8000/docs

---

## 📡 API Routes

### Health Check
```
GET /health
```
Returns service status

---

### 📥 Data Ingestion (`/api/v1/ingest`)

#### 1. **Mock Data Generation**
```
POST /api/v1/ingest/mock
```
Generate and insert mock social media posts for testing
- **Parameters**: `count` (default: 30)
- **Returns**: Generated posts count, inserted records

#### 2. **X (Twitter) Ingestion**
```
POST /api/v1/ingest/x
```
Fetch real-time posts from X/Twitter
- **Parameters**: `query` (default: "technology"), `limit` (default: 15)
- **Returns**: Fetched posts, newly inserted records

#### 3. **Telegram Ingestion**
```
POST /api/v1/ingest/telegram
```
Fetch real-time messages from public Telegram channels
- **Parameters**: `channel` (default: "durov"), `limit` (default: 15)
- **Returns**: Fetched posts, newly inserted records

#### 4. **Reddit Ingestion**
```
POST /api/v1/ingest/reddit
```
Fetch real-time posts from public Subreddits
- **Parameters**: `subreddit` (default: "technology"), `limit` (default: 15)
- **Returns**: Fetched posts, newly inserted records

#### 5. **Batch Live Ingestion**
```
POST /api/v1/ingest/batch-live
```
Fetch data from multiple sources simultaneously (Reddit, Telegram)
- **Returns**: Total sources queried, total fetched, newly inserted

---

### 📊 Analytics & Pipeline (`/api/v1/analytics`)

#### 1. **Run Analytics Pipeline**
```
POST /api/v1/analytics/run-pipeline
```
Trigger NLP processing and graph analysis on ingested posts
- **Returns**: Pipeline execution status and results

---

### 📈 Dashboard Intelligence (`/api/v1/dashboard`)

#### 1. **Unified Dashboard Overview**
```
GET /api/v1/dashboard/overview
```
Get comprehensive 5-vector SIH analytics payload including:
- Sentiment distribution
- Trending topics with velocity
- Network topology and influencers
- Demographic breakdown
- AI executive summary

**Response Includes:**
```json
{
  "summary_metrics": {
    "total_posts_ingested": 500,
    "total_nodes_mapped": 150,
    "total_edges_connected": 450
  },
  "sentiment_distribution": {
    "positive": 45.2,
    "negative": 25.1,
    "neutral": 29.7
  },
  "trending_topics": [
    {
      "topic": "#AI",
      "frequency": 125,
      "velocity_percentage": 150.0,
      "status": "surging"
    }
  ],
  "demographics_breakdown": {
    "age_distribution": {...},
    "geographic_distribution": {...},
    "language_distribution": {...}
  },
  "network_topology": {
    "nodes": [...],
    "edges": [...],
    "top_influencers": [...]
  },
  "ai_executive_summary": {...}
}
```

#### 2. **Timeline Metrics**
```
GET /api/v1/dashboard/timeline
```
Get hourly aggregated sentiment and volume timeline
- **Returns**: Time-series data with sentiment breakdown per hour

---

### 🕸️ Network & Link Analysis (`/api/v1/network`)

#### 1. **Propagation Timeline**
```
GET /api/v1/network/propagation-timeline
```
Track chronological diffusion of discussions through influencer networks
- **Parameters**: `topic` (optional), `limit` (default: 20)
- **Returns**: Cascade flow events with sentiment and emotion tracking

---

## 🗄️ Database Models

### Core Tables

#### `posts`
Stores all ingested social media posts
- `id` (UUID): Primary key
- `platform` (String): Source platform (twitter, telegram, reddit, etc.)
- `platform_post_id` (String): Unique ID from source platform
- `author_id`, `author_username`, `author_bio`
- `text` (Text): Post content
- `language` (String): Language code
- `created_at` (DateTime): Post creation timestamp
- `parent_post_id` (String): For tracking reply chains
- `engagement_count` (JSONB): Likes, retweets, etc.
- `raw_data` (JSONB): Original API response
- `is_processed` (Boolean): Processing status

#### `sentiment_results`
Stores NLP analysis results
- `post_id` (UUID FK): Reference to post
- `sentiment` (String): positive, negative, neutral
- `emotion` (String): anger, joy, sadness, fear, surprise, sarcasm
- `confidence` (Float): Model confidence score
- `model_version` (String): NLP model version

#### `network_edges`
Stores relationship graphs
- `source_author_id`, `target_author_id`
- `platform` (String)
- `interaction_type` (String): mention, reply, repost
- `created_at` (DateTime)

#### `trend_snapshots`
Stores trend tracking data
- `topic` (String): Hashtag or keyword
- `frequency` (Integer): Occurrence count
- `velocity` (Float): Growth rate percentage
- `sentiment_bias` (String): Prevalent sentiment
- `timestamp_bucket` (DateTime): Time window

---

## 🤖 Core Services

### Sentiment Service (`app/services/sentiment_service.py`)
- Dual-model approach: RoBERTa (sentiment) + BERT (emotion)
- 3-class sentiment: positive, negative, neutral
- 6-class emotion: anger, fear, joy, love, sadness, surprise
- Heuristic sarcasm detection
- Lazy model loading to optimize startup

### Demographic Service (`app/services/demographic_service.py`)
- Age bracket inference: 18-24, 25-34, 35-50
- Geographic profiling: India regions + International
- Language distribution tracking
- Keyword-based profiling from bio text

### Trend Service (`app/services/trend_service.py`)
- Hashtag and keyword extraction
- 2-hour/4-hour sliding window analysis
- Velocity percentage calculation
- Status classification: surging (50%+), rising (0%+), declining

### Network Service (`app/services/network_service.py`)
- PageRank algorithm for influence scoring
- Greedy Modularity community detection
- Mention, reply, and repost extraction
- Network topology metrics

### Insight Service (`app/services/insight_service.py`)
- AI-powered executive summary generation
- Multi-vector intelligence synthesis

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/sih_db

# API Settings
PROJECT_NAME=SIH Social Media Intelligence
API_V1_STR=/api/v1

# NLP Models (auto-downloaded on first use)
# Uses HuggingFace models with caching
```

---

## 📊 Data Flow

```
Raw Posts (X, Telegram, Reddit)
    ↓
Data Ingestion Pipeline → PostgreSQL
    ↓
Analytics Pipeline (triggered on-demand)
    ├─ Sentiment Analysis (BERT/RoBERTa)
    ├─ Demographic Inference (Keyword matching)
    ├─ Trend Detection (Hashtag/Keyword velocity)
    ├─ Network Analysis (NetworkX graph)
    └─ Results stored in respective tables
    ↓
Dashboard Aggregation
    ↓
API Response (Unified 5-Vector Analytics)
```

---

## 🚦 Pipeline Execution

### Automatic Processing
1. Call `/api/v1/ingest/{platform}` to fetch posts
2. Posts stored with `is_processed = False`
3. Call `/api/v1/analytics/run-pipeline` to trigger NLP
4. Services process unprocessed posts
5. Results stored in sentiment, network, trend tables

### Real-time Updates
Dashboard endpoints aggregate latest results on-demand from database views

---

## 🎯 Feature Highlights

✅ **Multi-Platform Support**
- X (Twitter), Telegram, Reddit ingestion
- Extensible adapter pattern for new platforms

✅ **Advanced NLP**
- Dual-model sentiment + emotion detection
- Sarcasm detection with heuristics
- Confidence scoring

✅ **Demographic Intelligence**
- Age, location, language profiling
- Behavioral pattern inference

✅ **Trend Analytics**
- Velocity-based trend ranking
- Time-window segmentation
- Sentiment bias per trend

✅ **Network Intelligence**
- Influencer identification (PageRank)
- Community detection
- Propagation tracking

✅ **Type-Safe Code**
- Full Pylance type checking
- SQLAlchemy 2.0 type hints
- Pydantic validation

---

## 📈 Performance Considerations

- **Database Indexing**: Platform, created_at, is_processed
- **Lazy Model Loading**: NLP models loaded on first use
- **Batch Processing**: Pipeline processes in transactions
- **Async Operations**: HTTP client for ingestion
- **JSONB Storage**: Flexible raw data retention

---

## 🔒 Security Features

- CORS enabled for all origins (configurable)
- PostgreSQL connection pooling
- Environment-based configuration
- Input validation via Pydantic

---

## 📝 API Response Examples

### Dashboard Overview
```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

### Mock Data Ingestion
```bash
curl -X POST http://localhost:8000/api/v1/ingest/mock?count=50
```

### Propagation Timeline
```bash
curl "http://localhost:8000/api/v1/network/propagation-timeline?topic=AI&limit=20"
```

### Timeline Metrics
```bash
curl http://localhost:8000/api/v1/dashboard/timeline
```

---

## 🗂️ Project Structure

```
social-analytics-backend-26/
├── app/
│   ├── api/v1/              # API route handlers
│   │   ├── ingestion.py     # Data collection endpoints
│   │   ├── analytics.py     # Pipeline triggers
│   │   ├── dashboard.py     # Intelligence endpoints
│   │   ├── timeline.py      # Time-series analytics
│   │   └── network.py       # Link analysis endpoints
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── post.py
│   │   ├── sentiment.py
│   │   ├── network.py
│   │   └── trend.py
│   ├── services/            # Business logic
│   │   ├── sentiment_service.py
│   │   ├── demographic_service.py
│   │   ├── trend_service.py
│   │   ├── network_service.py
│   │   └── insight_service.py
│   ├── ingestion/           # Platform adapters
│   │   ├── base.py
│   │   ├── mock_adapter.py
│   │   ├── x_adapter.py
│   │   ├── telegram_adapter.py
│   │   └── reddit_adapter.py
│   ├── core/                # Core utilities
│   │   ├── database.py
│   │   └── config.py
│   ├── workers/             # Background jobs
│   │   └── pipeline_worker.py
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # FastAPI app
├── scripts/                 # Database initialization
│   └── init_db.py
├── tests/                   # Unit & integration tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🚀 Next Steps / Roadmap

### High Priority (Phase 1)
- [ ] Instagram & Facebook adapters
- [ ] Enhanced sarcasm detection (ML-based)
- [ ] KOL (Key Opinion Leader) tier classification
- [ ] WebSocket support for live dashboard

### Medium Priority (Phase 2)
- [ ] Topic modeling (BERTopic)
- [ ] Time-series forecasting
- [ ] User behavior segmentation/clustering
- [ ] Cross-platform user linking

### Future Enhancements
- [ ] YouTube comment ingestion
- [ ] Bot detection algorithms
- [ ] Echo chamber identification
- [ ] PDF report generation
- [ ] Advanced centrality measures

See [IMPLEMENTATION_ANALYSIS.md](IMPLEMENTATION_ANALYSIS.md) for detailed feature planning.

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'Add your feature'`
3. Push branch: `git push origin feature/your-feature`
4. Open Pull Request

---

## 📄 License

Part of the Smart India Hackathon 2026 submission

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

---

## 🏆 SIH Problem Statement Alignment

This solution directly addresses **Problem Statement 26152 - Social Media Analytics** by implementing all five core components:

- ✅ **A. Continuous Data Collection** - Multi-platform ingestion with timeline management
- ✅ **B. Multi-Dimensional Sentiment** - NLP-based emotion and sentiment detection
- ✅ **C. Demographic Profiling** - Automated audience demographic inference
- ✅ **D. Real-Time Trends** - Velocity-based trend detection and ranking
- ✅ **E. Network Topology** - Graph analysis for KOL identification and influence mapping

**Status**: Core features implemented, Phase 2 features in development

---

**Last Updated**: August 29, 2026
