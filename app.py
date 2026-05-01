from flask import Flask, request, render_template_string, redirect, send_from_directory, jsonify
import sqlite3
from datetime import datetime
import razorpay

app = Flask(__name__)
DB = "water.db"
RAZORPAY_KEY_ID = "rzp_test_SjvV9KRZXcWeL9"
RAZORPAY_KEY_SECRET = "DVnW4o5WEtUpz1V7hDzG0ieW"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Serve local QR image
@app.route('/qr-image')
def qr_image():
    import os

    possible_files = [
        'GooglePay_QR.png',
        'GooglePay_QR.jpg',
        'GooglePay_QR.jpeg',
        'qr.png',
        'qr.jpg',
        'qr.jpeg'
    ]

    for file in possible_files:
        if os.path.exists(file):
            return send_from_directory('.', file)

    return "QR image not found"

# ---------- CSS STYLE ----------
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
    min-height:100vh;
    background:
        linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
        url('https://images.unsplash.com/photo-1502741338009-cac2772e18bc?q=80&w=2000&auto=format&fit=crop');
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
    display:flex;
    justify-content:center;
    align-items:center;
    padding:40px 20px;
    overflow-x:hidden;
}

.container{
    width:100%;
    max-width:520px;
    background:rgba(255,255,255,0.08);
    backdrop-filter:blur(18px);
    -webkit-backdrop-filter:blur(18px);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:35px;
    padding:40px;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.45);
    position:relative;
    overflow:hidden;
}

.container::before{
    content:'';
    position:absolute;
    width:220px;
    height:220px;
    background:rgba(59,130,246,0.25);
    border-radius:50%;
    top:-120px;
    right:-100px;
    filter:blur(40px);
}

.logo{
    width:100px;
    height:100px;
    margin:0 auto 20px;
    border-radius:30px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:45px;
    background:linear-gradient(135deg,#00c6ff,#0072ff);
    box-shadow:0 10px 30px rgba(0,114,255,0.45);
}

h1,h2{
    text-align:center;
    color:white;
    font-weight:700;
}

h1{
    font-size:40px;
    margin-bottom:8px;
}

.subtitle{
    text-align:center;
    color:rgba(255,255,255,0.75);
    margin-bottom:35px;
    font-size:14px;
    line-height:1.7;
}

.nav-grid{
    display:grid;
    gap:16px;
    margin-bottom:30px;
}

.menu-btn{
    text-decoration:none;
}

button{
    width:100%;
    padding:18px;
    border:none;
    border-radius:18px;
    background:linear-gradient(135deg,#00c6ff,#0072ff);
    color:white;
    font-size:15px;
    font-weight:600;
    cursor:pointer;
    transition:0.3s;
    box-shadow:0 8px 25px rgba(0,114,255,0.35);
}

button:hover{
    transform:translateY(-3px) scale(1.02);
    box-shadow:0 12px 30px rgba(0,114,255,0.45);
}

.section,
.info,
.qr-box{
    background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:25px;
    padding:25px;
}

input{
    width:100%;
    padding:18px;
    margin-bottom:18px;
    border:none;
    border-radius:18px;
    background:rgba(255,255,255,0.08);
    color:white;
    font-size:15px;
    outline:none;
    transition:0.3s;
}

input::placeholder{
    color:rgba(255,255,255,0.6);
}

input:focus{
    background:rgba(255,255,255,0.12);
    box-shadow:0 0 0 4px rgba(0,198,255,0.2);
}

.message{
    text-align:center;
    margin-top:22px;
    color:white;
    font-weight:500;
}

.info{
    margin-top:24px;
}

.info p,
.info h3{
    margin-bottom:14px;
    color:white;
}

.qr-box{
    margin-top:25px;
    text-align:center;
}

.qr-box img{
    width:240px;
    height:240px;
    border-radius:25px;
    background:white;
    padding:10px;
    box-shadow:0 10px 30px rgba(0,0,0,0.35);
}

.qr-title{
    color:white;
    font-size:16px;
    font-weight:600;
    margin-bottom:14px;
}

.upi-id{
    color:rgba(255,255,255,0.65);
    font-size:14px;
}

.back-btn{
    margin-top:24px;
}

table{
    color:white;
}

th{
    background:rgba(255,255,255,0.08);
}

td,th{
    padding:18px;
}

tr{
    border-bottom:1px solid rgba(255,255,255,0.08);
}

hr{
    border:none;
    height:1px;
    background:rgba(255,255,255,0.1);
    margin:28px 0;
}

@media(max-width:600px){

    .container{
        padding:28px 22px;
        border-radius:28px;
    }

    h1{
        font-size:30px;
    }

    .logo{
        width:85px;
        height:85px;
        font-size:38px;
    }
}

</style>
"""

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT UNIQUE,
        name TEXT,
        mobile TEXT,
        balance REAL DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT,
        amount REAL,
        type TEXT,
        timestamp TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------- MAIN SCREEN ----------
@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    balance = ""
    name = ""

    if request.method == "POST":
        card_id = request.form["card_id"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("SELECT name, balance FROM customers WHERE card_id=?", (card_id,))
        result = c.fetchone()

        if result:
            name, balance = result

            if balance >= 15:
                new_balance = balance - 15

                c.execute("UPDATE customers SET balance=? WHERE card_id=?",
                          (new_balance, card_id))

                c.execute("INSERT INTO transactions (card_id, amount, type, timestamp) VALUES (?, ?, 'deduct', ?)",
                          (card_id, 15, datetime.now()))

                conn.commit()

                message = "✅ Fill Allowed"
                balance = new_balance

            else:
                message = "❌ Low Balance"

        else:
            message = "❌ Card Not Found"

        conn.close()

    return render_template_string(STYLE + """
    <div class="container">

    <div class="logo">💧</div>
    <h1>AquaFlow Luxe</h1>
    <div class="subtitle">Luxury Smart Water Operations Platform</div>

    <div class="nav-grid">
    <a class="menu-btn" href="/add">
        <button>➕ Add Customer</button>
    </a>

    <a class="menu-btn" href="/recharge">
        <button>💳 Recharge Wallet</button>
    </a>

    <a class="menu-btn" href="/report">
        <button>📊 Business Analytics</button>
    </a>

    <a class="menu-btn" href="/customers">
        <button>👥 View Customers</button>
    </a>
    </div>

    <hr>

    <div class="section"><h2>Deduct ₹15</h2>

    <form method="post" onsubmit="return confirmDeduction()">
        <input name="card_id" placeholder="Tap / Enter Card ID" autofocus>

        <button type="submit">DEDUCT ₹15</button>
    </form>

    <script>
    function confirmDeduction() {
        return confirm("Do you want to deduct ₹15?");
    }
    </script>

    <div class="message">{{message}}</div>

    <div class="info">
        <p><strong>Name:</strong> {{name}}</p>
        <p><strong>Balance:</strong> ₹{{balance}}</p>
    </div>
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

            c.execute("""
                INSERT INTO customers (card_id, name, mobile)
                VALUES (?, ?, ?)
            """, (card_id, name, mobile))

            conn.commit()
            conn.close()

            message = "✅ Customer Added Successfully"

        except:
            message = "❌ Card Already Exists"

    return render_template_string(STYLE + """
    <div class="container">

    <div class="logo">💧</div>
    <h2>Add Customer</h2>
    <div class="subtitle">Register New Water Customer</div>

    <form method="post">
        <input name="card_id" placeholder="Card ID" autofocus>

        <input name="name" placeholder="Customer Name">

        <input name="mobile" placeholder="Mobile Number">

        <button type="submit">ADD CUSTOMER</button>
    </form>

    <div class="message">{{message}}</div>

    <a href="/">
        <button class="back-btn">Back To Home</button>
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

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("SELECT balance FROM customers WHERE card_id=?", (card_id,))
        customer = c.fetchone()

        if customer:
            c.execute("""
                UPDATE customers
                SET balance = balance + ?
                WHERE card_id=?
            """, (amount, card_id))

            c.execute("""
                INSERT INTO transactions
                (card_id, amount, type, timestamp)
                VALUES (?, ?, 'recharge', ?)
            """, (card_id, amount, datetime.now()))

            conn.commit()

            c.execute("SELECT balance FROM customers WHERE card_id=?", (card_id,))
            new_balance = c.fetchone()[0]

            message = f"✅ Recharge Successful | New Balance ₹{new_balance}"

        else:
            message = "❌ Customer Not Found"

        conn.close()

    return render_template_string(STYLE + """
    <div class="container">

    <div class="logo">💳</div>
    <h2>Recharge Balance</h2>
    <div class="subtitle">Add Wallet Balance Instantly</div>

    <form method="post" id="rechargeForm">
        <input name="card_id" placeholder="Card ID" required>

        <input name="amount" placeholder="Recharge Amount" required>

        <button type="button" id="upiOpenBtn" onclick="startRazorpayPayment()">
            🚀 Pay Securely
        </button>

        <br><br>

        <div id="timerBox" style="display:none; margin-top:20px; text-align:center;">
            <div style="
                background:rgba(239,68,68,0.15);
                border:1px solid rgba(239,68,68,0.3);
                padding:18px;
                border-radius:18px;
                color:#fca5a5;
                font-weight:600;
            ">
                ⏳ Payment Link Expires In:
                <div id="countdown" style="font-size:30px; margin-top:10px;">
                    05:00
                </div>
            </div>
        </div>

        <br>

        <button type="button" id="confirmBtn" onclick="confirmPayment()" style="display:none;">
            ✅ Payment Completed
        </button>
    </form>

    <div class="message">
        {{message}}<br><br>
        <small style="color:#94a3b8;">
            Scan QR → Complete Payment → Wallet Updates Automatically
        </small>
    </div>

    <div class="qr-box">
        <div class="qr-title">Scan & Pay via Google Pay / UPI</div>

        <img id="upiQR"
        src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=atharvkurundkar@okicici&pn=AquaFlow%20Luxe&cu=INR"
        alt="UPI QR">

        <br><br>

    </div>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {

        const amountInput = document.querySelector('input[name="amount"]');
        const qrImage = document.getElementById('upiQR');
        const timerBox = document.getElementById('timerBox');

        function updateQR() {
            const amount = amountInput.value || 0;

            const upiLink = `upi://pay?pa=atharvkurundkar@okicici&pn=AquaFlow Luxe&am=${amount}&cu=INR`;

            qrImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(upiLink)}`;
        }

        amountInput.addEventListener('input', updateQR);

        updateQR();

        window.startRazorpayPayment = async function() {

            const amount = amountInput.value || 0;
            const cardId = document.querySelector('input[name="card_id"]').value;

            if(amount <= 0){
                alert('Enter recharge amount');
                return;
            }

            if(cardId === ''){
                alert('Enter card ID');
                return;
            }

            const response = await fetch('/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: amount
                })
            });

            const data = await response.json();

           const options = {
    key: data.key,
    amount: data.amount,
    currency: 'INR',
    name: 'AquaFlow Luxe',
    description: 'Wallet Recharge',
    order_id: data.order_id,

    method: {
        upi: true,
        card: false,
        netbanking: false,
        wallet: false,
        emi: false,
        paylater: false
    },

    config: {
        display: {
            blocks: {
                upi: {
                    name: 'Pay using UPI',
                    instruments: [
                        {
                            method: 'upi'
                        }
                    ]
                }
            },
            sequence: ['block.upi'],
            preferences: {
                show_default_blocks: false
            }
        }
    },

    theme: {
        color: '#2563eb'
    },

    handler: function (response) {

        document.querySelector('.message').innerHTML = `
            <div style="
                background: rgba(34,197,94,0.15);
                border: 1px solid rgba(34,197,94,0.35);
                padding: 18px;
                border-radius: 18px;
                color: #86efac;
                font-weight: 600;
            ">
                ✅ Payment Successful<br><br>
                Wallet Recharged Successfully
            </div>
        `;

        document.getElementById('rechargeForm').submit();
    },

    modal: {
        ondismiss: function() {
            alert('Payment Cancelled');
        }
    }
};        

            const rzp = new Razorpay(options);
            rzp.open();
        }

        window.confirmPayment = function() {
            document.querySelector('.message').innerHTML = `
                <div style="
                    background: rgba(34,197,94,0.15);
                    border: 1px solid rgba(34,197,94,0.35);
                    padding: 18px;
                    border-radius: 18px;
                    color: #86efac;
                    font-weight: 600;
                ">
                    ✅ Payment Received Successfully<br><br>
                    Wallet Recharged Successfully
                </div>
            `;

            document.getElementById('rechargeForm').submit();
        }
    });
    </script>

    <a href="/">
        <button class="back-btn">Back To Home</button>
    </a>

    </div>
    """, message=message)

# ---------- CREATE RAZORPAY ORDER ----------
@app.route('/create-order', methods=['POST'])
def create_order():

    data = request.get_json()

    amount = int(float(data['amount']) * 100)

    order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1
    })

    return jsonify({
        'order_id': order['id'],
        'amount': amount,
        'key': RAZORPAY_KEY_ID
    })
# ---------- ALL CUSTOMERS ----------
@app.route("/customers")
def customers():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT card_id, name, mobile, balance
        FROM customers
        ORDER BY id DESC
    """)

    all_customers = c.fetchall()

    conn.close()

    return render_template_string(STYLE + """
    <div class="container" style="max-width:1100px;">

    <div class="logo">👥</div>
    <h1>All Customers</h1>
    <div class="subtitle">
        Live Customer Database & Wallet Details
    </div>

    <div style="overflow-x:auto;">

    <table style="
        width:100%;
        border-collapse:collapse;
        margin-top:20px;
        background:rgba(255,255,255,0.04);
        border-radius:20px;
        overflow:hidden;
    ">

        <tr style="background:rgba(255,255,255,0.08);">
            <th style="padding:18px; text-align:left;">Card ID</th>
            <th style="padding:18px; text-align:left;">Customer Name</th>
            <th style="padding:18px; text-align:left;">Mobile</th>
            <th style="padding:18px; text-align:left;">Balance</th>
        </tr>

        {% for customer in customers %}

        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
            <td style="padding:18px;">{{customer[0]}}</td>
            <td style="padding:18px;">{{customer[1]}}</td>
            <td style="padding:18px;">{{customer[2]}}</td>
            <td style="padding:18px; color:#86efac; font-weight:600;">
                ₹{{customer[3]}}
            </td>
        </tr>

        {% endfor %}

    </table>

    </div>

    <br>

    <a href="/">
        <button class="back-btn">⬅ Back To Home</button>
    </a>

    </div>
    """, customers=all_customers)
# ---------- REPORT ----------
@app.route("/report")
def report():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    today = datetime.now().date()

    # Total jars
    c.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE type='deduct'
        AND DATE(timestamp)=?
    """, (today,))
    jars = c.fetchone()[0]

    # Total revenue
    c.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE type='deduct'
        AND DATE(timestamp)=?
    """, (today,))
    revenue = c.fetchone()[0]

    if revenue is None:
        revenue = 0

    # Total recharges
    c.execute("""
        SELECT SUM(amount)
        FROM transactions
        WHERE type='recharge'
        AND DATE(timestamp)=?
    """, (today,))
    recharge_total = c.fetchone()[0]

    if recharge_total is None:
        recharge_total = 0

    conn.close()

    return render_template_string(STYLE + """
    <div class="container">

    <div class="logo">📊</div>
    <h1>Business Analytics</h1>
    <div class="subtitle">Daily Revenue & Jar Reports</div>

    <div class="info">
        <h3>Total Jars Sold: {{jars}}</h3>
        <h3>Total Revenue: ₹{{revenue}}</h3>
        <h3>Total Recharge: ₹{{recharge}}</h3>
    </div>

    <a href="/">
        <button class="back-btn">Back To Home</button>
    </a>

    </div>
    """, jars=jars, revenue=revenue, recharge=recharge_total)
# ---------- RUN ----------
if __name__ == "__main__":
    app.run()