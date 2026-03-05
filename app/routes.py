from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
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
    if current_user.is_authenticated and current_user.username == username:
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

            Wish.query.filter(Wish.user_id == current_user.id).update(
                {Wish.rank: Wish.rank + 1}, synchronize_session=False
            )

            db.session.add(wish)
            db.session.commit()

        return render_template(
            "wishlist_user.html", user=user, wishes=wishes, form=form
        )
    else:
        stmt = user.wishes.select().where(Wish.purchased.is_(False)).order_by(Wish.rank)

        wishes = db.session.scalars(stmt).all()
        return render_template("wishlist_public.html", user=user, wishes=wishes)


@app.route("/wishlist_items", methods=["POST"])
@login_required
def reorder_items():
    ordered_ids = request.form.getlist("item")

    wishes = Wish.query.filter(
        Wish.id.in_(ordered_ids), Wish.user_id == current_user.id
    ).all()

    wishes_by_id = {wish.id: wish for wish in wishes}

    for index, wish_id in enumerate(ordered_ids):
        wish = wishes_by_id.get(int(wish_id))
        if wish:
            wish.rank = index

    db.session.commit()

    return "", 204


@app.route("/purchase/<int:user_id>/<int:wish_id>", methods=["POST"])
def purchase_wish(user_id, wish_id):
    wish = Wish.query.filter_by(id=wish_id, user_id=user_id).first_or_404()

    wish.purchased = True
    db.session.commit()

    return render_template("wishes/_public_wish_row.html", wish=wish, user=wish.owner)


@app.route("/delete_wish/<int:wish_id>", methods=["DELETE"])
@login_required
def delete_wish(wish_id):
    wish = Wish.query.filter_by(id=wish_id, user_id=current_user.id).first_or_404()

    deleted_rank = wish.rank

    db.session.delete(wish)

    Wish.query.filter(Wish.user_id == current_user.id, Wish.rank > deleted_rank).update(
        {Wish.rank: Wish.rank - 1}, synchronize_session=False
    )

    db.session.commit()

    return "", 200
