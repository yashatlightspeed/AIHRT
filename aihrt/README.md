# AIHRT 
### Artificially Intelligent Head Recruiter Tech

> Built this for my final year project at Chandigarh University (AIT).

---

## What is this?

An AI system that conducts job interviews automatically and scores 
candidates based on HOW they speak, not just WHAT they say.

Instead of a human interviewer, AIHRT:
- Records your spoken answers directly in the browser
- Transcribes them using OpenAI Whisper
- Analyses semantic coherence, cognitive load, emotional alignment,
  and stress resilience using our custom NBCAM model
- Generates adaptive follow-up questions using GPT-4o-mini
- Gives a Final Cognitive Score (FCS) out of 100
- Shows the recruiter a full dashboard with AI-generated insights

---

## The Scoring System (NBCAM)

We designed a custom model called the
**Neuro-Behavioral Cognitive Alignment Model** with 4 layers:

| Score | Full Name | What it measures |
|-------|-----------|-----------------|
| CSS | Cognitive Stability Score | Does the answer stay on topic throughout? |
| CLI | Cognitive Load Index | Acoustic signs of stress in the voice |
| ECS | Emotional Consistency Score | Does emotion in words match emotion in voice? |
| SRS | Stress Resilience Score | Do scores stay stable under increasing pressure? |
| **FCS** | **Final Cognitive Score** | **All 4 combined → score out of 100** |

---

## Tech Stack

**Backend**
- Python + FastAPI
- OpenAI Whisper (speech to text, 244M parameters)
- Sentence-BERT all-MiniLM-L6-v2 (semantic embeddings)
- DistilRoBERTa (7-class emotion classification)
- Librosa (acoustic feature extraction)
- GPT-4o-mini (adaptive questions + behavioral insights)
- PostgreSQL + SQLAlchemy

**Frontend**
- React.js
- Web Audio API (real-time waveform visualization)
- MediaRecorder API (browser audio capture)

**Infrastructure**
- Docker + Docker Compose (3 containers)

---

## How to Run It

You need Docker Desktop installed. That's literally it.
```bash
git clone https://github.com/YOURUSERNAME/AIHRT.git
cd AIHRT
cp .env.example .env
```

Open `.env` and add your OpenAI API key, then:
```bash
docker compose up
```

Open **http://localhost:3000** in your browser.

> ⚠️ First run takes ~8 minutes — downloads Whisper (461MB),
> SBERT (90MB), and DistilRoBERTa (330MB).
> Every run after that takes under 60 seconds.

---

## Seed the Questions (first time only)

After the containers are running, visit:
**http://localhost:8000/docs** → find `POST /api/questions/seed` → click Execute

---

## Results

Tested on 8 real candidate sessions. FCS ranged from 50 to 75.

| Candidate | Role | CSS | CLI | ECS | SRS | FCS | Classification |
|-----------|------|-----|-----|-----|-----|-----|----------------|
| C1 | ML Engineer | 0.74 | 0.32 | 0.77 | 0.80 | 75 | Strong Candidate |
| C2 | Backend Dev | 0.69 | 0.41 | 0.72 | 0.74 | 69 | Above Average |
| C3 | Product Manager | 0.63 | 0.29 | 0.70 | 0.71 | 69 | Above Average |
| C4 | Data Scientist | 0.58 | 0.46 | 0.73 | 0.69 | 64 | Average |
| C5 | QA Engineer | 0.66 | 0.38 | 0.64 | 0.62 | 64 | Average |
| C6 | Frontend Dev | 0.51 | 0.35 | 0.61 | 0.66 | 61 | Average |
| C7 | Cloud Engineer | 0.57 | 0.52 | 0.60 | 0.57 | 56 | Below Average |
| C8 | Graduate Trainee | 0.42 | 0.47 | 0.54 | 0.50 | 50 | Below Average |

---

## Project Structure
```
aihrt/
├── docker-compose.yml          # Starts all 3 containers
├── .env.example                # Copy this to .env and fill in your keys
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI entry point
│   ├── models.py               # Database tables
│   ├── database.py             # PostgreSQL connection
│   ├── nbcam/
│   │   ├── layer1_sdm.py       # Semantic Drift Mapping → CSS
│   │   ├── layer2_cli.py       # Cognitive Load Index → CLI
│   │   ├── layer3_ecam.py      # Emotion-Content Alignment → ECS
│   │   ├── layer4_acpt.py      # Adaptive Pressure Testing → SRS
│   │   └── fusion.py           # Combines scores → FCS
│   ├── services/
│   │   ├── asr_engine.py       # Whisper transcription + audio features
│   │   └── gpt_insights.py     # GPT behavioral analysis
│   └── routers/
│       ├── candidates.py
│       ├── interviews.py
│       ├── responses.py
│       ├── questions.py
│       └── scores.py
└── frontend/
    └── src/
        ├── App.jsx             # Page routing
        └── pages/
            ├── LandingPage.jsx
            ├── RegistrationPage.jsx
            ├── InterviewPage.jsx   # Audio recording + waveform
            ├── ProcessingPage.jsx
            └── DashboardPage.jsx   # Score gauges + insights
```

---

## Research Paper

We wrote a full IEEE-format research paper on the NBCAM methodology.
Available in the `/paper` folder.

---

## Team

Built by 3 students from Chandigarh University, Apex Institute of Technology:

| Name | Email |
|------|-------|
| Aayush Sharma | aayushhsharma13@gmail.com |
| Yash Tripathi | yashmizoram@gmail.com |
| Yashita | gargyashita13@gmail.com |

---

## Known Issues / Limitations

- First startup is slow (model downloads ~880MB total)
- Microphone needs HTTPS in production (localhost works fine)
- GPT features require an OpenAI API key in `.env`
- Best tested on Chrome and Edge
- For research paper data, candidates should answer in clear English

---

## What I learned

This project taught me more than 3 years of college combined.
Docker, FastAPI, transformer models, audio signal processing
