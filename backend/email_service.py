import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import logging
from email_templates.password_reset import send_password_reset_email

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_complaint_confirmation(recipient_email, tracking_id, complaint_details):
    # Email configuration
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASSWORD')
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Complaint Submission Confirmation'

    # Email body
    body = f"""Dear User,

Thank you for submitting your complaint. Your complaint has been successfully registered in our system.

Tracking ID: {tracking_id}

Complaint Details:
- Bus Number: {complaint_details['busNumber']}
- Route Number: {complaint_details['routeNumber']}
- Type: {complaint_details['complaintType']}
- Location: {complaint_details['location']}
- Date: {complaint_details['date']}

You can track the status of your complaint using the tracking ID on our website.

Best regards,
Bus Complaint Management System"""

    message.attach(MIMEText(body, 'plain'))

    # Create SMTP session
    try:
        logger.info(f"Attempting to connect to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login to the server
        logger.info(f"Attempting to login with email {sender_email}")
        server.login(sender_email, sender_password)

        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed. Please check your email and app password.")
        logger.error("Please make sure you have:\n1. Enabled 2-Step Verification in your Google Account\n2. Generated an App Password for this application\n3. Used the App Password in the .env file")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while sending email: {str(e)}")
        return False

def send_status_update_notification(recipient_email, tracking_id, new_status, remarks=''):
    # Email configuration
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASSWORD')
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Complaint Status Update'

    # Email body
    body = f"""Dear User,

This is to inform you that the status of your complaint has been updated.

Tracking ID: {tracking_id}
New Status: {new_status}

Remarks: {remarks if remarks else 'No additional remarks'}

You can track your complaint using the tracking ID on our website.

Best regards,
Bus Complaint Management System"""

    message.attach(MIMEText(body, 'plain'))

    # Create SMTP session
    try:
        logger.info(f"Attempting to connect to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login to the server
        logger.info(f"Attempting to login with email {sender_email}")
        server.login(sender_email, sender_password)

        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logger.info(f"Status update email sent successfully to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed. Please check your email and app password.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while sending email: {str(e)}")
        return False