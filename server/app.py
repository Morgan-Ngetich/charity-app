import os
from flask import Flask, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from models import db, Users, Charities, Donations, Stories, Beneficiaries, Admins, Items, Reviews, WordsOfSupport, PaymentTransactions, DonorPaymentMethods, ReminderSettings, RegularDonations, InventoryItems

load_dotenv()

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
api = Api(app)



# Define API resources
class UsersResource(Resource):
    def get(self):
        users = Users.query.all()
        return jsonify([user.serialize() for user in users])

class CharitiesResource(Resource):
    def get(self):
        charities = Charities.query.all()
        return jsonify([charity.serialize() for charity in charities])

class DonationsResource(Resource):
    def get(self):
        donations = Donations.query.all()
        return jsonify([donation.serialize() for donation in donations])

class StoriesResource(Resource):
    def get(self):
        stories = Stories.query.all()
        return jsonify([story.serialize() for story in stories])

class BeneficiariesResource(Resource):
    def get(self):
        beneficiaries = Beneficiaries.query.all()
        return jsonify([beneficiary.serialize() for beneficiary in beneficiaries])

class AdminsResource(Resource):
    def get(self):
        admins = Admins.query.all()
        return jsonify([admin.serialize() for admin in admins])

class ItemsResource(Resource):
    def get(self):
        items = Items.query.all()
        return jsonify([item.serialize() for item in items])

class ReviewsResource(Resource):
    def get(self):
        reviews = Reviews.query.all()
        return jsonify([review.serialize() for review in reviews])

class WordsOfSupportResource(Resource):
    def get(self):
        words_of_support = WordsOfSupport.query.all()
        return jsonify([support.serialize() for support in words_of_support])

class PaymentTransactionsResource(Resource):
    def get(self):
        payment_transactions = PaymentTransactions.query.all()
        return jsonify([transaction.serialize() for transaction in payment_transactions])

class DonorPaymentMethodsResource(Resource):
    def get(self):
        donor_payment_methods = DonorPaymentMethods.query.all()
        return jsonify([method.serialize() for method in donor_payment_methods])

class ReminderSettingsResource(Resource):
    def get(self):
        reminder_settings = ReminderSettings.query.all()
        return jsonify([setting.serialize() for setting in reminder_settings])

class RegularDonationsResource(Resource):
    def get(self):
        regular_donations = RegularDonations.query.all()
        return jsonify([donation.serialize() for donation in regular_donations])

class InventoryItemsResource(Resource):
    def get(self):
        inventory_items = InventoryItems.query.all()
        return jsonify([item.serialize() for item in inventory_items])

# Add API routes
api.add_resource(UsersResource, '/users')
api.add_resource(CharitiesResource, '/charities')
api.add_resource(DonationsResource, '/donations')
api.add_resource(StoriesResource, '/stories')
api.add_resource(BeneficiariesResource, '/beneficiaries')
api.add_resource(AdminsResource, '/admins')
api.add_resource(ItemsResource, '/items')
api.add_resource(ReviewsResource, '/reviews')
api.add_resource(WordsOfSupportResource, '/words_of_support')
api.add_resource(PaymentTransactionsResource, '/payment_transactions')
api.add_resource(DonorPaymentMethodsResource, '/donor_payment_methods')
api.add_resource(ReminderSettingsResource, '/reminder_settings')
api.add_resource(RegularDonationsResource, '/regular_donations')
api.add_resource(InventoryItemsResource, '/inventory_items')

if __name__ == '__main__':
    app.run(debug=True)
