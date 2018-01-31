"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register')
def show_reg_form():
    """Display user registration form."""

    return render_template('reg_form.html')


@app.route('/register', methods=['POST'])
def submit_reg_form():
    """Check for unique user email and create new user."""

    email = request.form.get('email')
    password = request.form.get('password')

    existing_emails = db.session.query(User.email)

    if email in existing_emails:
        pass
    else:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect('/')


@app.route('/login', methods=['GET'])
def show_login_form():
    """Display user log-in page."""

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def submit_login_form():
    """Check for unique email and password. If correct, log in."""

    email = request.form.get('email')
    password = request.form.get('password')

    result = User.query.filter((User.email == email) &
                               (User.password == password))

    if result.count() == 0:
        flash('Username and/or password incorrect.')
        return redirect('/login')
    else:
        user = result.first()
        session['user_id'] = user.user_id
        flash('Logged in')
        return redirect('/user=' + str(user.user_id))


@app.route('/logout')
def submit_logout():
    """Logs out user by emptying session and redirects to homepage"""

    del session['user_id']
    return redirect('/')


@app.route('/user=<user_id>')
def show_user_page(user_id):
    """Show information relating to specific user."""

    user_info = Rating.query.filter(Rating.user_id == user_id).all()
    # import pdb; pdb.set_trace()
    zipcode = user_info[0].user.zipcode
    age = user_info[0].user.age

    # movie_info = db.session.query(Rating.score, Rating.movie.title)

    movie_info = db.session.query(Rating.score, Movie.title).join(Movie)
    score_title = movie_info.filter(Rating.user_id == user_id).all()



    return render_template('user_info.html', score_title=score_title,
                           zipcode=zipcode, age=age, user_id=user_id)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
