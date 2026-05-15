from flask import Flask, request, render_template_string, redirect, send_from_directory, jsonify, session
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "aquaflow_super_secure_key"

DB = "water.db"

ADMIN_PASSWORD = "aquaflowadmin"

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
background:#07111f;
background-image:
radial-gradient(circle at top left, rgba(0,183,255,0.22), transparent 30%),
radial-gradient(circle at bottom right, rgba(37,99,235,0.20), transparent 30%);
min-height:100vh;
padding:40px 20px;
color:white;
}

.container{
width:100%;
max-width:1200px;
margin:auto;
background:rgba(8,15,28,0.72);
backdrop-filter:blur(18px);
border:1px solid rgba(255,255,255,0.08);
border-radius:30px;
padding:40px;
box-shadow:0 20px 60px rgba(0,0,0,0.45);
}

.logo{
font-size:62px;
margin-bottom:8px;
line-height:1;
}

h1,h2{
text-align:center;
margin-bottom:10px;
}

.subtitle{
color:#94a3b8;
margin-bottom:35px;
font-size:15px;
line-height:1.6;
}

.nav-grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
gap:15px;
margin-bottom:30px;
}

button{
width:100%;
padding:16px;
border:none;
border-radius:16px;
background:linear-gradient(270deg,#0ea5e9,#2563eb,#06b6d4);
background-size:400% 400%;
animation:gradientMove 8s ease infinite;
color:white;
font-weight:700;
cursor:pointer;
font-size:15px;
transition:0.25s ease;
box-shadow:0 12px 30px rgba(37,99,235,0.25);
}

button:hover{
transform:translateY(-2px);
filter:brightness(1.05);
}

@keyframes gradientMove{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

input{
width:100%;
padding:17px;
margin-bottom:16px;
border:1px solid rgba(255,255,255,0.08);
border-radius:16px;
background:rgba(255,255,255,0.05);
color:white;
font-size:15px;
outline:none;
transition:0.2s;
}

input:focus{
border-color:#38bdf8;
background:rgba(255,255,255,0.08);
}

input::placeholder{
color:#b7c2d2;
}

.message{
text-align:center;
margin-top:20px;
font-weight:600;
}

.stat-grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:15px;
margin:25px 0;
}

.stat-card{
background:linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.03));
padding:24px;
border-radius:24px;
text-align:left;
border:1px solid rgba(255,255,255,0.06);
backdrop-filter:blur(10px);
}

.stat-card h3{
font-size:14px;
color:#b6c3d2;
margin-bottom:10px;
}

.stat-card p{
font-size:34px;
font-weight:800;
margin-top:6px;
}

.search-box{
margin-bottom:20px;
}

.customer-card{
background:#0b1728;
padding:22px;
border-radius:22px;
margin-bottom:16px;
border:1px solid rgba(255,255,255,0.06);
line-height:2;
transition:0.2s;
}

.customer-card:hover{
transform:translateY(-2px);
border-color:rgba(56,189,248,0.25);
}

.topbar{
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:25px;
flex-wrap:wrap;
gap:10px;
}

.live-clock{
background:rgba(255,255,255,0.10);
padding:10px 18px;
border-radius:14px;
font-weight:600;
}

.plan-grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:18px;
margin:25px 0 35px 0;
}

.plan-card{
background:#0b1728;
border:1px solid rgba(255,255,255,0.06);
padding:28px 24px;
border-radius:26px;
text-align:left;
transition:0.25s;
position:relative;
overflow:hidden;
}

.plan-card:hover{
transform:translateY(-4px);
border-color:rgba(56,189,248,0.35);
}

.plan-price{
font-size:30px;
font-weight:800;
margin:10px 0;
}

.badge{
display:inline-flex;
align-items:center;
justify-content:center;
padding:7px 14px;
border-radius:999px;
background:rgba(14,165,233,0.15);
color:#7dd3fc;
font-size:11px;
font-weight:700;
margin-top:16px;
letter-spacing:1px;
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

.container{
padding:22px;
border-radius:24px;
}

.topbar{
flex-direction:column;
align-items:flex-start;
}

.stat-grid{
grid-template-columns:1fr;
}

.plan-grid{
grid-template-columns:1fr;
}

.logo{
font-size:42px;
}

h1{
font-size:28px;
}

/* ---- Custom Additions ---- */
.glow-line{
height:1px;
background:linear-gradient(to right,transparent,#38bdf8,transparent);
margin:30px 0;
opacity:0.5;
}

.live-dot{
width:10px;
height:10px;
border-radius:50%;
background:#22c55e;
display:inline-block;
margin-right:8px;
box-shadow:0 0 15px #22c55e;
animation:pulse 1.5s infinite;
}

@keyframes pulse{
0%{transform:scale(1);opacity:1;}
50%{transform:scale(1.3);opacity:0.6;}
100%{transform:scale(1);opacity:1;}
}

.quick-actions{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:18px;
margin-top:20px;
}

.action-card{
background:#0f1c31;
padding:24px;
border-radius:24px;
border:1px solid rgba(255,255,255,0.06);
transition:0.25s;
}

.action-card:hover{
transform:translateY(-4px);
border-color:rgba(56,189,248,0.4);
}

.action-card h3{
margin-bottom:10px;
}

.action-card p{
color:#94a3b8;
font-size:14px;
line-height:1.7;
}

.hero-banner{
background:linear-gradient(135deg,#0ea5e9,#2563eb);
padding:35px;
border-radius:28px;
margin-bottom:30px;
position:relative;
overflow:hidden;
}

.hero-banner h2{
text-align:left;
font-size:34px;
margin-bottom:12px;
}

.hero-banner p{
color:rgba(255,255,255,0.88);
line-height:1.8;
max-width:700px;
}

.hero-banner::after{
content:'';
position:absolute;
width:300px;
height:300px;
background:rgba(255,255,255,0.08);
border-radius:50%;
right:-120px;
top:-120px;
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

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():

    message = ""

    if request.method == 'POST':

        password = request.form['password']

        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/')

        else:
            message = '❌ Wrong Password'

    return render_template_string(STYLE + """

    <div class="container" style="max-width:500px;">

        <div class="logo">🔐</div>

        <h1>Admin Login</h1>

        <div class="subtitle">
        Secure AquaFlow administration access.
        </div>

        <form method="post">

            <input type="password"
            name="password"
            placeholder="Enter Admin Password"
            required>

            <button type="submit">
                LOGIN
            </button>

        </form>

        <div class="message">{{message}}</div>

    </div>

    """, message=message)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if 'admin' not in session:
        return redirect('/login')

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

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM customers")
    total_customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM recharge_requests WHERE status='pending'")
    pending_requests = c.fetchone()[0]

    c.execute("SELECT SUM(amount) FROM transactions WHERE type='deduct'")
    total_revenue = c.fetchone()[0]

    if total_revenue is None:
        total_revenue = 0

    conn.close()

    return render_template_string(STYLE + """

    <div class="container">

    <div class="topbar">
        <div>
            <div class="logo">🌊</div>
            <h1>AquaFlow Luxe</h1>
        </div>

        <div class="live-clock" id="clock">
            Loading Time...
        </div>
    </div>

    <div class="subtitle">
    <span class="live-dot"></span>
    Premium smart water management platform with luxury dashboard analytics and seamless recharge experience.
    </div>

    <div class="hero-banner">
        <h2>Next Generation Water Distribution</h2>
        <p>
            AquaFlow Luxe helps you manage customers, monitor recharge requests, track live revenue and automate your smart water delivery workflow with a premium dashboard experience.
        </p>
    </div>

    <div class="stat-grid">

        <div class="stat-card">
            <h3>Total Customers</h3>
            <p>{{total_customers}}</p>
        </div>

        <div class="stat-card">
            <h3>Pending Requests</h3>
            <p>{{pending_requests}}</p>
        </div>

        <div class="stat-card">
            <h3>Total Revenue</h3>
            <p>₹{{total_revenue}}</p>
        </div>

        <div class="stat-card">
            <h3>System Status</h3>
            <p style="color:#22c55e;">LIVE</p>
        </div>

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

        <a href="/logout">
            <button>🚪 Logout</button>
        </a>

    </div>

    <div class="plan-grid">

        <div class="plan-card">
            <h3>Starter</h3>
            <div class="plan-price">₹99</div>
            <div style="margin-top:10px;color:#94a3b8;">Perfect for regular households</div>
            <div class="badge">POPULAR</div>
        </div>

        <div class="plan-card">
            <h3>Premium</h3>
            <div class="plan-price">₹499</div>
            <div style="margin-top:10px;color:#94a3b8;">Most popular commercial plan</div>
            <div class="badge">BEST VALUE</div>
        </div>

        <div class="plan-card">
            <h3>Elite</h3>
            <div class="plan-price">₹999</div>
            <div style="margin-top:10px;color:#94a3b8;">High-volume premium distribution</div>
            <div class="badge">VIP</div>
        </div>

    </div>

    <div class="glow-line"></div>

    <div class="quick-actions">

        <div class="action-card">
            <h3>⚡ Fast Recharge</h3>
            <p>
                Users can instantly submit recharge proof and get wallet balance approval from admin.
            </p>
        </div>

        <div class="action-card">
            <h3>📈 Live Analytics</h3>
            <p>
                Track total customers, sales revenue and pending recharge approvals in real-time.
            </p>
        </div>

        <div class="action-card">
            <h3>🔐 Secure Management</h3>
            <p>
                Customer records and recharge history are securely managed using SQLite database storage.
            </p>
        </div>

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

    <script>
    function updateClock(){
        const now = new Date();
        document.getElementById('clock').innerHTML = now.toLocaleString();
    }

    setInterval(updateClock,1000);
    updateClock();
    </script>

    </div>

    """,
    message=message,
    balance=balance,
    name=name,
    total_customers=total_customers,
    pending_requests=pending_requests,
    total_revenue=total_revenue
    )

# ---------- ADD CUSTOMER ----------
@app.route("/add", methods=["GET", "POST"])
def add():
    if 'admin' not in session:
        return redirect('/login')

    message = ""

    if request.method == "POST":

        card_id = "AQ" + str(int(datetime.now().timestamp()))[-6:]
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

    <div class="subtitle">
    Card ID Auto Generated
    </div>

    <form method="post">

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
    if 'admin' not in session:
        return redirect('/login')

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

        <input type="number" name="amount" placeholder="Recharge Amount" required>

        <div class="qr-box">

            <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=atharvkurundkar@okicici&pn=AquaFlow&cu=INR">

            <br>

            <button
onclick="window.location.href='upi://pay?pa=atharvkurundkar@okicici&pn=AquaFlow&cu=INR'"
type="button">
📲 Open UPI App
</button>

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
    if 'admin' not in session:
        return redirect('/login')

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

        print(f"Recharge Approved -> {card_id} | Amount: {amount}")

        conn.commit()

    conn.close()

    return redirect("/requests")

# ---------- CUSTOMERS ----------
@app.route("/customers")
def customers():
    if 'admin' not in session:
        return redirect('/login')

    search = request.args.get("search", "")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if search:

        c.execute('''
        SELECT card_id,name,mobile,balance
        FROM customers
        WHERE name LIKE ? OR card_id LIKE ? OR mobile LIKE ?
        ORDER BY id DESC
        ''', (f'%{search}%', f'%{search}%', f'%{search}%'))

    else:

        c.execute('''
        SELECT card_id,name,mobile,balance
        FROM customers
        ORDER BY id DESC
        ''')

    customers = c.fetchall()

    conn.close()

    return render_template_string(STYLE + """

    <div class="container" style="max-width:900px;">

    <div class="logo">👥</div>

    <h1>Customers</h1>
    <div class="subtitle">
    Manage all registered AquaFlow customers from one premium dashboard.
    </div>

    <form method="get" class="search-box">
        <input
        type="text"
        name="search"
        placeholder="Search customer"
        value="{{search}}">

        <button type="submit">🔍 Search</button>
    </form>

    {% for c in customers %}

    <div class="customer-card">

        <b>🪪 Card ID:</b> {{c[0]}}<br>
        <b>👤 Name:</b> {{c[1]}}<br>
        <b>📱 Mobile:</b> {{c[2]}}<br>
        <b>💰 Balance:</b>
        <span style="color:{% if c[3] < 50 %}#ef4444{% else %}#22c55e{% endif %};font-weight:700;">
        ₹{{c[3]}}
        </span>

        <br>

        <img
        src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={{c[0]}}"
        style="margin-top:15px;border-radius:16px;background:white;padding:10px;">

    </div>

    {% endfor %}

    <br>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, customers=customers, search=search)

# ---------- REPORT ----------
@app.route("/report")
def report():
    if 'admin' not in session:
        return redirect('/login')

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
    <div class="subtitle">
    Live business insights and revenue tracking dashboard.
    </div>

    <div style="margin-top:30px; line-height:2;">

        <h2>Total Water Sales: {{jars}}</h2>

        <h2>Total Revenue: ₹{{revenue}}</h2>

    </div>

    <div class="glow-line"></div>

    <div class="quick-actions">

        <div class="action-card">
            <h3>📈 Revenue Growth</h3>
            <p>
                AquaFlow is actively tracking live sales and recharge performance.
            </p>
        </div>

        <div class="action-card">
            <h3>🚰 Smart Distribution</h3>
            <p>
                Automated wallet deduction helps streamline water distribution.
            </p>
        </div>

    </div>

    <a href="/">
        <button>⬅ Back</button>
    </a>

    </div>

    """, jars=jars, revenue=revenue)

# ---------- API STATS ----------
@app.route('/api/stats')
def api_stats():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM customers")
    customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM recharge_requests WHERE status='pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT SUM(amount) FROM transactions WHERE type='deduct'")
    revenue = c.fetchone()[0]

    if revenue is None:
        revenue = 0

    conn.close()

    return jsonify({
        "customers": customers,
        "pending_requests": pending,
        "revenue": revenue,
        "status": "LIVE"
    })

# ---------- UPLOADS ----------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)