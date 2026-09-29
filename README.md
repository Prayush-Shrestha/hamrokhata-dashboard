# Hamro Khata Simple Dashboard

This version follows the simple structure of the reference `tee` project:

- React + Vite frontend
- FastAPI backend
- MySQL database
- Pandas for calculations
- Matplotlib for charts
- No Streamlit
- No React sidebar
- No Recharts
- One main dashboard API: `/api/dashboard`

## Expected MySQL table

The dashboard works with a `tasks` table using these columns:

- id
- title
- description
- employee_name
- status
- priority
- start_date
- due_date
- created_at

Status values:

- pending
- in_progress
- completed

Priority values:

- low
- medium
- high

## Backend

Open PowerShell:

```powershell
cd D:\task-hamro-khata\backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Test:

```text
http://localhost:8000/api/health
```

Then:

```text
http://localhost:8000/api/dashboard
```

## Frontend

Open another PowerShell:

```powershell
cd D:\task-hamro-khata\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```
