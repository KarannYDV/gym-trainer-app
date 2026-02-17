from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for
from datetime import datetime



app = Flask(__name__)
app.secret_key = "supersecretkey"


# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gym.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Goal table
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


# Workout Plan table
class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)

class DietAdvice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=False)
    advice_text = db.Column(db.String(300), nullable=False)

class UserPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))




@app.route("/generate", methods=["POST"])
def generate():
    goal_name = request.form["goal"]
    experience = request.form["experience"]

    # Find goal in database
    goal = Goal.query.filter_by(name=goal_name).first()

    # Fetch workout plan
    plans = WorkoutPlan.query.filter_by(
        goal_id=goal.id,
        experience_level=experience
    ).order_by(WorkoutPlan.day_number).all()
    diet = DietAdvice.query.filter_by(goal_id=goal.id).first()

    new_plan = UserPlan(
    user_id=session["user_id"],
    goal=goal_name,
    experience=experience)

    db.session.add(new_plan)
    db.session.commit()



    return render_template("plan.html", goal=goal_name, experience=experience, plans=plans ,diet=diet)

@app.route("/my-plans")
def my_plans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    plans = UserPlan.query.filter_by(user_id=session["user_id"]).all()
    return render_template("my_plans.html", plans=plans)



def seed_data():
    if Goal.query.count() == 0:
        # Create goals
        fat_loss = Goal(name="Fat Loss")
        muscle_gain = Goal(name="Muscle Gain")
        strength = Goal(name="Strength")

        db.session.add_all([fat_loss, muscle_gain, strength])
        db.session.commit()

        # Workout Plans (Muscle Gain - Beginner)
        workout_plans = [
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=1, description="Chest + Triceps"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=2, description="Back + Biceps"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=3, description="Rest"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=4, description="Leg Day"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=5, description="Shoulders"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=6, description="Core + Abs"),
            WorkoutPlan(goal_id=muscle_gain.id, experience_level="Beginner", day_number=7, description="Rest"),
        ]

        db.session.add_all(workout_plans)

        # Diet Advice
        diet_advice = [
            DietAdvice(goal_id=fat_loss.id, advice_text="Maintain a calorie deficit. Eat high protein, reduce processed sugar, increase fiber intake."),
            DietAdvice(goal_id=muscle_gain.id, advice_text="Maintain a calorie surplus. 1.6-2g protein per kg bodyweight. Include complex carbs."),
            DietAdvice(goal_id=strength.id, advice_text="Balanced diet with sufficient carbs for energy and adequate protein for recovery."),
        ]

        db.session.add_all(diet_advice)
        db.session.commit()



if __name__ == "__main__":
   with app.app_context():
    db.create_all()
    seed_data()
 # Create tables
    app.run(host="0.0.0.0", port=5000)

