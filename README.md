# Finance Dashboard

A comprehensive finance dashboard for loan eligibility assessment with data visualization and scoring.

## Project Structure

```
finance-dashboard/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── config/         # Configuration
│   ├── requirements.txt    # Python dependencies
│   └── uploads/           # Temporary file storage
├── frontend/              # React Next.js frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Next.js pages
│   │   ├── hooks/         # Custom hooks
│   │   ├── utils/         # Utility functions
│   │   └── styles/        # CSS styles
│   ├── package.json       # Node dependencies
│   └── next.config.js     # Next.js configuration
└── README.md              # This file
```

## Features

- 📊 Excel file upload and processing
- 📈 Interactive data visualizations
- 🎯 Rule-based scoring system
- 📋 Comprehensive dashboard UI
- 🔍 Multi-case evaluation

## Tech Stack

**Backend:**
- Python 3.9+
- FastAPI
- Pandas
- Plotly
- OpenPyXL

**Frontend:**
- React 18
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn/ui

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Upload Excel file with eligibility criteria (Sheet 1) and cases (subsequent sheets)
2. View processed data and visualizations
3. Review scoring results and recommendations 