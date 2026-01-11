Smart Medicine Management System using QR Code
Medisophos is a team-based mini project developed to manage medicine records efficiently.
The system helps store, update, and track medicine information using a simple and user-friendly interface.

This project was created as part of an academic mini project and is maintained for learning and portfolios purpose.

Features
- Add new medicine records
- Update existing medicine details
- Delete medicine records
- View available medicines
- Basic stock management
- Clean and simple UI

Requirements:
- Python 3.10+
- pip

Install dependencies:
    pip install -r requirements.txt

Run:
    python app.py

Open in browser: http://127.0.0.1:5000

Project structure (single-folder):
medicine_qr_project/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── add_medicine.html
│   ├── view_medicine.html
│   └── update_medicine.html
└── static/
    ├── css/
    │   └── style.css
    └── qr_codes/  # auto-created at runtime


Notes:
- This is a minimal, extendable starter. It uses SQLite for simplicity.
- For production use: add authentication, validation, input sanitation, HTTPS, and role-based access.
