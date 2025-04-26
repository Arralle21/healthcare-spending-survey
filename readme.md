# Healthcare Spending Survey Application  
**Submitted by**: Abdullahi Mohamed Jibril  
![Python](https://img.shields.io/badge/Python-3.11%2B-blue) 
![Flask](https://img.shields.io/badge/Flask-2.3.2-green) 
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen) 
![AWS](https://img.shields.io/badge/AWS-EB-orange)

##  Live Deployment
[![Production Site](https://img.shields.io/badge/Production-Live_Site-blue)](http://healthcare-survey-new.eba-q77ahvcn.us-west-2.elasticbeanstalk.com)

##  System Architecture
![Healthcare Data Flow Diagram](docs/assets/data_flow.png)
*Figure 1: End-to-end data collection pipeline*

## Key Features
- **Responsive Survey Form** with client-side validation
- **Real-time MongoDB Storage** with Atlas backups
- **Automated CSV Exports** to AWS S3 (daily)
- **Interactive Visualizations** in Jupyter Notebook

## Quick Start
bash
# Clone repository
git clone https://github.com/Arralle21/healthcare-spending-survey.git
cd healthcare-spending-survey

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "MONGODB_URI=your_connection_string" > .env
echo "S3_BUCKET_NAME=your-bucket-name" >> .env

# Launch application
python application.py
🔧 API Endpoints
Endpoint	Method	Description
/	GET	Survey form
/submit	POST	Data submission endpoint
/download	GET	CSV export
/health	GET	System status check
🛠 Troubleshooting
MongoDB Connection Issues
✅ Verify IP Access List in Atlas
✅ Check connection string format

S3 Upload Failures
✅ Confirm IAM role has s3:PutObject permission
✅ Validate bucket name and region
