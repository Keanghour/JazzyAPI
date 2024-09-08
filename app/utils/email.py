# import os
# from dotenv import load_dotenv
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Load environment variables from .env file
# load_dotenv(dotenv_path="env/.env")  # Adjust the path as needed

# def send_otp_email(to_email: str, user_full_name: str, otp_code: int, expires_in_minutes: int):
#     sender_email = os.getenv("EMAIL_ADDRESS")
#     password = os.getenv("EMAIL_PASSWORD")

#     if not sender_email or not password:
#         raise ValueError("Email address and password must be set in environment variables")

#     # Create the email content
#     otp_subject = "Your OTP Code for Verification"
#     otp_body = f"""
#     Dear {user_full_name},

#     Here is your OTP code to verify your email: {otp_code}

#     This code is valid for {expires_in_minutes} minutes.

#     If you did not request this, please ignore this email.

#     Best regards,
#     Your Company Name
#     """

#     # Set up the email message
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = to_email
#     msg['Subject'] = otp_subject

#     msg.attach(MIMEText(otp_body, 'plain'))

#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(sender_email, password)
#             server.sendmail(sender_email, to_email, msg.as_string())
#             print("OTP email sent successfully")
#     except smtplib.SMTPException as e:
#         # Use logging instead of print in production
#         print(f"SMTP error: {e}")
#         raise
#     except Exception as e:
#         # General exception handling
#         print(f"Error sending email: {e}")
#         raise
