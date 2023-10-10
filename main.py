from flask import Flask, render_template, flash, redirect, request, session, jsonify, url_for
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "This_is_Secret_Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'  # Corrected the database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/home/")
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user:
            return render_template("view.html", user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = User.query.filter_by(name=user).first()  # Corrected the query
        if found_user:
            session["email"] = found_user.email
        else:
            usr = User(user, "")
            db.session.add(usr)
            db.session.commit()

        flash("Login Successful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = User.query.filter_by(name=user).first()  # Corrected the query
            found_user.email = email
            db.session.commit()
            flash("Your email has been saved")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not Logged In")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    user = session.get("user", None)
    flash(f"You have been logged out, {user}", "information")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)
