# 🔬 Lab Management & Analytics System

A comprehensive, professional Lab Management System built with Python Streamlit. Chrome-based and mobile-friendly.

## 📋 Features

### 👥 User Roles (3 Users Total)

#### Staff Users (2)
- ✅ Can Add new entries
- ✅ Can Edit during punching only
- 🔒 After Save/Print → Record locked
- ❌ Cannot Delete any record
- ❌ Cannot view activity logs

#### Admin User (1)
- ✅ Can Add / Edit / Delete any record at any time
- ✅ Can unlock locked records
- ✅ Can view full activity logs
- ✅ Can change system theme (colors)
- ✅ Can backup database

### 📋 10 Performas (Categories)
1. Data Retrieval Reports
2. Lab Activity
3. Special Checking in Lab
4. Daily Checking Report
5. Monthly Site Checking Report
6. AMI MDI TCPs
7. Audit Record
8. Court Cases
9. Log Book Record
10. TA/DA Record

### 📊 Data Entry Columns
- S.No (Auto Increment)
- Sub-Division
- Reference No (Strict 14-digit validation)
- Name
- Tariff
- Load
- Meter No
- Make
- MCO No
- MCO Date
- Bill Reading
- Meter Reading
- Difference (Auto Calculation)
- Status
- Remarks
- Entry_Date (Auto Timestamp)

### 📜 Activity Tracking
- Full activity record of every session
- Tracks: Add, Edit, Delete, Print actions
- Records: Username, Session ID, Performa Name, Action Type, Reference No, Date & Time

### 🎨 Theme Customization (Admin Only)
- Background Color
- Sidebar Color
- Text Color
- Card Color
- Primary/Accent Color
- Preset themes available

### 🔍 Search & Filter
- Global search by Name, Meter No, Reference No
- Date range filter in every performa
- Export to Excel, PDF & CSV

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to project directory:**
```bash
cd "c:\Users\PC\Pictures\Lab Report and Analytics"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Open in browser:**
```
http://localhost:8501
```

## 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@123 |
| Staff | staff1 | Staff@123 |
| Staff | staff2 | Staff@123 |

## 📱 Mobile Responsive
The application is fully responsive and works on mobile devices.

## ☁️ Cloud Deployment

### Deploy to Streamlit Cloud
1. Push code to GitHub (recommended branch: `main`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** and connect your GitHub repository
4. Set:
	- **Branch:** `main`
	- **Main file path:** `app.py`
5. Click **Deploy**

#### Streamlit Cloud Notes
- Python version is pinned via `runtime.txt` (`python-3.11`)
- Dependencies auto-install from `requirements.txt`
- `.streamlit/secrets.toml` is ignored by Git; add secrets from Streamlit Cloud **App Settings → Secrets**
- For persistent cloud data, set PostgreSQL URL in secrets:
	```toml
	DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DBNAME"
	```
- App automatically uses PostgreSQL when `DATABASE_URL` is set, otherwise SQLite fallback.
- SQLite (`lab_management.db`) is local-file based. On Streamlit Cloud, local file storage is not guaranteed for long-term persistence. For production persistence, move to a managed database (e.g., PostgreSQL/Supabase).

### Deploy to Heroku
1. Create `Procfile`:
```
web: sh setup.sh && streamlit run app.py
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

## 📁 Project Structure

```
Lab Report and Analytics/
├── app.py              # Main application
├── database.py         # Database operations
├── auth.py             # Authentication module
├── utils.py            # Helper functions
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── README.md           # Documentation
├── .streamlit/
│   └── config.toml     # Streamlit configuration
└── lab_management.db   # SQLite database (auto-created)
```

## 🛡️ Security Features
- Password encryption using bcrypt
- Session-based authentication
- Role-based access control
- Activity logging for audit trail

## 📞 Support
For issues or questions, please contact the system administrator.

---
**Version:** 1.0.0  
**Built with:** Python Streamlit
