import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_digest(to_email: str, digest_text: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "GitHub Daily Digest"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 30px;">
        <div style="max-width: 650px; margin: auto; background-color: #161b22; border-radius: 12px; padding: 30px; border: 1px solid #30363d;">
            
            <h1 style="color: #58a6ff; font-size: 24px; margin-bottom: 5px;">GitHub Daily Digest</h1>
            <p style="color: #8b949e; font-size: 13px; margin-top: 0;">Last 24 hours of activity</p>
            <hr style="border: 1px solid #30363d; margin: 20px 0;">

            <div style="white-space: pre-wrap; font-size: 15px; line-height: 1.7; color: #c9d1d9;">
                {digest_text.replace(chr(10), '<br>')}
            </div>

            <hr style="border: 1px solid #30363d; margin: 20px 0;">
            <p style="color: #8b949e; font-size: 12px; text-align: center;">
                Sent by <strong style="color: #58a6ff;">GitHub Digest Agent</strong> • Munaf Studios
            </p>

        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"Digest sent to {to_email}")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")


if __name__ == "__main__":
    test_digest = """aliii-codes/groq-coding-agent
1 Commit — Add agentic loop by Ali
0 Issues
0 Pull Requests"""
    
    send_digest(GMAIL_USER, test_digest)