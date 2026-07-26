# FoodExpress – Secure Cloud-Based Food Ordering System

FoodExpress is a secure cloud-based food ordering web application developed as part of a DevSecOps capstone project.

The project demonstrates the integration of web application development, AWS cloud infrastructure, Linux administration, cybersecurity, Docker, CI/CD automation, backup and recovery, and centralized monitoring.

## Technologies Used

- Python Flask
- MySQL
- HTML, CSS and JavaScript
- Amazon EC2
- Ubuntu Linux
- Nginx
- Docker
- GitHub Actions
- Amazon CloudWatch
- Amazon SNS
- UFW Firewall
- Fail2Ban

## Main Features

- User registration and login
- Food ordering functionality
- User and administrator functionality
- MySQL database integration
- Secure password handling
- Nginx reverse proxy
- Linux server hardening
- Automated database and application backups
- CloudWatch monitoring and security alarms
- Docker-based application build
- GitHub Actions CI/CD workflow
- Application health-check endpoint

## Basic Setup

1. Clone the repository.
2. Navigate to the backend directory.
3. Create and activate a Python virtual environment.
4. Install the required packages from `requirements.txt`.
5. Configure the required database and application environment variables.
6. Configure the MySQL database.
7. Start the Flask application.
8. Configure Nginx as the reverse proxy for production deployment.

## Cloud Deployment

The FoodExpress application is deployed on an Ubuntu-based Amazon EC2 instance. AWS Security Groups and UFW are used for network protection, while SSH hardening and Fail2Ban provide additional server security.

Amazon CloudWatch is used for infrastructure and security monitoring, with Amazon SNS configured for alarm notifications.

## DevOps

The project uses Docker for application containerization and GitHub Actions for CI/CD automation.

The CI workflow automatically builds the FoodExpress Docker image. A CD workflow is also configured for AWS deployment through AWS Systems Manager (SSM) using OIDC authentication.

## Backup and Monitoring

Automated backups are scheduled using a Linux cron job. Application and database backup operations are handled by the server backup script.

CloudWatch alarms monitor server health, CPU utilization, failed login attempts, and suspicious sudo activity.

## Project Author

**Sandra PS**  
St. Teresa's College (Autonomous), Ernakulam
