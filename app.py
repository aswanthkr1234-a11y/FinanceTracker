import sqlite3
from flask import Flask, render_template, request, redirect, session, send_file, flash
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


# Ensure DB tables exist before any request handler runs
import database  # noqa: F401

app = Flask(__name__)
app.secret_key="finance_tracker_secret"

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    username = session['user']

    search = request.args.get("search")
    month = request.args.get("month")

    # IMPORTANT: never rely on SELECT * column ordering because DB migrations may reorder columns.
    # templates/index.html expects:
    # income tuple => [id, source, category, amount, date]
    if search:
        cursor.execute(
            """
            SELECT id, source, category, amount, date
            FROM income
            WHERE username=? AND source LIKE ?
            ORDER BY id DESC
            """,
            (username, '%' + search + '%',),
        )
    elif month:
        cursor.execute(
            """
            SELECT id, source, category, amount, date
            FROM income
            WHERE username=? AND substr(date,6,2)=?
            ORDER BY id DESC
            """,
            (username,month),
        )
    else:
        cursor.execute(
            """
            SELECT id, source, category, amount, date
            FROM income
            WHERE username=?
            ORDER BY id DESC
            """,(username,)
        )

    incomes = cursor.fetchall()

    # templates/index.html expects:
    # expense tuple => [id, expense, amount, date]
    cursor.execute(
        """
        SELECT id, expense, amount, date
        FROM expense
        WHERE username=?
        ORDER BY id DESC
        """, (username,)
    )
    expenses = cursor.fetchall()

    cursor.execute(
        "SELECT SUM(amount) FROM income WHERE username=?",
        (username,)
    )
    total_income = cursor.fetchone()[0]
    if total_income is None:
        total_income = 0

    cursor.execute(
        "SELECT SUM(amount) FROM expense WHERE username=?",
        (username,)
    )
    total_expense = cursor.fetchone()[0]
    if total_expense is None:
        total_expense = 0

    cursor.execute("""
                   SELECT source, SUM(amount)
                   FROM income
                   WHERE username=?
                   GROUP BY source
                   ORDER BY SUM(amount) DESC
                   LIMIT 1
                   """, (username,))


    top_income = cursor.fetchone()

    cursor.execute("""
                   SELECT expense, SUM(amount)
                   FROM expense
                   WHERE username=?
                   GROUP BY expense
                   ORDER BY SUM(amount) DESC
                   LIMIT 1
                   """, (username,))
    top_expense = cursor.fetchone()

    cursor.execute("""
                   SELECT source, amount
                   FROM income
                   WHERE username=?
                   ORDER BY id DESC
                   LIMIT 5
                   """, (username,))
    recent_income = cursor.fetchall()

    cursor.execute("SELECT amount FROM budget LIMIT 1")
    budget = cursor.fetchone()

    if budget:
        budget = budget[0]

    else:
        budget=0
    remaining = budget - total_expense

    savings = total_income - total_expense
    conn.close()

    return render_template(
        'index.html',
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        budget=budget,
        remaining=remaining,
        top_income=top_income,
        top_expense=top_expense,
        recent_income=recent_income

        )

@app.route('/add-income', methods=['GET', 'POST'])
def add_income():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        source = request.form['source']
        category = request.form.get('category', 'Other')
        amount = request.form['amount']
        date = request.form.get('date', '')
        username = session['user']

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO income (username, source, category, amount, date) VALUES (?, ?, ?, ?, ?)",
            (username, source, category, amount, date)
        )

        conn.commit()
        conn.close()
        flash("Income added successfully!","success")
        return redirect('/')

    return render_template('add_income.html')

@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        expense = request.form['expense']
        amount = request.form['amount']
        username = session['user']


        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expense (username, expense, amount) VALUES (?, ?, ?)", (username, expense, amount))

        conn.commit()
        conn.close()
        flash("Expense added successfully!", "success")
        return redirect('/')
    return render_template('add_expense.html')

@app.route('/delete-income/<int:id>')
def delete_income(id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Income deleted successfully!", "success")
    return redirect('/')

@app.route('/edit-income/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    conn=sqlite3.connect("finance.db")
    cursor=conn.cursor()

    if request.method=='POST':
        source=request.form['source']
        amount=request.form['amount']
        cursor.execute("UPDATE income SET source=?, amount=? WHERE id=?", (source, amount, id))
        conn.commit()
        conn.close()
        return redirect('/')
    cursor.execute(
        "SELECT id, source, category, amount, date FROM income WHERE id=?",
        (id,)
    )
    income = cursor.fetchone()

    conn.close()
    return render_template("edit_income.html", income=income)

@app.route('/delete-expense/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expense WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Expense deleted successfully", "Success")
    return redirect('/')

@app.route('/edit-expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    if request.method == "POST":
        expense = request.form["expense"]
        amount = request.form["amount"]

        cursor.execute(
            "UPDATE expense SET expense=?, amount=? WHERE id=?",
            (expense, amount, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute(
        "SELECT id, expense, amount, date FROM expense WHERE id=?",
        (id,)
    )
    expense = cursor.fetchone()

    conn.close()

    return render_template("edit_expense.html", expense=expense)

@app.route('/report')
def report():
    if 'user' not in session:
        return redirect('/login')
    return render_template('report.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')
        return "Invalid Username or Password"
    return render_template('login.html')

@app.route('/logout')
def logout():

    session.pop('user', None) 
    return redirect('/login')

@app.route('/set-budget', methods=['GET', 'POST' ])
def set_budget():
    if request.method == 'POST':
        budget = request.form['budget']

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        # Ensure table exists (prevents sqlite3.OperationalError: no such table: budget)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budget(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL
            )
            """
        )

        cursor.execute("DELETE FROM budget")

        cursor.execute(
            "INSERT INTO budget(amount) VALUES(?)",
            (budget,)
        )


        conn.commit()
        conn.close()

        return redirect('/')
    return render_template("set_budget.html")
@app.route('/export')
def export():
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Finance Report"

    ws.append(["Type", "Name", "Amount"])

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT source, amount FROM income")
    incomes = cursor.fetchall()

    for income in incomes:
        ws.append(["Income", income[0], income[1]])

    cursor.execute("SELECT expense, amount FROM expense ")
    expenses = cursor.fetchall()

    for expense in expenses:
        ws.append(["Expense", expense[0], expense[1]])

    conn.close()
    filename = "Finance_Report.xlsx"
    wb.save(filename)
    return send_file(filename, as_attachment=True)

@app.route('/export-pdf')
def export_pdf():

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT source, amount FROM income")
    incomes = cursor.fetchall()

    cursor.execute("SELECT expense, amount FROM expense")
    expenses = cursor.fetchall()

    conn.close()

    filename = "Finance_Report.pdf"

    doc=SimpleDocTemplate(filename)
    elements = []
    data=[["Type", "Name", "Amount"]]

    for income in incomes:
        data.append(["income", income[0], income[1]])
    for expense in expenses:
        data.append(["Expense", expense[0], expense[1]])
    table = Table(data)

    # Use TableStyle from reportlab and fix GRID tuple syntax
    from reportlab.platypus import TableStyle

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(filename, as_attachment=True)
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)

