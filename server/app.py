from dotenv import load_dotenv
import os
import json
import binascii
from datetime import timedelta
from flask import Flask, jsonify, request, make_response, session
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse 
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token,get_jwt
import bcrypt
from bcrypt import checkpw
from werkzeug.security import check_password_hash
from email_validator import validate_email, EmailNotValidError

from wtforms import Form, StringField, PasswordField, validators, ValidationError
from models import db, Users, Charities, Donations, Stories, Beneficiaries, Admins, ContactDetails, Message, Items, Reviews, WordsOfSupport, PaymentTransactions, DonorPaymentMethods, ReminderSettings, RegularDonations

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError



def create_app():
    app = Flask(__name__)   
   
    blacklist = set()  # Define the blacklist set for storing JWT tokens   
    mail = Mail() # Initialize the Mail object
    
    # Load environment variables from .env file
    load_dotenv()

    # Set JWT secret key if not already set
    if 'JWT_SECRET_KEY' not in os.environ:
        os.environ['JWT_SECRET_KEY'] = binascii.hexlify(os.urandom(32)).decode()
        
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Short expiration time for access token
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)   # Longer expiration time for refresh token
    app.config['WTF_CSRF_ENABLED'] = False

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
   
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Configure mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    mail = Mail(app)

    # Configure JWT
    jwt = JWTManager(app)

    migrate = Migrate(app, db)
    api = Api(app)
    
    
    class SignupForm(Form):      
        username = StringField('Username', validators=[validators.DataRequired()])
        email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
        password = PasswordField('Password', validators=[validators.DataRequired()])
        phone_number = StringField('Phone Number')  # Optional field
        
        def validate_email(self, field):
            try:
                validate_email(field.data)
            except EmailNotValidError:
                raise ValidationError('Invalid email address')


    


    class LoginForm(Form):
        email = StringField('Email', validators=[validators.InputRequired(), validators.Email()])
        password = PasswordField('Password', validators=[validators.InputRequired()])


    def validate_token(token):
        return token['jti'] in blacklist

    # Send message email function
    def send_message_email(user_id, charity_email, message, charity_name, charity_mission):
        user = Users.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        sender_email = user.email

        try:
            # Send email to charity
            msg_to_charity = Message(subject='New Message from a User', sender=sender_email, recipients=[charity_email])
            msg_to_charity.body = f'New message from a user: {message}'
            mail.send(msg_to_charity)

            # Send email to user
            msg_to_user = Message(subject='Your Support Means the World to Us!', sender=[charity_email], recipients=[sender_email])
            msg_to_user.body = f"""Dear {user.username},\n\nThank you for reaching out to {charity_name}! We've received your message and are grateful for your interest in supporting our cause.\n\nYour generosity can make a real difference in the lives of those we serve. Please consider making a donation today to help us continue our mission of {charity_mission}.\n\nClick here to donate now and make an impact: [Donation Link]\n\nYour support is invaluable to us, and we appreciate your commitment to making the world a better place.\n\nThank you for being a part of our journey.\n\nWarm regards,\nThe {charity_name} Team"""
            mail.send(msg_to_user)
        except Exception as e:
            # Handle email sending error
            app.logger.error(f"Error sending email: {e}")
            raise

        return None


    # Define API resources
    @app.route('/signup', methods=['POST'])
    def signup():
        form_data = request.get_json()
        form = SignupForm(data=form_data)
        if form.validate():
            username = form.username.data
            phone_number = form.phone_number.data
            email = form.email.data
            password = form.password.data

            if Users.query.filter_by(email=email).first():
                return jsonify(message='User already exists'), 400

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            new_user = Users(username=username, phone_number=phone_number, email=email, password=hashed_password.decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=email)
            return jsonify(access_token=access_token), 201
        else:
            return jsonify(errors=form.errors), 400

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        print("Request JSON data:", data)  # Print the entire request JSON data for debugging
        
        email = data.get('email', {}).get('email', '')  # Access email from nested structure
        password = data.get('email', {}).get('password', '')  # Access password from nested structure

        if email == '' or password == '':
            return jsonify(errors={"email": ["This field is required."], "password": ["This field is required."]}), 400

        user = Users.query.filter_by(email=email).first()
        if user and checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)           
            return jsonify(access_token=access_token), 200
        else:
            return jsonify(message="Invalid email or password"), 401



                            
    
    @app.route('/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify(access_token=access_token), 200

    @app.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        jti = get_jwt()['jti']
        blacklist.add(jti)
        return jsonify(message='Successfully logged out'), 200
    
    
    
    # Define API resources
    class UsersResource(Resource):
        def get(self):
            users = Users.query.all()
            return jsonify([user.serialize() for user in users])

        def post(self):
            data = request.json
            email = data.get('email')
            user = Users.query.filter_by(email=email).first()
            if user:
                return {'message': 'User already exists'}, 400
            new_user = Users(**data)
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created successfully'}, 201

    class UserDetailResource(Resource):
        def get(self, user_id):
            user = Users.query.get(user_id)
            if user:
                return jsonify(user.serialize())
            else:
                return {'message': 'User not found'}, 404

        def put(self, user_id):
            data = request.json
            user = Users.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
            return {'message': 'User updated successfully'}, 200

        def delete(self, user_id):
            user = Users.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200


    class CharitiesResource(Resource):
        def get(self):
            charities = Charities.query.all()
            charities_data = []
            for charity in charities:
                contact_details = ContactDetails.query.filter_by(charity_id=charity.charity_id).all()
                messages = Message.query.filter_by(charity_id=charity.charity_id).all()
                charity_data = charity.serialize()
                charity_data['contact_details'] = [contact.serialize() for contact in contact_details]
                charity_data['messages'] = [message.serialize() for message in messages]
                charities_data.append(charity_data)
            return jsonify(charities_data)

        def post(self):
            # Parse the request data from request.form
            data = request.json
            description = data.get('description')
            goal = data.get('goal')
            image_url = data.get('image_url')
            mission = data.get('mission')
            name = data.get('name')
            raised = data.get('raised')
            contact_details_data = data.get('contact_details')
            status = data.get("status")
            category = data.get("category")

            charity = Charities(
                description=description,
                goal=goal,
                image_url=image_url,
                mission=mission,
                name=name,
                raised=raised,
                status=status,
                category=category                
            )

            for contact_detail_data in contact_details_data:
                contact_detail = ContactDetails(
                    phone_number=contact_detail_data.get('phone_number'),
                    charity_email=contact_detail_data.get('charity_email'),
                    map_details=contact_detail_data.get('map_details'),
                    charity=charity
                )
                db.session.add(contact_detail)

            db.session.add(charity)
            db.session.commit()

            return make_response(jsonify({'message': 'Post created successfully'}), 201)



    class CharityDetailResource(Resource):
        def get(self, charity_id):
            charity = Charities.query.get(charity_id)
            if not charity:
                return {'message': 'Charity not found'}, 404

            # Get contact details for the charity
            contact_details = ContactDetails.query.filter_by(charity_id=charity_id).all()

            # Get messages for the charity
            messages = Message.query.filter_by(charity_id=charity_id).all()

            # Serialize charity, contact details, and messages
            charity_data = charity.serialize()
            charity_data['contact_details'] = [contact.serialize() for contact in contact_details]
            charity_data['messages'] = [message.serialize() for message in messages]

            return jsonify(charity_data)

        def put(self, charity_id):
            data = request.json
            charity = Charities.query.get(charity_id)
            if not charity:
                return {'message': 'Charity not found'}, 404
            for key, value in data.items():
                setattr(charity, key, value)
            db.session.commit()
            return {'message': 'Charity updated successfully'}, 200

        def delete(self, charity_id):
            charity = Charities.query.get(charity_id)
            if not charity:
                return {'message': 'Charity not found'}, 404
            db.session.delete(charity)
            db.session.commit()
            return {'message': 'Charity deleted successfully'}, 200
        
        
    class SendMessageResource(Resource):
        def post(self, charity_id):
            data = request.json
            message_text = data.get('message')
            user_id = data.get('user_id')

            # Check if user_id and charity_id are valid
            user = Users.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404

            charity = Charities.query.get(charity_id)
            if not charity:
                return {'message': 'Charity not found'}, 404

            try:
                # Check if the charity has existing contact details
                contact_details = ContactDetails.query.filter_by(charity_id=charity_id).first()
                if not contact_details:
                    # Create new contact details if none exist
                    contact_details = ContactDetails(charity_id=charity_id)
                    db.session.add(contact_details)
                    db.session.commit()

                # Save message to the database
                new_message = Message(user_id=user_id, message=message_text, contact_details_id=contact_details.id)
                db.session.add(new_message)
                db.session.commit()

                # Send email to charity
                send_message_email(user_id, charity.email, message_text)

                return {'message': 'Message sent successfully'}, 200
            except Exception as e:
                # Handle email sending error
                app.logger.error(f"Error sending email: {e}")
                return {'message': 'An error occurred while sending the message'}, 500



    class DonationsResource(Resource):
        def get(self):
            donations = Donations.query.all()
            return jsonify([donation.serialize() for donation in donations])

        def post(self):
            data = request.json
            donation = Donations(**data)
            db.session.add(donation)
            db.session.commit()
            return {'message': 'Donation created successfully'}, 201

    class DonationDetailResource(Resource):
        def get(self, donation_id):
            donation = Donations.query.get(donation_id)
            if donation:
                return jsonify(donation.serialize())
            else:
                return {'message': 'Donation not found'}, 404

        def put(self, donation_id):
            data = request.json
            donation = Donations.query.get(donation_id)
            if not donation:
                return {'message': 'Donation not found'}, 404
            for key, value in data.items():
                setattr(donation, key, value)
            db.session.commit()
            return {'message': 'Donation updated successfully'}, 200

        def delete(self, donation_id):
            donation = Donations.query.get(donation_id)
            if not donation:
                return {'message': 'Donation not found'}, 404
            db.session.delete(donation)
            db.session.commit()
            return {'message': 'Donation deleted successfully'}, 200


    class StoriesResource(Resource):
        def get(self):
            stories = Stories.query.all()
            return jsonify([story.serialize() for story in stories])

        def post(self):
            data = request.json
            story = Stories.query.filter_by(id=data.get('id')).first()
            if story:
                return {'message': 'Story already exists'}, 400
            new_story = Stories(**data)
            db.session.add(new_story)
            db.session.commit()
            return {'message': 'Story created successfully'}, 201

    class StoriesDetailResource(Resource):
        def get(self, story_id):
            story = Stories.query.get(story_id)
            if story:
                return jsonify(story.serialize())
            else:
                return {'message': 'Story not found'}, 404

        def put(self, story_id):
            data = request.json
            story = Stories.query.get(story_id)
            if not story:
                return {'message': 'Story not found'}, 404
            for key, value in data.items():
                setattr(story, key, value)
            db.session.commit()
            return {'message': 'Story updated successfully'}, 200

        def delete(self, story_id):
            story = Stories.query.get(story_id)
            if not story:
                return {'message': 'Story not found'}, 404
            db.session.delete(story)
            db.session.commit()
            return {'message': 'Story deleted successfully'}, 200

    class BeneficiariesResource(Resource):
        def get(self):
            beneficiaries = Beneficiaries.query.all()
            return jsonify([beneficiary.serialize() for beneficiary in beneficiaries])

        def post(self):
            data = request.json
            beneficiary = Beneficiaries.query.filter_by(id=data.get('id')).first()
            if beneficiary:
                return {'message': 'Beneficiary already exists'}, 400
            new_beneficiary = Beneficiaries(**data)
            db.session.add(new_beneficiary)
            db.session.commit()
            return {'message': 'Beneficiary created successfully'}, 201

    class BeneficiariesDetailResource(Resource):
        def get(self, beneficiary_id):
            beneficiary = Beneficiaries.query.get(beneficiary_id)
            if beneficiary:
                return jsonify(beneficiary.serialize())
            else:
                return {'message': 'Beneficiary not found'}, 404

        def put(self, beneficiary_id):
            data = request.json
            beneficiary = Beneficiaries.query.get(beneficiary_id)
            if not beneficiary:
                return {'message': 'Beneficiary not found'}, 404
            for key, value in data.items():
                setattr(beneficiary, key, value)
            db.session.commit()
            return {'message': 'Beneficiary updated successfully'}, 200

        def delete(self, beneficiary_id):
            beneficiary = Beneficiaries.query.get(beneficiary_id)
            if not beneficiary:
                return {'message': 'Beneficiary not found'}, 404
            db.session.delete(beneficiary)
            db.session.commit()
            return {'message': 'Beneficiary deleted successfully'}, 200


    class AdminsResource(Resource):
        def get(self):
            admins = Admins.query.options(db.joinedload(Admins.user)).all()
            return jsonify([admin.serialize() for admin in admins])

        def post(self):
            data = request.json
            admin_id = data.get('id')
            admin = Admins.query.filter_by(id=admin_id).first()
            if admin:
                return {'message': 'Admin already exists'}, 400
            new_admin = Admins(**data)
            db.session.add(new_admin)
            db.session.commit()
            return {'message': 'Admin created successfully'}, 201

    class AdminsDetailResource(Resource):
        def get(self, admin_id):
            admin = Admins.query.get(admin_id)
            if admin:
                return jsonify(admin.serialize())
            else:
                return {'message': 'Admin not found'}, 404

        def put(self, admin_id):
            data = request.json
            admin = Admins.query.get(admin_id)
            if not admin:
                return {'message': 'Admin not found'}, 404
            for key, value in data.items():
                setattr(admin, key, value)
            db.session.commit()
            return {'message': 'Admin updated successfully'}, 200

        def delete(self, admin_id):
            admin = Admins.query.get(admin_id)
            if not admin:
                return {'message': 'Admin not found'}, 404
            db.session.delete(admin)
            db.session.commit()
            return {'message': 'Admin deleted successfully'}, 200

    class ItemsResource(Resource):
        def get(self):
            items = Items.query.all()
            return jsonify([item.serialize() for item in items])

        def post(self):
            data = request.json
            item_id = data.get('id')
            item = Items.query.filter_by(id=item_id).first()
            if item:
                return {'message': 'Item already exists'}, 400
            new_item = Items(**data)
            db.session.add(new_item)
            db.session.commit()
            return {'message': 'Item created successfully'}, 201

    class ItemsDetailResource(Resource):
        def get(self, item_id):
            item = Items.query.get(item_id)
            if item:
                return jsonify(item.serialize())
            else:
                return {'message': 'Item not found'}, 404

        def put(self, item_id):
            data = request.json
            item = Items.query.get(item_id)
            if not item:
                return {'message': 'Item not found'}, 404
            for key, value in data.items():
                setattr(item, key, value)
            db.session.commit()
            return {'message': 'Item updated successfully'}, 200

        def delete(self, item_id):
            item = Items.query.get(item_id)
            if not item:
                return {'message': 'Item not found'}, 404
            db.session.delete(item)
            db.session.commit()
            return {'message': 'Item deleted successfully'}, 200

    class ReviewsResource(Resource):
        def get(self):
            reviews = Reviews.query.all()
            return jsonify([review.serialize() for review in reviews])

        def post(self):
            data = request.json
            review_id = data.get('id')
            review = Reviews.query.filter_by(id=review_id).first()
            if review:
                return {'message': 'Review already exists'}, 400
            new_review = Reviews(**data)
            db.session.add(new_review)
            db.session.commit()
            return {'message': 'Review created successfully'}, 201

    class ReviewsDetailResource(Resource):
        def get(self, review_id):
            review = Reviews.query.get(review_id)
            if review:
                return jsonify(review.serialize())
            else:
                return {'message': 'Review not found'}, 404

        def put(self, review_id):
            data = request.json
            review = Reviews.query.get(review_id)
            if not review:
                return {'message': 'Review not found'}, 404
            for key, value in data.items():
                setattr(review, key, value)
            db.session.commit()
            return {'message': 'Review updated successfully'}, 200

        def delete(self, review_id):
            review = Reviews.query.get(review_id)
            if not review:
                return {'message': 'Review not found'}, 404
            db.session.delete(review)
            db.session.commit()
            return {'message': 'Review deleted successfully'}, 200

    class WordsOfSupportResource(Resource):
        def get(self):
            words_of_support = WordsOfSupport.query.all()
            return jsonify([support.serialize() for support in words_of_support])

        def post(self):
            data = request.json
            support_id = data.get('id')
            support = WordsOfSupport.query.filter_by(id=support_id).first()
            if support:
                return {'message': 'Words of support already exists'}, 400
            new_support = WordsOfSupport(**data)
            db.session.add(new_support)
            db.session.commit()
            return {'message': 'Words of support created successfully'}, 201

    class WordsOfSupportDetailResource(Resource):
        def get(self, support_id):
            support = WordsOfSupport.query.get(support_id)
            if support:
                return jsonify(support.serialize())
            else:
                return {'message': 'Words of support not found'}, 404

        def put(self, support_id):
            data = request.json
            support = WordsOfSupport.query.get(support_id)
            if not support:
                return {'message': 'Words of support not found'}, 404
            for key, value in data.items():
                setattr(support, key, value)
            db.session.commit()
            return {'message': 'Words of support updated successfully'}, 200

        def delete(self, support_id):
            support = WordsOfSupport.query.get(support_id)
            if not support:
                return {'message': 'Words of support not found'}, 404
            db.session.delete(support)
            db.session.commit()
            return {'message': 'Words of support deleted successfully'}, 200




    class PaymentTransactionsResource(Resource):
        def get(self):
            payment_transactions = PaymentTransactions.query.all()
            return jsonify([transaction.serialize() for transaction in payment_transactions])

        def post(self):
            data = request.json
            transaction_id = data.get('id')
            transaction = PaymentTransactions.query.filter_by(id=transaction_id).first()
            if transaction:
                return {'message': 'Payment transaction already exists'}, 400
            new_transaction = PaymentTransactions(**data)
            db.session.add(new_transaction)
            db.session.commit()
            return {'message': 'Payment transaction created successfully'}, 201

    class PaymentTransactionsDetailResource(Resource):
        def get(self, transaction_id):
            transaction = PaymentTransactions.query.get(transaction_id)
            if transaction:
                return jsonify(transaction.serialize())
            else:
                return {'message': 'Payment transaction not found'}, 404

        def put(self, transaction_id):
            data = request.json
            transaction = PaymentTransactions.query.get(transaction_id)
            if not transaction:
                return {'message': 'Payment transaction not found'}, 404
            for key, value in data.items():
                setattr(transaction, key, value)
            db.session.commit()
            return {'message': 'Payment transaction updated successfully'}, 200

        def delete(self, transaction_id):
            transaction = PaymentTransactions.query.get(transaction_id)
            if not transaction:
                return {'message': 'Payment transaction not found'}, 404
            db.session.delete(transaction)
            db.session.commit()
            return {'message': 'Payment transaction deleted successfully'}, 200

    class DonorPaymentMethodsResource(Resource):
        def get(self):
            donor_payment_methods = DonorPaymentMethods.query.all()
            return jsonify([method.serialize() for method in donor_payment_methods])

        def post(self):
            data = request.json
            method_id = data.get('id')
            method = DonorPaymentMethods.query.filter_by(id=method_id).first()
            if method:
                return {'message': 'Donor payment method already exists'}, 400
            new_method = DonorPaymentMethods(**data)
            db.session.add(new_method)
            db.session.commit()
            return {'message': 'Donor payment method created successfully'}, 201

    class DonorPaymentMethodsDetailResource(Resource):
        def get(self, method_id):
            method = DonorPaymentMethods.query.get(method_id)
            if method:
                return jsonify(method.serialize())
            else:
                return {'message': 'Donor payment method not found'}, 404

        def put(self, method_id):
            data = request.json
            method = DonorPaymentMethods.query.get(method_id)
            if not method:
                return {'message': 'Donor payment method not found'}, 404
            for key, value in data.items():
                setattr(method, key, value)
            db.session.commit()
            return {'message': 'Donor payment method updated successfully'}, 200

        def delete(self, method_id):
            method = DonorPaymentMethods.query.get(method_id)
            if not method:
                return {'message': 'Donor payment method not found'}, 404
            db.session.delete(method)
            db.session.commit()
            return {'message': 'Donor payment method deleted successfully'}, 200

    class ReminderSettingsResource(Resource):
        def get(self):
            reminder_settings = ReminderSettings.query.all()
            return jsonify([setting.serialize() for setting in reminder_settings])

        def post(self):
            data = request.json
            setting_id = data.get('id')
            setting = ReminderSettings.query.filter_by(id=setting_id).first()
            if setting:
                return {'message': 'Reminder setting already exists'}, 400
            new_setting = ReminderSettings(**data)
            db.session.add(new_setting)
            db.session.commit()
            return {'message': 'Reminder setting created successfully'}, 201

    class ReminderSettingsDetailResource(Resource):
        def get(self, setting_id):
            setting = ReminderSettings.query.get(setting_id)
            if setting:
                return jsonify(setting.serialize())
            else:
                return {'message': 'Reminder setting not found'}, 404

        def put(self, setting_id):
            data = request.json
            setting = ReminderSettings.query.get(setting_id)
            if not setting:
                return {'message': 'Reminder setting not found'}, 404
            for key, value in data.items():
                setattr(setting, key, value)
            db.session.commit()
            return {'message': 'Reminder setting updated successfully'}, 200

        def delete(self, setting_id):
            setting = ReminderSettings.query.get(setting_id)
            if not setting:
                return {'message': 'Reminder setting not found'}, 404
            db.session.delete(setting)
            db.session.commit()
            return {'message': 'Reminder setting deleted successfully'}, 200

    class RegularDonationsResource(Resource):
        def get(self):
            regular_donations = RegularDonations.query.all()
            return jsonify([donation.serialize() for donation in regular_donations])

        def post(self):
            data = request.json
            donation_id = data.get('id')
            donation = RegularDonations.query.filter_by(id=donation_id).first()
            if donation:
                return {'message': 'Regular donation already exists'}, 400
            new_donation = RegularDonations(**data)
            db.session.add(new_donation)
            db.session.commit()
            return {'message': 'Regular donation created successfully'}, 201

    class RegularDonationsDetailResource(Resource):
        def get(self, donation_id):
            donation = RegularDonations.query.get(donation_id)
            if donation:
                return jsonify(donation.serialize())
            else:
                return {'message': 'Regular donation not found'}, 404

        def put(self, donation_id):
            data = request.json
            donation = RegularDonations.query.get(donation_id)
            if not donation:
                return {'message': 'Regular donation not found'}, 404
            for key, value in data.items():
                setattr(donation, key, value)
            db.session.commit()
            return {'message': 'Regular donation updated successfully'}, 200

        def delete(self, donation_id):
            donation = RegularDonations.query.get(donation_id)
            if not donation:
                return {'message': 'Regular donation not found'}, 404
            db.session.delete(donation)
            db.session.commit()
            return {'message': 'Regular donation deleted successfully'}, 200

    
    api.add_resource(UsersResource, '/users')
    api.add_resource(UserDetailResource, '/users/<int:user_id>')
    
    api.add_resource(CharitiesResource, '/charities')
    api.add_resource(CharityDetailResource, '/charities/<int:charity_id>')
    api.add_resource(SendMessageResource, '/charities/<int:charity_id>/message')
    
    api.add_resource(DonationsResource, '/donations')
    api.add_resource(DonationDetailResource, '/donations/<int:donation_id>')
    
    api.add_resource(StoriesResource, '/stories')
    api.add_resource(StoriesDetailResource, '/stories/<int:story_id>')
    
    api.add_resource(BeneficiariesResource, '/beneficiaries')
    api.add_resource(BeneficiariesDetailResource, '/beneficiaries/<int:beneficiary_id>')
    
    api.add_resource(AdminsResource, '/admins')
    api.add_resource(AdminsDetailResource, '/admins/<int:admin_id>')
    
    api.add_resource(ItemsResource, '/items')
    api.add_resource(ItemsDetailResource, '/items/<int:item_id>')
    
    api.add_resource(ReviewsResource, '/reviews')
    api.add_resource(ReviewsDetailResource, '/reviews/<int:review_id>')
    
    api.add_resource(WordsOfSupportResource, '/words_of_support')
    api.add_resource(WordsOfSupportDetailResource, '/words_of_support/<int:support_id>')
    
    api.add_resource(PaymentTransactionsResource, '/payment_transactions')  # I also need to fetch the payment method based on user
    api.add_resource(PaymentTransactionsDetailResource, '/payment_transactions/<int:transaction_id>')
    
    api.add_resource(DonorPaymentMethodsResource, '/donor_payment_methods')  # I also need to fetch the payment method based on user
    api.add_resource(DonorPaymentMethodsDetailResource, '/donor_payment_methods/<int:method_id>')
    
    api.add_resource(ReminderSettingsResource, '/reminder_settings') # I also think I need to fetch the reminder_settings based on user
    api.add_resource(ReminderSettingsDetailResource, '/reminder_settings/<int:setting_id>')
    
    api.add_resource(RegularDonationsResource, '/regular_donations')
    api.add_resource(RegularDonationsDetailResource, '/regular_donations/<int:donation_id>')
    


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)