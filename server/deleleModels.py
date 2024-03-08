from app import create_app
from models import db, Users, Charities, Donations, Stories, Beneficiaries, Admins, Items, Reviews, WordsOfSupport, PaymentTransactions, DonorPaymentMethods, ReminderSettings, RegularDonations

# Create the app instance
app = create_app()

# Use the app context to make sure db.session is within the application context
with app.app_context():
    def delete_all_records():
        try:
            # Delete all RegularDonations
            db.session.query(RegularDonations).delete()

            # Delete all ReminderSettings
            db.session.query(ReminderSettings).delete()

            # Delete all DonorPaymentMethods
            db.session.query(DonorPaymentMethods).delete()

            # Delete all PaymentTransactions
            db.session.query(PaymentTransactions).delete()

            # Delete all WordsOfSupport
            db.session.query(WordsOfSupport).delete()

            # Delete all Reviews
            db.session.query(Reviews).delete()

            # Delete all Items
            db.session.query(Items).delete()

            # Delete all Admins
            db.session.query(Admins).delete()

            # Delete all Beneficiaries
            db.session.query(Beneficiaries).delete()

            # Delete all Stories
            db.session.query(Stories).delete()

            # Delete all Donations
            db.session.query(Donations).delete()

            # Delete all Charities
            db.session.query(Charities).delete()

            # Delete all Users
            db.session.query(Users).delete()

            # Commit the changes
            db.session.commit()

            print("All records deleted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            db.session.rollback()

    try:
        delete_all_records()
    except Exception as e:
        print(f"An error occurred: {e}")
