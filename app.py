from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Note
from forms import RegisterForm, LoginForm, NoteForm, DeleteForm

CURRENT_USER = "username"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
toolbar = DebugToolbarExtension(app)


def authenicate_user(username):
    """ Display a template the shows information
        about that user (everything except for their password)
    """

    # is there any user logged into the session
    # is the logged in username = username in the URL

    if CURRENT_USER not in session:
        flash("You are not authorized to view this page.")
        return redirect("/login")

    elif username != session[CURRENT_USER]:
        flash("You are not authorized to access another user's page.")
        logged_in_user = session[CURRENT_USER]
        return redirect(f"/users/{logged_in_user}")
    else:
        return True


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
        session[CURRENT_USER] = user.username

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
############## if logged in, redirect to user page ######################

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session[CURRENT_USER] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad username/password"]

    return render_template("login_user.html", form=form)


@app.route("/users/<username>")
def show_user(username):
    """ Display a template the shows information
        about that user (everything except for their password)
    """

    # is there any user logged into the session
    # is the logged in username = username in the URL

    # if CURRENT_USER not in session:
    #     flash("You are not authorized to view this page.")
    #     return redirect("/login")

    # elif username != session[CURRENT_USER]:
    #     flash("You are not authorized to access another user's page.")
    #     logged_in_user = session[CURRENT_USER]
    #     return redirect(f"/users/{logged_in_user}")

    if authenicate_user(username):
        flash('entered if')
        user = User.query.get_or_404(username)
        return render_template("user.html", user=user)


@app.route("/logout")
def logout_user():
    """ Clear any information from the session
        and redirect to homepage
    """

    session.pop(CURRENT_USER)
    return redirect("/")


@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_notes_form(username):
    """ GET: Display a form to add notes.
        POST: Add a new note and redirect to /users/<username>
    """

    if CURRENT_USER not in session:
        flash("You are not authorized to view this page.")
        return redirect("/login")

    elif username != session[CURRENT_USER]:
        flash("You are not authorized to access another user's page.")
        logged_in_user = session[CURRENT_USER]
        return redirect(f"/users/{logged_in_user}")

    form = NoteForm()
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content)
        user.notes.append(note)

        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        return render_template("new_note.html", user=user, form=form)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def update_notes_form(note_id):
    """ GET: Display a form to update notes.
        POST: update note and redirect to /users/<username>
    """
    note = Note.query.get_or_404(note_id)
    username = note.user.username
    form = NoteForm(obj=note)

    if CURRENT_USER not in session:
        flash("You are not authorized to view this page.")
        return redirect("/login")

    elif username != session[CURRENT_USER]:
        flash("You are not authorized to access another user's page.")
        logged_in_user = session[CURRENT_USER]
        return redirect(f"/users/{logged_in_user}")

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        return render_template("update_note.html", form=form, note=note)


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def delete_note(note_id):
    """ Delete note and redirect to /users/<username>
    """
    note = Note.query.get_or_404(note_id)
    username = note.user.username

    if CURRENT_USER not in session:
        flash("You are not authorized to view this page.")
        return redirect("/login")

    elif username != session[CURRENT_USER]:
        flash("You are not authorized to access another user's page.")
        logged_in_user = session[CURRENT_USER]
        return redirect(f"/users/{logged_in_user}")
    
    form = DeleteForm()
    if form.validate_on_submit():
        ###################### not working #####################
        db.session.delete(note)
        db.session.commit()

    return redirect(f'/users/{username}')
