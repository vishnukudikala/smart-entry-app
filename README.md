# SmartEntry — Smart Event Ticketing & QR Entry System

## Tech Stack
- **Backend**: Python 3.10+, Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **QR Code**: qrcode + Pillow
- **QR Scanning**: jsQR (browser camera)

---

## Features
- 🎫 Browse & book events online
- 💳 Online payment simulation (UPI / Card / Net Banking)
- 📋 Enter personal details during booking
- 🔲 Auto-generated unique QR Code ticket
- 🔑 Unique Entry Code per booking (e.g. SE-X7K2M9P4)
- 📷 Live camera QR scanner for event entry
- 👤 Attendee details shown instantly on scan
- ✅ Duplicate scan detection (already checked-in warning)
- 🖨 Printable ticket page

---

## Local Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL
```bash
mysql -u root -p < schema.sql
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 4. Run the app
```bash
python app.py
```
Visit: http://localhost:5000

---

## Deploy on Railway (Free)

### Step 1: Create a Railway account
Go to https://railway.app and sign up.

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "SmartEntry app"
git remote add origin https://github.com/YOUR_USERNAME/smart-entry.git
git push -u origin main
```

### Step 3: Deploy on Railway
1. Go to https://railway.app/new
2. Select "Deploy from GitHub Repo"
3. Choose your repo
4. Railway will auto-detect it's a Python app

### Step 4: Add MySQL on Railway
1. In your Railway project, click "+ New"
2. Select "Database" → "MySQL"
3. Railway will create a MySQL instance
4. Copy the connection variables

### Step 5: Set Environment Variables
In Railway → Variables tab, add:
```
MYSQL_HOST=<from Railway MySQL>
MYSQL_USER=<from Railway MySQL>
MYSQL_PASSWORD=<from Railway MySQL>
MYSQL_DB=railway
SECRET_KEY=your-secret-key-here
```

### Step 6: Run schema
In Railway MySQL shell or any MySQL client, run the contents of `schema.sql`.

### Step 7: Add Procfile
Railway uses this to start your app:
```
web: python app.py
```

Your app will be live at: `https://your-app.railway.app`

---

## Deploy on Render (Free)

1. Create account at https://render.com
2. New → Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py`
5. Add a MySQL database (or use PlanetScale for free MySQL)
6. Set environment variables

---

## Deploy on PythonAnywhere (Free tier)

1. Go to https://www.pythonanywhere.com
2. Upload files via Files tab
3. Create a MySQL database in the Databases tab
4. Set up a Web App pointing to your Flask app
5. Set environment variables in the WSGI config

---

## Project Structure
```
smart_entry/
├── app.py              # Main Flask application
├── schema.sql          # MySQL database schema + sample data
├── requirements.txt    # Python dependencies
├── .env.example        # Environment config template
├── templates/
│   ├── base.html       # Base layout with navbar
│   ├── index.html      # Homepage with hero & event preview
│   ├── events.html     # All events with filters
│   ├── booking.html    # 3-step booking form
│   ├── ticket.html     # Full ticket view
│   └── scan.html       # QR scanner for event staff
├── static/
│   ├── css/
│   │   ├── style.css   # Main stylesheet
│   │   └── scan.css    # Scanner-specific styles
│   ├── js/
│   │   └── main.js     # JS utilities
│   └── qrcodes/        # Generated QR code images (auto-created)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events` | List all upcoming events |
| GET | `/api/events/<id>` | Get single event details |
| POST | `/api/book` | Book a ticket (creates QR) |
| GET | `/api/ticket/<ref>` | Get ticket by booking ref |
| POST | `/api/scan` | Scan/verify QR code |

---

## Scanning Flow
1. Event staff opens `/scan` on their device
2. Tap "Start Camera" to activate QR scanner
3. Point camera at attendee's QR code
4. App calls `/api/scan` with QR data
5. Returns attendee's full details + entry code
6. Green ✓ = Valid entry | Yellow ⚠ = Already checked in | Red ✗ = Invalid

---

## License
MIT — Free to use and modify.
