from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    role = db.Column(db.String(255), nullable=False, default="Donor")

    # Relationship with Admins table
    admin_relation = db.relationship('Admins', back_populates='user', uselist=False, overlaps="admin_relation")

    def serialize(self):
        serialized_data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'image_url': self.image_url,
            'role': self.role
        }
        if self.phone_number is not None:  # Check if phone_number is not None
            serialized_data['phone_number'] = self.phone_number
        return serialized_data

class Admins(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # The relationship with the Users table
    user = db.relationship('Users', back_populates='admin_relation', uselist=False, overlaps="admin_relation")
    
    
    def serialize(self):
        user_data = self.user.serialize() if self.user is not None else None
        return {
            'admin_id': self.admin_id,
            'user': user_data
        }
        

class Charities(db.Model):
    charity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String)
    goal = db.Column(db.Float, nullable=False, default=0.0)
    raised = db.Column(db.Float, nullable=False, default=0.0)
    mission = db.Column(db.String)   
    status = db.Column(db.String, nullable=False, default="Pending")  # Add status field with default value "Pending"
    category = db.Column(db.String)  # Add category field

    # One-to-One relationship with ContactDetails
    contact_details = relationship("ContactDetails", back_populates="charity", uselist=False, cascade="all, delete-orphan")

    def serialize(self):
        return {
            'charity_id': self.charity_id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'goal': self.goal,
            'raised': self.raised,
            'mission': self.mission,
            'status':self.status,
            'category':self.category            
        }

class ContactDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id', ondelete='CASCADE'), nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    charity_email = db.Column(db.String, nullable=False)
    map_details = db.Column(db.String)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    charity = relationship("Charities", back_populates="contact_details") # One-to-One relationship with Charities
    messages = relationship("Message", back_populates="contact_details") # One-to-One relationship with Messages

    def serialize(self):
        return {
            'id': self.id,
            'charity_id': self.charity_id,
            'phone_number': self.phone_number,
            'charity_email': self.charity_email,
            'map_details': self.map_details,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'messages': [msg.serialize() for msg in self.messages]
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # One-to-Many relationship with ContactDetails
    contact_details_id = db.Column(db.Integer, db.ForeignKey('contact_details.id', ondelete='CASCADE'), nullable=False)
    contact_details = relationship("ContactDetails", back_populates="messages")

    @property
    def charity_id(self):
        return self.contact_details.charity_id if self.contact_details else None

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S')
        }


class Donations(db.Model):
    donation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(255))
    frequency = db.Column(db.String(255))

    def serialize(self):
        return {
            'donation_id': self.donation_id,
            'user_id': self.user_id,
            'charity_id': self.charity_id,
            'amount': str(self.amount),
            'is_anonymous': self.is_anonymous,
            'payment_method': self.payment_method,
            'frequency': self.frequency
        }

class Stories(db.Model):
    story_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    date_posted = db.Column(db.Date)

    def serialize(self):
        return {
            'story_id': self.story_id,
            'charity_id': self.charity_id,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'date_posted': self.date_posted.strftime('%Y-%m-%d') if self.date_posted else None
        }

class Beneficiaries(db.Model):
    beneficiary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    inventory_sent = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))

    def serialize(self):
        return {
            'beneficiary_id': self.beneficiary_id,
            'name': self.name,
            'description': self.description,
            'charity_id': self.charity_id,
            'inventory_sent': self.inventory_sent,
            'image_url': self.image_url
        }

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    image_url = db.Column(db.String(255))

    def serialize(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'charity_id': self.charity_id,
            'image_url': self.image_url
        }

class Reviews(db.Model):
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date_posted = db.Column(db.Date)

    def serialize(self):
        return {
            'review_id': self.review_id,
            'charity_id': self.charity_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'date_posted': self.date_posted.strftime('%Y-%m-%d') if self.date_posted else None
        }

class WordsOfSupport(db.Model):
    support_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.Date)

    def serialize(self):
        return {
            'support_id': self.support_id,
            'charity_id': self.charity_id,
            'user_id': self.user_id,
            'message': self.message,
            'date_posted': self.date_posted.strftime('%Y-%m-%d') if self.date_posted else None
        }

class PaymentTransactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    payment_method = db.Column(db.String(255))
    transaction_status = db.Column(db.String(255))
    date_paid = db.Column(db.Date)

    def serialize(self):
        return {
            'transaction_id': self.transaction_id,
            'donor_id': self.donor_id,
            'charity_id': self.charity_id,
            'amount': str(self.amount),
            'payment_method': self.payment_method,
            'transaction_status': self.transaction_status,
            'date_paid': self.date_paid.strftime('%Y-%m-%d') if self.date_paid else None
        }

class DonorPaymentMethods(db.Model):
    method_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    payment_method_name = db.Column(db.String(255), nullable=False)
    payment_method_details = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'method_id': self.method_id,
            'donor_id': self.donor_id,
            'payment_method_name': self.payment_method_name,
            'payment_method_details': self.payment_method_details
        }

class ReminderSettings(db.Model):
    setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    reminder_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'setting_id': self.setting_id,
            'donor_id': self.donor_id,
            'charity_id': self.charity_id,
            'reminder_time': self.reminder_time.strftime('%H:%M:%S') if self.reminder_time else None,
            'is_active': self.is_active
        }

class RegularDonations(db.Model):
    donation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.charity_id'), nullable=False)
    frequency = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def serialize(self):
        return {
            'donation_id': self.donation_id,
            'donor_id': self.donor_id,
            'charity_id': self.charity_id,
            'frequency': self.frequency,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        }


