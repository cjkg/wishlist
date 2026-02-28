from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from app import app, db
from app.forms import LoginForm, WishForm
from app.models import User, Wish
import sqlalchemy as sa
from urllib.parse import urlsplit


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/wishlist/<username>", methods=["GET", "POST"])
def wishlist(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    stmt = user.wishes.select().order_by(Wish.rank)
    wishes = db.session.scalars(stmt).all()

    form = WishForm()
    if form.validate_on_submit():
        wish = Wish(
            user_id=user.id,
            title=form.title.data.strip(),
            note=form.note.data.strip(),
            link=form.link.data.strip(),
            rank=1,
            purchased=False,
        )
        db.session.add(wish)
        db.session.commit()

    return render_template("wishlist.html", user=user, wishes=wishes, form=form)
