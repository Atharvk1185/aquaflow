from flask import Flask, request, render_template_string, redirect, send_from_directory
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

DB = "water.db"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- STYLE ----------
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:'Poppins',sans-serif;
}

body{
background:
linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55)),
url('https://images.unsplash.com/photo-1502741338009-cac2772e18bc?q=80&w=2070&auto=format&fit=crop');
background-size:cover;
background-position:center;
background-attachment:fixed;
min-height:100vh;
display:flex;
justify-content:center;
align-items:center;
padding:30px;
color:white;
}

.container{
width:100%;
max-width:650px;
background:rgba(255,255,255,0.08);
backdrop-filter:blur(20px);
border:1px solid rgba(255,255,255,0.15);
border-radius:30px;
padding:35px;
box-shadow:0 20px 50px rgba(0,0,0,0.35);
}

.logo{
font-size:55px;
text-align:center;
margin-bottom:15px;
}

h1,h2{
text-align:center;
margin-bottom:10px;
}

.subtitle{
text-align:center;
color:#d1d5db;
margin-bottom:30px;
}

.nav-grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:15px;
margin-bottom:30px;
}

button{
width:100%;
padding:16px;
border:none;
border-radius:18px;
background:linear-gradient(135deg,#00c6ff,#0072ff);
color:white;
font-weight:700;
cursor:pointer;
font-size:15px;
transition:0.3s;
}

button:hover{
transform:translateY(-3px);
}

input{
width:100%;
padding:16px;
margin-bottom:16px;
border:none;
border-radius:16px;
background:rgba(255,255,255,0.12);
color:white;
font-size:15px;
outline:none;
}

input::placeholder{
color:#d1d5db;
}

.message{
text-align:center;
margin-top:20px;
font-weight:600;
}

.qr-box{
text-align:center;
margin-top:25px;
}

.qr-box img{
width:240px;
height:240px;
background:white;
padding:12px;
border-radius:25px;
}

table{
width:100%;
border-collapse:collapse;
margin-top:20px;
}

th,td{
padding:14px;
border-bottom:1px solid rgba(255,255,255,0.1);
text-align:left;
}

a{
text-decoration:none;
}

@media(max-width:700px){

.nav-grid{
grid-template-columns:1fr;
}

.container{
padding:22px;
}

}
</style>
"""

# ---------- DATABASE ----------
def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT UNIQUE,
        name TEXT,
        mobile TEXT,
        balance REAL DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT,
        amount REAL,
        type TEXT,
        timestamp TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS recharge_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT,
        amount REAL,
        screenshot TEXT,
        status TEXT DEFAULT 'pending',
        timestamp TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():

    message = ""
    balance = ""
    name = ""

    if request.method == "POST":

        card_id = request.form["card_id"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "SELECT name, balance FROM customers WHERE card_id=?",
            (card_id,)
        )

        result = c.fetchone()

        if result:

            name, balance = result

            if balance >= 15:

                new_balance = balance - 15

                c.execute(
                    "UPDATE customers SET balance=? WHERE card_id=?",
                    (new_balance, card_id)
                )

                c.execute('''
                INSERT INTO transactions
                (card_id, amount, type, timestamp)
                VALUES (?, ?, 'deduct', ?)
                ''', (card_id, 15, datetime.now()))

                conn.commit()

                message = "✅ Water Dispensed Successfully"
                balance = new_balance

            else:
                message = "❌ Low Balance"

        else:
            message = "❌ Card Not Found"

        conn.close()

    return render_template_string(STYLE + """

    <div class="container">

    <div class="logo">🌊</div>

    <h1>AquaFlow Luxe</h1>

    <div class="subtitle">
    Premium Smart Water Management
    </div>

    <div class="nav-grid">

        <a href="/add">
            <button>➕ Add Customer</button>
        </a>

        <a href="/recharge">
            <button>💳 Recharge</button>
        </a>

        <a href="/customers">
            <button>👥 Customers</button>
        </a>

        <a href="/report">
            <button>📊 Reports</button>
        </a>

        <a href="/requests">
            <button>🧾 Recharge Requests</button>
        </a>

    </div>

    <form method="post">

        <input name="card_id" placeholder="Enter Card ID" required>

        <button type="submit">
            🚰 Deduct ₹15
        </button>

    </form>

    <div class="message">
        {{message}}
    </div>

    <br>

    <div>
        <b>Name:</b> {{name}}<br><br>
        <b>Balance:</b> ₹{{balance}}
    </div>

    </div>

    """, message=message, balance=balance, name=name)

# ---------- ADD CUSTOMER ----------
@app.route("/add", methods=["GET", "POST"])
def add():

    message = ""

    if request.method == "POST":

        card_id = request.form["card_id"]
        name = request.form["name"]
        mobile = request.form["mobile"]

        try:

            conn = sqlite3.connect(DB)
            c = conn.cursor()

            c.execute('''
            INSERT INTO customers(card_id,name,mobile)
            VALUES(?,?,?)
            ''', (card_id, name, mobile))

            conn.commit()
            conn.close()

            message = "✅ Customer Added"

        except:
            message = "❌ Card Already Exists"

    return render_template_string(STYLE + """

    <div class="container">

    <div class="logo">➕</div>

    <h2>Add Customer</h2>

    <form method="post">

        <input name="card_id" placeholder="Card ID" required>

        <input name="name" placeholder="Customer Name" required>

        <input name="mobile" placeholder="Mobile Number" required>

        <button type="submit">
            ADD CUSTOMER
        </button>

    </form>

    <div class="message">{{message}}</div>

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, message=message)

# ---------- RECHARGE ----------
@app.route("/recharge", methods=["GET", "POST"])
def recharge():

    message = ""

    if request.method == "POST":

        card_id = request.form["card_id"]
        amount = float(request.form["amount"])

        screenshot = request.files["screenshot"]

        filename = secure_filename(screenshot.filename)

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        screenshot.save(filepath)

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM customers WHERE card_id=?",
            (card_id,)
        )

        customer = c.fetchone()

        if customer:

            c.execute('''
            INSERT INTO recharge_requests
            (card_id, amount, screenshot, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (card_id, amount, filename, datetime.now()))

            conn.commit()

            message = "✅ Recharge Request Submitted"

        else:
            message = "❌ Customer Not Found"

        conn.close()

    return render_template_string(STYLE + """

    <div class="container">

    <div class="logo">💳</div>

    <h2>Recharge Wallet</h2>

    <div class="subtitle">
    Scan QR & Upload Payment Screenshot
    </div>

    <form method="post" enctype="multipart/form-data">

        <input name="card_id" placeholder="Card ID" required>

        <input name="amount" placeholder="Recharge Amount" required>

        <div class="qr-box">

            <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=atharvkurundkar@okicici&pn=AquaFlow&cu=INR">

            <br><br>

            <div>
                UPI ID: atharvkurundkar@okicici
            </div>

        </div>

        <br>

        <input type="file" name="screenshot" required>

        <button type="submit">
            📤 Submit Payment Proof
        </button>

    </form>

    <div class="message">{{message}}</div>

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, message=message)

# ---------- RECHARGE REQUESTS ----------
@app.route("/requests")
def requests_page():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
    SELECT *
    FROM recharge_requests
    ORDER BY id DESC
    ''')

    data = c.fetchall()

    conn.close()

    return render_template_string(STYLE + """

    <div class="container" style="max-width:1100px;">

    <div class="logo">🧾</div>

    <h1>Recharge Requests</h1>

    <table>

    <tr>
        <th>ID</th>
        <th>Card</th>
        <th>Amount</th>
        <th>Screenshot</th>
        <th>Status</th>
        <th>Action</th>
    </tr>

    {% for r in data %}

    <tr>

        <td>{{r[0]}}</td>
        <td>{{r[1]}}</td>
        <td>₹{{r[2]}}</td>

        <td>
            <a href="/uploads/{{r[3]}}" target="_blank">
                View
            </a>
        </td>

        <td>{{r[4]}}</td>

        <td>

            {% if r[4] == 'pending' %}

            <a href="/approve/{{r[0]}}">
                <button>Approve</button>
            </a>

            {% endif %}

        </td>

    </tr>

    {% endfor %}

    </table>

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, data=data)

# ---------- APPROVE ----------
@app.route("/approve/<int:req_id>")
def approve(req_id):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
    SELECT card_id, amount
    FROM recharge_requests
    WHERE id=?
    ''', (req_id,))

    data = c.fetchone()

    if data:

        card_id = data[0]
        amount = data[1]

        c.execute('''
        UPDATE customers
        SET balance = balance + ?
        WHERE card_id=?
        ''', (amount, card_id))

        c.execute('''
        UPDATE recharge_requests
        SET status='approved'
        WHERE id=?
        ''', (req_id,))

        c.execute('''
        INSERT INTO transactions
        (card_id, amount, type, timestamp)
        VALUES (?, ?, 'recharge', ?)
        ''', (card_id, amount, datetime.now()))

        conn.commit()

    conn.close()

    return redirect("/requests")

# ---------- CUSTOMERS ----------
@app.route("/customers")
def customers():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
    SELECT card_id,name,mobile,balance
    FROM customers
    ORDER BY id DESC
    ''')

    customers = c.fetchall()

    conn.close()

    return render_template_string(STYLE + """

    <div class="container" style="max-width:1000px;">

    <div class="logo">👥</div>

    <h1>Customers</h1>

    <table>

    <tr>
        <th>Card ID</th>
        <th>Name</th>
        <th>Mobile</th>
        <th>Balance</th>
    </tr>

    {% for c in customers %}

    <tr>
        <td>{{c[0]}}</td>
        <td>{{c[1]}}</td>
        <td>{{c[2]}}</td>
        <td>₹{{c[3]}}</td>
    </tr>

    {% endfor %}

    </table>

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, customers=customers)

# ---------- REPORT ----------
@app.route("/report")
def report():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    SELECT COUNT(*)
    FROM transactions
    WHERE type='deduct'
    """)

    jars = c.fetchone()[0]

    c.execute("""
    SELECT SUM(amount)
    FROM transactions
    WHERE type='deduct'
    """)

    revenue = c.fetchone()[0]

    if revenue is None:
        revenue = 0

    conn.close()

    return render_template_string(STYLE + """

    <div class="container">

    <div class="logo">📊</div>

    <h1>Business Report</h1>

    <div style="margin-top:30px; line-height:2;">

        <h2>Total Water Sales: {{jars}}</h2>

        <h2>Total Revenue: ₹{{revenue}}</h2>

    </div>

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, jars=jars, revenue=revenue)

# ---------- UPLOADS ----------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)