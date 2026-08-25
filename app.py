from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "student-management-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# USER MODEL
# =========================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


# =========================
# STUDENT MODEL
# =========================

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    course = db.Column(
        db.String(100),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=False
    )


# =========================
# REGISTER
# =========================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]


        # Check existing username
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "Username already exists!",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # Check existing email
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "Email already registered!",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # Hash password
        hashed_password = generate_password_hash(
            password
        )


        user = User(
            name=name,
            email=email,
            username=username,
            password=hashed_password
        )


        db.session.add(user)
        db.session.commit()


        flash(
            "Account created successfully! Please login.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        user = User.query.filter_by(
            username=username
        ).first()


        if user and check_password_hash(
            user.password,
            password
        ):

            session["logged_in"] = True

            session["user_id"] = user.id

            session["username"] = user.username

            session["name"] = user.name


            flash(
                "Login successful!",
                "success"
            )


            return redirect(
                url_for("index")
            )


        flash(
            "Invalid username or password!",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# DASHBOARD
# =========================

@app.route("/")
def index():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    search = request.args.get(
        "search",
        ""
    )


    if search:

        students = Student.query.filter(
            (Student.name.ilike(
                f"%{search}%"
            )) |
            (Student.course.ilike(
                f"%{search}%"
            ))
        ).all()

    else:

        students = Student.query.all()


    total_students = Student.query.count()


    total_courses = db.session.query(
        db.func.count(
            db.func.distinct(
                Student.course
            )
        )
    ).scalar()


    average_age = db.session.query(
        db.func.avg(
            Student.age
        )
    ).scalar()


    if average_age:

        average_age = round(
            average_age,
            1
        )

    else:

        average_age = 0


    return render_template(
        "index.html",
        students=students,
        search=search,
        total_students=total_students,
        total_courses=total_courses,
        average_age=average_age
    )


# =========================
# ADD STUDENT
# =========================

@app.route(
    "/add",
    methods=["GET", "POST"]
)
def add_student():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        student = Student(

            name=request.form["name"],

            email=request.form["email"],

            phone=request.form["phone"],

            course=request.form["course"],

            age=request.form["age"]

        )


        db.session.add(student)

        db.session.commit()


        flash(
            "Student added successfully!",
            "success"
        )


        return redirect(
            url_for("index")
        )


    return render_template(
        "add_student.html"
    )


# =========================
# EDIT STUDENT
# =========================

@app.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit_student(id):

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    student = Student.query.get_or_404(id)


    if request.method == "POST":

        student.name = request.form["name"]

        student.email = request.form["email"]

        student.phone = request.form["phone"]

        student.course = request.form["course"]

        student.age = request.form["age"]


        db.session.commit()


        flash(
            "Student updated successfully!",
            "success"
        )


        return redirect(
            url_for("index")
        )


    return render_template(
        "edit_student.html",
        student=student
    )


# =========================
# DELETE STUDENT
# =========================

@app.route(
    "/delete/<int:id>"
)
def delete_student(id):

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    student = Student.query.get_or_404(id)


    db.session.delete(student)

    db.session.commit()


    flash(
        "Student deleted successfully!",
        "success"
    )


    return redirect(
        url_for("index")
    )


# =========================
# CREATE DATABASE
# =========================

with app.app_context():

    db.create_all()


# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )