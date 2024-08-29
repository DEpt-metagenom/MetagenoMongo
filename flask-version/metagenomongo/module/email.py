import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(file_name, remote_path):
    # Set up the MIME
    sender_email = os.getenv('SENDER_EMAIL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    try:
        recipient_email = recipient_email.split(',')
        print(recipient_email)
    except:
        print(f"An error occurred: check RECIPIENT_EMAIL is set correctly")
        return
    sender_password = os.getenv('SENDER_PASSWORD')
    message = MIMEMultipart()
    message['Subject'] = f"The file {file_name} upload"
    message['From'] = sender_email
    

    # Add body to email
    message.attach(MIMEText(f"The file {file_name} has been uploaded to the {remote_path}.", 'plain'))

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
            try:
                message['To'] = recipient
                server.sendmail(sender_email, recipient, text)
                print(f"Email sent successfully to {recipient}!")
            except Exception as e:
                print(f"An error occurred while sending the email to {recipient}: {e}")

    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

    finally:
        server.quit()
