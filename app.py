from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

SAMPLE_STUDENT = {
    "name": "Sree Simhan Kumar",
    "reg_no": "24BF1234",
    "program": "B.Tech CSE",
    "school": "SCOPE",
    "campus": "Vellore",
    "email": "sreesimham2007@gmail.com",
    "phone": "+91 9791165406",
    "semester": "4th Semester",
    "cgpa": "8.52",
}

SAMPLE_ATTENDANCE = [
    {"code": "CSE3002", "name": "Internet & Web Programming", "total": 40, "attended": 36, "pct": 90},
    {"code": "CSE2005", "name": "Operating Systems", "total": 38, "attended": 32, "pct": 84},
    {"code": "MAT3005", "name": "Probability & Statistics", "total": 42, "attended": 35, "pct": 83},
    {"code": "CSE3003", "name": "Database Management Systems", "total": 36, "attended": 33, "pct": 92},
    {"code": "CSE2006", "name": "Computer Networks", "total": 40, "attended": 34, "pct": 85},
]

SAMPLE_TIMETABLE = [
    {"day": "Monday",    "slots": ["IWP (A1)", "—", "OS (B1)", "—", "DBMS Lab (L1+L2)", "—"]},
    {"day": "Tuesday",   "slots": ["P&S (C1)", "—", "CN (D1)", "—", "IWP Lab (L3+L4)", "—"]},
    {"day": "Wednesday", "slots": ["OS (A1)", "—", "IWP (B1)", "—", "P&S (C1)", "—"]},
    {"day": "Thursday",  "slots": ["DBMS (D1)", "—", "CN (A1)", "—", "OS Lab (L5+L6)", "—"]},
    {"day": "Friday",    "slots": ["CN (B1)", "—", "DBMS (C1)", "—", "P&S Tutorial", "—"]},
]

SAMPLE_GRADES = [
    {"code": "CSE2004", "name": "Data Structures & Algorithms", "credits": 4, "grade": "A"},
    {"code": "CSE2003", "name": "Digital Logic & Design", "credits": 3, "grade": "A+"},
    {"code": "MAT2001", "name": "Discrete Mathematics", "credits": 4, "grade": "B+"},
    {"code": "CSE2001", "name": "Computer Architecture", "credits": 3, "grade": "A"},
    {"code": "ENG1001", "name": "Technical English", "credits": 2, "grade": "S"},
]

SLOT_TIMES = ["8:00–8:50", "9:00–9:50", "10:00–10:50", "11:00–11:50", "12:00–12:50", "2:00–2:50"]


@app.route("/")
def index():
    return render_template("index.html", logged_in=session.get("logged_in", False))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        session["student"] = SAMPLE_STUDENT
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        student=session["student"],
        attendance=SAMPLE_ATTENDANCE,
        timetable=SAMPLE_TIMETABLE,
        grades=SAMPLE_GRADES,
        slot_times=SLOT_TIMES,
        section="overview",
    )


@app.route("/dashboard/<section>")
def dashboard_section(section):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        student=session["student"],
        attendance=SAMPLE_ATTENDANCE,
        timetable=SAMPLE_TIMETABLE,
        grades=SAMPLE_GRADES,
        slot_times=SLOT_TIMES,
        section=section,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
