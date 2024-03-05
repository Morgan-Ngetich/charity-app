from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)

class Charities(db.Model):
    charity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=False)

class Donations(db.Model):
    donation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(255))
    frequency = db.Column(db.String(255))

class Stories(db.Model):
    story_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    date_posted = db.Column(db.Date)

class Beneficiaries(db.Model):
    beneficiary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    inventory_sent = db.Column(db.Boolean, default=False)

class Admins(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)

class Reviews(db.Model):
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date_posted = db.Column(db.Date)

class WordsOfSupport(db.Model):
    support_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.Date)

class PaymentTransactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    payment_method = db.Column(db.String(255))
    transaction_status = db.Column(db.String(255))
    date_paid = db.Column(db.Date)

class DonorPaymentMethods(db.Model):
    method_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    payment_method_name = db.Column(db.String(255), nullable=False)
    payment_method_details = db.Column(db.Text, nullable=False)

class ReminderSettings(db.Model):
    setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    reminder_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=False)

class RegularDonations(db.Model):
    donation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    frequency = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

class InventoryItems(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    quantity_requested = db.Column(db.Integer, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
