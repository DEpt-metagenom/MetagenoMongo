import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email():
    # Set up the MIME

    sender_email = os.getenv('META_EMAIL')
    recipient_email = sender_email
    sender_password = os.getenv('META_PASS')
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email

    # Add body to email
    message.attach(MIMEText("ENV variable", 'plain'))

    # Create SMTP session
    try:
        # Use Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        # Login to the server
        server.login(sender_email, sender_password)
        # Send the email
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

    finally:
        server.quit()
