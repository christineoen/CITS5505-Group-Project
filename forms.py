from datetime import time
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, TimeField, IntegerField, TextAreaField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models.user import User
from utils import DAYS


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 100)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Sign Up")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered.")


class ProfileDetailsForm(FlaskForm):
    # Shared (saved to User)
    suburb   = StringField("Suburb", validators=[Optional(), Length(max=100)])
    postcode = StringField("Postcode", validators=[Optional(), Length(max=10)])

    # Sitter fields
    bio              = TextAreaField("Bio", validators=[Optional(), Length(max=1000)])
    hourly_rate      = FloatField("Hourly rate ($/hr)", validators=[Optional(), NumberRange(min=0)])
    experience_years = IntegerField("Years of experience", validators=[Optional(), NumberRange(min=0)])
    availability     = SelectMultipleField("Availability", choices=[(d, d) for d in DAYS], validators=[Optional()])

    # Parent fields
    about         = TextAreaField("About your family", validators=[Optional(), Length(max=1000)])
    children_json = StringField("Children", validators=[Optional()])

    submit = SubmitField("Continue")

    def validate_hourly_rate(self, field):
        if field.data is None and self._role == "sitter":
            raise ValidationError("Please enter your hourly rate.")

    def validate_experience_years(self, field):
        if field.data is None and self._role == "sitter":
            raise ValidationError("Please enter your years of experience.")

    @property
    def _role(self):
        from flask import session
        return session.get("pending_role", "")




class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")


class BookingForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()], default=time(18, 0))
    duration_hours = IntegerField(
        "Duration (hours)",
        validators=[DataRequired(), NumberRange(min=1, max=12, message="Duration must be between 1 and 12 hours.")],
        default=4,
    )
    notes = TextAreaField("Notes (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Request Booking")


class RatingForm(FlaskForm):
    score = IntegerField(
        "Rating",
        validators=[DataRequired(message="Please select a rating."), NumberRange(min=1, max=5)]
    )
    comment = TextAreaField(
        "Comment (Optional)",
        validators=[Optional(), Length(max=500, message="Comment must not exceed 500 characters.")]
    )
    submit = SubmitField("Submit Rating")
