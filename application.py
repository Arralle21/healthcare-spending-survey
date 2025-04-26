from flask import Flask, render_template, request, redirect, url_for, send_file
import pymongo
import pandas as pd
from datetime import datetime
import os
import json
from bson import json_util
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
import sys
import boto3
from botocore.exceptions import ClientError
import io

# Initialize Flask application
application = Flask(__name__, template_folder='templates', static_folder='static')
app = application  # For compatibility with existing code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure data directory (critical for EB)
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.getcwd(), 'data'))
os.makedirs(DATA_DIR, exist_ok=True)
os.chmod(DATA_DIR, 0o777)  # Ensure write permissions
logger.info(f"Using data directory: {DATA_DIR}")

# S3 Configuration
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'healthcare-survey-data')  # Set the bucket name you've created
USE_S3 = True  # Always try to use S3 if AWS credentials are available
logger.info(f"S3 configuration: Bucket={S3_BUCKET}, Use S3={USE_S3}")

def get_s3_client():
    """Create and return an S3 client"""
    if not USE_S3:
        return None
    
    try:
        s3_client = boto3.client('s3',
            region_name=os.environ.get('AWS_REGION', 'us-west-2')
        )
        logger.info("Successfully connected to S3")
        return s3_client
    except Exception as e:
        logger.error(f"Failed to connect to S3: {str(e)}")
        return None

# MongoDB Configuration
def get_mongo_client():
    try:
        mongodb_uri = os.environ.get(
            'MONGODB_URI',
            'mongodb+srv://abdulaahimohamed65:oHavsLz1m1OiLTOU@cluster0.jytzac6.mongodb.net/'
            '?retryWrites=true&w=majority&appName=Cluster0&tls=true'
        )
        
        client = pymongo.MongoClient(
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
        
        # Verify connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client
        
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected MongoDB error: {str(e)}")
    
    return None

# Initialize MongoDB connection
try:
    client = get_mongo_client()
    if client:
        db = client["healthcare_survey"]
        users_collection = db["users"]
        # Create index if it doesn't exist
        if "submission_date_1" not in users_collection.index_information():
            users_collection.create_index([("submission_date", pymongo.DESCENDING)], background=True)
        logger.info("MongoDB initialized successfully")
    else:
        logger.warning("MongoDB client is None - running in offline mode?")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {str(e)}")
    client = None

# Initialize S3 client
s3_client = get_s3_client()

@application.route('/health')
def health_check():
    """Enhanced health check endpoint"""
    status = {
        "mongodb": "Not configured",
        "data_dir": "Not checked",
        "s3": "Not configured"
    }
    
    try:
        # Check MongoDB connection
        if client:
            client.admin.command('ping')
            status["mongodb"] = "Connected"
        
        # Check data directory accessibility
        test_file = os.path.join(DATA_DIR, '.healthcheck')
        with open(test_file, 'w') as f:
            f.write(datetime.now().isoformat())
        os.remove(test_file)
        status["data_dir"] = "Writable"
        
        # Check S3 connection
        if s3_client:
            s3_client.list_buckets()
            status["s3"] = "Connected"
            
        return json.dumps(status), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        status["error"] = str(e)
        return json.dumps(status), 503, {'Content-Type': 'application/json'}

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
            
            # Store in MongoDB
            if client:
                result = users_collection.insert_one(user_data)
                logger.info(f"Inserted document with ID {result.inserted_id}")
                export_to_csv()
            
            return render_template('thank_you.html')
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return render_template('error.html', error=str(e)), 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return render_template('error.html', error="An unexpected error occurred"), 500

@application.route('/download')
def download_data():
    """Add a route to download the latest CSV data"""
    if USE_S3 and s3_client:
        try:
            # Generate a presigned URL for downloading from S3
            presigned_url = s3_client.generate_presigned_url('get_object',
                Params={'Bucket': S3_BUCKET, 'Key': 'user_data.csv'},
                ExpiresIn=3600
            )
            return redirect(presigned_url)
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return render_template('error.html', error="Failed to retrieve data file"), 500
    else:
        # Local file download
        try:
            csv_path = os.path.join(DATA_DIR, 'user_data.csv')
            if os.path.exists(csv_path):
                return send_file(csv_path, as_attachment=True)
            else:
                return render_template('error.html', error="Data file not found"), 404
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            return render_template('error.html', error="Failed to download file"), 500

def export_to_csv():
    """Enhanced CSV export function with S3 support"""
    if not client:
        logger.warning("Skipping CSV export - no MongoDB connection")
        return
        
    try:
        cursor = users_collection.find({})
        data = json.loads(json_util.dumps(list(cursor)))
        
        processed_data = []
        for user in data:
            record = {
                'age': user['age'],
                'gender': user['gender'],
                'total_income': user['total_income'],
                'submission_date': user['submission_date']['$date']
            }
            
            # Extract expense categories
            if 'expenses' in user:
                for category, amount in user['expenses'].items():
                    record[category] = amount
                    
            processed_data.append(record)
        
        df = pd.DataFrame(processed_data)
        
        # Always save locally first
        csv_path = os.path.join(DATA_DIR, 'user_data.csv')
        try:
            # Ensure proper file permissions
            if os.path.exists(csv_path):
                os.chmod(csv_path, 0o666)
            
            df.to_csv(csv_path, index=False)
            os.chmod(csv_path, 0o666)  # Set permissions after write
            logger.info(f"Successfully exported data to local file: {csv_path}")
        except Exception as e:
            logger.error(f"Local CSV export failed: {str(e)}", exc_info=True)
        
        # Upload to S3 if configured
        if USE_S3 and s3_client:
            try:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key='user_data.csv',
                    Body=csv_buffer.getvalue(),
                    ContentType='text/csv'
                )
                logger.info(f"Successfully uploaded data to S3 bucket: {S3_BUCKET}")
            except Exception as e:
                logger.error(f"S3 upload failed: {str(e)}", exc_info=True)
        
    except Exception as e:
        logger.error(f"CSV export process failed: {str(e)}", exc_info=True)

if __name__ == '__main__':
    # Additional initialization checks
    try:
        # Verify data directory
        test_file = os.path.join(DATA_DIR, '.startup_check')
        with open(test_file, 'w') as f:
            f.write(datetime.now().isoformat())
        os.remove(test_file)
        
        logger.info("Startup checks passed")
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}")
        sys.exit(1)
    
    application.run(debug=False, host='0.0.0.0', port=8000)