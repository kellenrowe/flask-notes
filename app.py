from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """ redirects user to /register route """

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_new_user():
    """ GET: Show a form that when submitted will register/create a user.
        Accepts username, password, email, first_name, and last_name.

        POST: Process the registration form by adding a new user. Then redirect
        to /secret
    """
    # create form
    form = RegisterForm()

    # if form is valid
    if form.validate_on_submit():

        user = User.register(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )

        db.session.add(user)
        db.session.commit()
        session["username"] = user.username

        # on successful login, redirect user to logged in landing page
        return redirect(f"/users/{user.username}")
    else:
        return render_template("register_user.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """ GET: Show a form that when submitted will login a user. This form
        should accept a username and a password.

        POST: Process the login form, ensuring the user is authenticated and
        going to /secret if so.
    """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad username/password"]
            return render_template("login_user.html", form=form)
    else:
        return render_template("login_user.html", form=form)


@app.route("/users/<username>")
def show_user(username):
    """ Display a template the shows information 
    about that user (everything except for their password)
    """

    # is there any user logged into the session
    # is the logged in username = username in the URL

    if "username" not in session:
        flash("You are not authorized to view this page.")      

        return redirect("/login")
    elif username != session["username"]:
        flash("You are not authorized to access another user's page. We got yo numba!")      

        logged_in_user = session["username"]

        return redirect(f"/users/{logged_in_user}")
    else:
        user = User.query.get_or_404(username)
        return render_template("user.html", user=user)


@app.route("/logout")
def logout_user():
    """ Clear any information from the session 
    and redirect to homepage 
    """

    session.pop("username")

    return redirect("/")
