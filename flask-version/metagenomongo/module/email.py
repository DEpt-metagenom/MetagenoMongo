import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(file_name, remote_path):
    # Set up the MIME

    sender_email = os.getenv('META_EMAIL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    recipient_email = recipient_email.split(',')
    sender_password = os.getenv('META_PASS')
    message = MIMEMultipart()
    message['Subject'] = f"The file {file_name} upload"
    message['From'] = sender_email
    message['To'] = recipient_email

    # Add body to email
    message.attach(MIMEText(f"The file {file_name} has been uploaded to the {remote_path}.", 'plain', "utf-8"))

    # Create SMTP session
    try:
        # Use Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        # Login to the server
        server.login(sender_email, sender_password)
        # Send the email
        text = message.as_string()
        for recipient in recipient_email:
            server.sendmail(sender_email, recipient, text)
        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

    finally:
        server.quit()
