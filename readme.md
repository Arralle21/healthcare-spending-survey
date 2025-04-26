# Healthcare Spending Survey Application
#Submitted : Abdullahi Mohamed Jibril 

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3.2-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen)
![AWS](https://img.shields.io/badge/AWS-EB-orange)

##  Live Deployment
[![Open in Browser](https://img.shields.io/badge/Production-Live%20Site-success)](http://healthcare-survey-new.eba-q77ahvcn.us-west-2.elasticbeanstalk.com)
[![Demo](https://img.shields.io/badge/Demo-Video-important)](https://youtu.be/your-demo-link) *(optional)*

## Features

- **Responsive Survey Form**: Collects age, gender, income, and expense breakdowns
- **Real-time Data Storage**: MongoDB Atlas with automatic backups
- **CSV Export**: Daily exports to AWS S3 (`healthcare-survey-data` bucket)
- **Interactive Analysis**: [View Jupyter Notebook](analysis/data_analysis.ipynb)

## Quick Deployment

### Try the Live Version
Access the production deployment:  
🔗 [Production Site](http://healthcare-survey-new.eba-q77ahvcn.us-west-2.elasticbeanstalk.com)

### API Endpoints
| Endpoint | Description |
|----------|-------------|
| `/` | Survey form |
| `/submit` | POST endpoint for submissions |
| `/download` | CSV export |
| `/health` | System status |

##  Local Setup
bash
# Clone with HTTPS
git clone https://github.com/Arralle21/healthcare-spending-survey.git

# Or with SSH
git clone git@github.com:Arralle21/healthcare-spending-survey.git
Configuration
Get MongoDB URI from Atlas Console

Create .env file:

MONGODB_URI="mongodb+srv://<user>:<password>@cluster0.jytzac6.mongodb.net/?retryWrites=true&w=majority"
S3_BUCKET_NAME="your-bucket-name"
AWS_REGION="us-west-2"

🔧 Troubleshooting
Issue: MongoDB connection fails
 Solution: Verify IP Whitelisting in Atlas

Issue: S3 upload errors
✅Check IAM permissions for s3:PutObject






