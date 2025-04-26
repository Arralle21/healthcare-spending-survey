# Healthcare Spending Survey Application
# Submitted by : Abdullahi Mohamed Jibril

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3.2-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen)

A secure web application for collecting and analyzing healthcare expenditure data with cloud storage and visualization capabilities.

## Features

- 📝 Interactive survey form with validation
- 🗄️ MongoDB cloud database storage
- 📊 Automated CSV exports to S3
- 📈 Jupyter Notebook data visualization
- ☁️ AWS Elastic Beanstalk deployment ready
- 🔒 Environment-based security configuration

## Quick Start

### 1. Clone Repository
-Bash
git clone https://github.com/Arralle21/healthcare-spending-survey.git
cd healthcare-spending-survey

## Setup environment Variable

python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt

## Configure Environment 
MONGODB_URI=your_mongodb_connection_string
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=us-west-2
FLASK_ENV=development

## Run Application
python application.py

## Deployement 
Install EB CLI:pip install awsebcli
eb init
eb create healthcare-survey-prod
eb deploy

## Environment Variables
Configure in EB Console:
MONGODB_URI
S3_BUCKET_NAME
AWS_REGION
FLASK_ENV=production

________________________________________________________________________________________________________________________________________________________________________________________________________________
                                                                                           Thanks

