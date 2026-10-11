import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = "telemetry_drop.db"
FLAG = os.getenv("CHALLENGE_FLAG", "Eclipse{5ql_1nj3ct10n_auth_byp455_succ355}")

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # ADVANCED WAF RULE: Block spaces to force /**/ bypass
        if " " in username or " " in password:
            return render_template("login.html", error="Access Denied: Spaces are forbidden by firewall rules.")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Vulnerability: Direct string concatenation without parameterization
        query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}';"

        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except sqlite3.OperationalError as e:
            conn.close()
            return render_template("login.html", error=f"Database Exception: {str(e)}")

        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[2]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid observatory credentials."

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("role") != "administrator":
        return redirect(url_for("login"))
    return render_template("admin.html", username=session.get("username"))

@app.route("/reports")
def reports():
    if "user_id" not in session or session.get("role") != "administrator":
        return redirect(url_for("login"))
    return render_template("reports.html", username=session.get("username"))

@app.route("/reports/view")
def view_report():
    if "user_id" not in session or session.get("role") != "administrator":
        return redirect(url_for("login"))

    report_id = request.args.get("id")

    if report_id == "1":
        title = "Report #01 - Array Calibration"
        data = "Array B aligned to 1420.405 MHz. Thermal variances within acceptable margins."
        is_flag = False
    elif report_id == "2":
        title = "Report #02 - Network Traffic Audit"
        data = "Routine telemetry bursts completed at 04:00 UTC. No anomalies detected in outbound streams."
        is_flag = False
    elif report_id == "99":
        title = "Report #99 - CLASSIFIED QUARANTINE LOG"
        data = f"WARNING: UNAUTHORIZED PAYLOAD INTERCEPTED BY SENTINEL IDS.\nORIGIN: ECLIPSE SYNDICATE.\n\nDECRYPTED EXFILTRATION BUFFER:\n{FLAG}"
        is_flag = True
    else:
        title = "File Not Found"
        data = "Error: The requested report ID does not exist in the archive."
        is_flag = False

    return render_template("view_report.html", title=title, data=data, is_flag=is_flag)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)