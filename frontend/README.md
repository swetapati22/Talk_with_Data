# 📊 TalkWithData: AI-Powered CSV Visualization Generator

**TalkWithData** simplifies data exploration for everyone — no coding needed. Upload a CSV file and instantly see context-aware charts and the code that generated them, all powered by AI.

---

## Inspiration

We noticed that many students and professionals struggle to interpret raw CSV files. Creating visualizations often requires programming knowledge, which can be a barrier. Our goal: make data analysis as simple as dragging and dropping a file.

---

## What It Does

- Upload a **CSV file** to receive **intelligent visualizations** (e.g. heatmaps, bar charts, scatter plots).
- Each visualization includes a **summary**, **AI-generated plot**, and the **Python code** used to create it.
- Uses **Google Gemini AI** to understand data context and generate meaningful visual insights.

---

## How We Built It

- **Frontend**: Built with **React.js**, allowing CSV upload and dynamic display of charts and code.
- **Backend**: Powered by **Flask**, uses **Matplotlib** and **Seaborn** to create plots and return them as base64-encoded images.
- **AI Integration**: Utilized **Google Gemini AI** to suggest the most relevant visualizations.
- **Communication**: Configured **CORS** to ensure seamless interaction between frontend and backend.

---

## Challenges We Overcame

- Handling **CORS issues** between the frontend and backend.
- Parsing inconsistent or messy **real-world CSV data**.
- Ensuring **AI-generated Python code** is executable and safe.
- Maintaining a smooth UX even with **large file uploads**.

---

## Accomplishments

- Created a **zero-code interface** for high-quality data insights.
- Built a complete pipeline from file upload to AI-generated visual outputs.
- Delivered a visually pleasing and accessible app experience.

---

## Built With

- **Frontend**: React.js
- **Backend**: Flask (Python), CORS
- **AI**: Google Gemini
- **Visualization**: Matplotlib, Seaborn

---

## Getting Started

1. Start Flask backend (in `/backend`):
   ```bash
   python app.py
   ````

2. Run React frontend (in `/frontend`):

   ```bash
   npm install
   npm run start
   ```
