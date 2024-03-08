from flask import Flask
from faker import Faker
from models import db, Users, Charities, Donations, Stories, Beneficiaries, Admins, Items, Reviews, WordsOfSupport, PaymentTransactions, DonorPaymentMethods, ReminderSettings, RegularDonations
from app import create_app
import random
import datetime

app = create_app()
fake = Faker()


def seed_users(num_users):
    with app.app_context():
        for _ in range(num_users):
            user = Users(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(),
                image_url=fake.image_url(),
                role=random.choice(['donor', 'charity']),
            )
            db.session.add(user)
        db.session.commit()

def seed_charities(num_charities):
    with app.app_context():
        for _ in range(num_charities):
            charity = Charities(
                name=fake.company(),
                description=fake.text(),
                image_url=fake.image_url(),
                goal=random.uniform(1000.0, 50000.0),  # Random goal amount between 1000 and 10000
                raised=random.uniform(0.0, 45000.0),    # Random raised amount between 0 and 5000
                approved=True
            )
            db.session.add(charity)
        db.session.commit()

def seed_donations(num_donations, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_donations):
            user = random.choice(users)
            charity = random.choice(charities)
            donation = Donations(
                user_id=user.user_id,
                charity_id=charity.charity_id,
                amount=random.randint(10, 1000),
                is_anonymous=random.choice([True, False]),
                payment_method=random.choice(['paypal', 'stripe']),
                frequency=random.choice(['one-time', 'monthly'])
            )
            db.session.add(donation)
        db.session.commit()

def seed_stories(num_stories, num_charities):
    with app.app_context():
        charities = Charities.query.all()
        for _ in range(num_stories):
            charity = random.choice(charities)
            story = Stories(
                charity_id=charity.charity_id,
                title=fake.sentence(),
                content=fake.paragraph(),
                image_url=fake.image_url(),
                date_posted=fake.date_this_decade()
            )
            db.session.add(story)
        db.session.commit()

def seed_beneficiaries(num_beneficiaries, num_charities):
    with app.app_context():
        charities = Charities.query.all()
        for _ in range(num_beneficiaries):
            charity = random.choice(charities)
            beneficiary = Beneficiaries(
                name=fake.name(),
                description=fake.text(),
                charity_id=charity.charity_id,
                inventory_sent=random.choice([True, False]),
                image_url=fake.image_url()
            )
            db.session.add(beneficiary)
        db.session.commit()

def seed_admins(num_admins):
    with app.app_context():
        users = Users.query.all()
        for _ in range(num_admins):
            user = random.choice(users)
            admin = Admins(
                user_id=user.user_id
            )
            db.session.add(admin)
        db.session.commit()


def seed_items(num_items, num_charities):
    with app.app_context():
        charities = Charities.query.all()
        for _ in range(num_items):
            charity = random.choice(charities)
            item = Items(
                name=fake.word(),
                description=fake.text(),
                quantity=random.randint(1, 100),
                charity_id=charity.charity_id,
                image_url=fake.image_url()
            )
            db.session.add(item)
        db.session.commit()

def seed_reviews(num_reviews, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_reviews):
            user = random.choice(users)
            charity = random.choice(charities)
            review = Reviews(
                user_id=user.user_id,
                charity_id=charity.charity_id,
                rating=random.randint(1, 5),
                comment=fake.text(),
                date_posted=fake.date_this_decade()
            )
            db.session.add(review)
        db.session.commit()

def seed_words_of_support(num_words, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_words):
            user = random.choice(users)
            charity = random.choice(charities)
            support = WordsOfSupport(
                user_id=user.user_id,
                charity_id=charity.charity_id,
                message=fake.text(),
                date_posted=fake.date_this_decade()
            )
            db.session.add(support)
        db.session.commit()

def seed_payment_transactions(num_transactions, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_transactions):
            user = random.choice(users)
            charity = random.choice(charities)
            transaction = PaymentTransactions(
                donor_id=user.user_id,
                charity_id=charity.charity_id,
                amount=random.randint(10, 1000),
                payment_method=random.choice(['paypal', 'stripe']),
                transaction_status=random.choice(['success', 'pending', 'failed']),
                date_paid=fake.date_this_decade()
            )
            db.session.add(transaction)
        db.session.commit()

def seed_donor_payment_methods(num_methods, num_users):
    with app.app_context():
        users = Users.query.all()
        for _ in range(num_methods):
            user = random.choice(users)
            method = DonorPaymentMethods(
                donor_id=user.user_id,
                payment_method_name=random.choice(['paypal', 'stripe', 'credit_card']),
                payment_method_details=fake.credit_card_full()
            )
            db.session.add(method)
        db.session.commit()

def seed_reminder_settings(num_settings, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_settings):
            user = random.choice(users)
            charity = random.choice(charities)
            setting = ReminderSettings(
                donor_id=user.user_id,
                charity_id=charity.charity_id,
                reminder_time=fake.time(),
                is_active=random.choice([True, False])
            )
            db.session.add(setting)
        db.session.commit()

def seed_regular_donations(num_donations, num_users, num_charities):
    with app.app_context():
        users = Users.query.all()
        charities = Charities.query.all()
        for _ in range(num_donations):
            user = random.choice(users)
            charity = random.choice(charities)
            donation = RegularDonations(
                donor_id=user.user_id,
                charity_id=charity.charity_id,
                frequency=random.choice(['weekly', 'monthly', 'quarterly']),
                start_date=fake.date_this_decade(),
                end_date=fake.date_this_decade()
            )
            db.session.add(donation)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        num_users = 20
        num_charities = 20
        num_donations = 100
        num_stories = 50
        num_beneficiaries = 50
        num_admins = 5
        num_items = 10
        num_reviews = 100
        num_words = 100
        num_transactions = 100
        num_methods = 50
        num_settings = 50
        num_regular_donations = 50
        

        seed_users(num_users)
        seed_charities(num_charities)
        seed_donations(num_donations, num_users, num_charities)
        seed_stories(num_stories, num_charities)
        seed_beneficiaries(num_beneficiaries, num_charities)
        seed_admins(num_admins)
        seed_items(num_items, num_charities)
        seed_reviews(num_reviews, num_users, num_charities)
        seed_words_of_support(num_words, num_users, num_charities)
        seed_payment_transactions(num_transactions, num_users, num_charities)
        seed_donor_payment_methods(num_methods, num_users)
        seed_reminder_settings(num_settings, num_users, num_charities)
        seed_regular_donations(num_regular_donations, num_users, num_charities)
