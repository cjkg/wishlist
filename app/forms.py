from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=4, max=64, message="Username must be between 4 and 64 characters"
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=4, max=256, message="Password must be between 8 and 256 characters"
            ),
        ],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WishForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(min=1, max=256, message="Wish must be between 1 and 256 characters"),
        ],
        render_kw={"placeholder": "Capital Vol. 1, by Karl Marx"},
    )
    note = StringField(
        "Note",
        validators=[Length(max=1024)],
        render_kw={"placeholder": "A book I'd really like!"},
    )
    link = StringField(
        "Link",
        validators=[Length(max=4096, message="Link must be less than 4096")],
        render_kw={"placeholder": "https://www.example.com"},
    )
    submit = SubmitField("Add to Wishlist")
