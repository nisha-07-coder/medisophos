from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, qrcode, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-random-key'
DB = 'medicine.db'

# Ensure QR folder exists
os.makedirs('static/qr_codes', exist_ok=True)

# Initialize database
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS medicine (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        manufacturer TEXT,
                        manufacture_date TEXT,
                        expiry_date TEXT,
                        price REAL,
                        additional_info TEXT,
                        qr_path TEXT,
                        last_updated TEXT
                        )''')
init_db()

# Fetch all medicines
def get_all_medicines():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM medicine ORDER BY id DESC')
        return cur.fetchall()

# Dashboard
@app.route('/')
def dashboard():
    meds = get_all_medicines()
    total = len(meds)
    near_expiry = 0
    today = datetime.today().date()
    for m in meds:
        try:
            exp = datetime.strptime(m['expiry_date'], '%Y-%m-%d').date()
            if (exp - today).days <= 30:
                near_expiry += 1
        except Exception:
            pass
    return render_template('dashboard.html', medicines=meds, total=total, near_expiry=near_expiry)

# Add medicine
@app.route('/add', methods=['GET','POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        manufacturer = request.form.get('manufacturer').strip()
        mdate = request.form.get('mdate').strip()
        edate = request.form.get('edate').strip()
        price = request.form.get('price') or 0
        info = request.form.get('info') or ''

        if not name or not edate:
            flash('Name and expiry date are required.', 'danger')
            return redirect(url_for('add_medicine'))

        last_updated = datetime.now().isoformat()
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO medicine 
                        (name, manufacturer, manufacture_date, expiry_date, price, additional_info, qr_path, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (name, manufacturer, mdate, edate, price, info, '', last_updated))
            conn.commit()
            mid = cur.lastrowid

        # QR Code with medicine text
        medicine_text = f"""
Name: {name}
Manufacturer: {manufacturer}
Manufacture Date: {mdate}
Expiry Date: {edate}
Price: {price}
Additional Info: {info}
"""
        qr_img = qrcode.make(medicine_text)
        safe_name = name.replace(' ', '_')[:40]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        qr_filename = f"{safe_name}_{timestamp}.png"
        qr_path = os.path.join('static', 'qr_codes', qr_filename)
        qr_img.save(qr_path)

        with sqlite3.connect(DB) as conn:
            conn.execute('UPDATE medicine SET qr_path=? WHERE id=?', (qr_path, mid))
            conn.commit()

        flash('Medicine added successfully with QR code.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_medicine.html')

# View medicine
@app.route('/view/<int:mid>')
def view_medicine(mid):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM medicine WHERE id=?', (mid,))
        med = cur.fetchone()
    if not med:
        flash('Medicine not found.', 'warning')
        return redirect(url_for('dashboard'))
    return render_template('view_medicine.html', medicine=med)

# Update medicine
@app.route('/update/<int:mid>', methods=['GET','POST'])
def update_medicine(mid):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM medicine WHERE id=?', (mid,))
        med = cur.fetchone()
    if not med:
        flash('Medicine not found.', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name').strip()
        manufacturer = request.form.get('manufacturer').strip()
        mdate = request.form.get('mdate').strip()
        edate = request.form.get('edate').strip()
        price = request.form.get('price') or 0
        info = request.form.get('info') or ''

        # QR code
        medicine_text = f"""
Name: {name}
Manufacturer: {manufacturer}
Manufacture Date: {mdate}
Expiry Date: {edate}
Price: {price}
Additional Info: {info}
"""
        qr_img = qrcode.make(medicine_text)
        safe_name = name.replace(' ', '_')[:40]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        qr_filename = f"{safe_name}_{timestamp}.png"
        qr_path = os.path.join('static', 'qr_codes', qr_filename)
        qr_img.save(qr_path)

        last_updated = datetime.now().isoformat()
        with sqlite3.connect(DB) as conn:
            conn.execute('''UPDATE medicine SET name=?, manufacturer=?, manufacture_date=?, expiry_date=?, 
                            price=?, additional_info=?, qr_path=?, last_updated=? WHERE id=?''',
                         (name, manufacturer, mdate, edate, price, info, qr_path, last_updated, mid))
        flash('Medicine updated successfully with updated QR text.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_medicine.html', medicine=med)

# Delete medicine
@app.route('/delete/<int:mid>', methods=['POST'])
def delete_medicine(mid):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute('SELECT qr_path FROM medicine WHERE id=?', (mid,))
        row = cur.fetchone()
        if row and row[0] and os.path.exists(row[0]):
            os.remove(row[0])
        conn.execute('DELETE FROM medicine WHERE id=?', (mid,))
    flash('Medicine deleted.', 'info')
    return redirect(url_for('dashboard'))

# Search
@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        with sqlite3.connect(DB) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM medicine WHERE name LIKE ? ORDER BY id DESC", (f'%{q}%',))
            results = cur.fetchall()
    return render_template('dashboard.html', medicines=results, total=len(results), near_expiry=0)

if __name__ == '__main__':
    app.run(debug=True)
