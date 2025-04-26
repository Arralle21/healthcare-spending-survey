from flask import Flask, render_template, request, redirect, url_for
import pymongo
import pandas as pd
from datetime import datetime
import os
import json
from bson import json_util
import logging
from pymongo.errors import ConnectionFailure, OperationFailure

# Initialize Flask application
application = Flask(__name__, template_folder='templates', static_folder='static')
app = application  # For compatibility with existing code

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    def __init__(self, mongodb_uri=None):
        """Initialize User class with MongoDB connection"""
        self.client = None
        self.db = None
        self.collection = None
        self.connect(mongodb_uri)
        
    def connect(self, mongodb_uri):
        """Establish MongoDB connection"""
        try:
            if not mongodb_uri:
                mongodb_uri = os.environ.get(
                    'MONGODB_URI',
                    'mongodb+srv://abdulaahimohamed65:oHavsLz1m1OiLTOU@cluster0.jytzac6.mongodb.net/'
                    '?retryWrites=true&w=majority&appName=Cluster0&tls=true'
                )
            
            self.client = pymongo.MongoClient(
                mongodb_uri,
                tls=True,
                tlsAllowInvalidCertificates=False,
                connectTimeoutMS=30000,
                socketTimeoutMS=None,
                serverSelectionTimeoutMS=5000,
                connect=False,
                maxPoolSize=1,
                retryWrites=True,
                w='majority'
            )
            self.db = self.client["healthcare_survey"]
            self.collection = self.db["users"]
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB via User class")
            
            # Create index if it doesn't exist
            if "submission_date_1" not in self.collection.index_information():
                self.collection.create_index([("submission_date", pymongo.DESCENDING)])
                
        except Exception as e:
            logger.error(f"User class MongoDB connection failed: {str(e)}")
            self.client = None
    
    def get_all_users(self):
        """Get all users from MongoDB"""
        if not self.collection:
            return []
        try:
            cursor = self.collection.find({})
            return json.loads(json_util.dumps(list(cursor)))
        except Exception as e:
            logger.error(f"Failed to get users: {str(e)}")
            return []
    
    def export_to_csv(self, output_path=None):
        """Export all users to CSV file"""
        if not output_path:
            output_path = os.path.join(os.getcwd(), 'data', 'user_data.csv')
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get all users
            users = self.get_all_users()
            if not users:
                logger.info("No users found to export")
                return None
                
            # Process data
            processed_data = []
            for user in users:
                record = {
                    'age': user['age'],
                    'gender': user['gender'],
                    'total_income': user['total_income'],
                    'submission_date': user['submission_date']['$date']
                }
                
                # Extract expense categories
                if 'expenses' in user:
                    for category, amount in user['expenses'].items():
                        record[f'{category}_expense'] = amount
                        
                processed_data.append(record)
            
            # Create DataFrame and export
            df = pd.DataFrame(processed_data)
            df.to_csv(output_path, index=False)
            logger.info(f"User class exported data to {output_path}")
            return df
            
        except Exception as e:
            logger.error(f"User class CSV export failed: {str(e)}")
            return None
    
    def add_user(self, user_data):
        """Add a new user to MongoDB"""
        if not self.collection:
            return None
        try:
            result = self.collection.insert_one(user_data)
            logger.info(f"Added new user with ID {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to add user: {str(e)}")
            return None

# Initialize User class
try:
    user_manager = User()
    if not user_manager.client:
        logger.warning("User class failed to initialize MongoDB connection")
except Exception as e:
    logger.error(f"Failed to initialize User class: {str(e)}")
    user_manager = None

# Ensure data directory exists
DATA_DIR = os.path.join(os.getcwd(), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

@application.route('/health')
def health_check():
    """Endpoint for health checks"""
    try:
        if user_manager and user_manager.client:
            user_manager.client.admin.command('ping')
            return "OK", 200
        return "OK (no DB)", 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return "Service Unavailable", 503

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        try:
            # Form validation
            age = int(request.form['age'])
            gender = request.form['gender']
            total_income = float(request.form['income'])
            
            if age < 18 or age > 120:
                raise ValueError("Age must be between 18 and 120")
            if total_income < 0:
                raise ValueError("Income cannot be negative")

            # Process expenses
            expenses = {}
            categories = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
            
            for category in categories:
                if request.form.get(category):
                    amount = float(request.form.get(f"{category}_amount", 0))
                    if amount < 0:
                        raise ValueError(f"{category} amount cannot be negative")
                    expenses[category] = amount

            # Create document
            user_data = {
                "age": age,
                "gender": gender,
                "total_income": total_income,
                "expenses": expenses,
                "submission_date": datetime.now(),
                "ip_address": request.remote_addr
            }
            
            # Store in MongoDB using User class
            if user_manager:
                inserted_id = user_manager.add_user(user_data)
                if inserted_id:
                    user_manager.export_to_csv()
            
            return render_template('thank_you.html')
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return render_template('error.html', error=str(e)), 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return render_template('error.html', error="An unexpected error occurred"), 500

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=8000)