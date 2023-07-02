import datetime
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email_id = "modi.anurag1992@gmail.com"
sender_email_pwd = ""
recipients_email_id: list[str] = [
    "modi.anurag1992@gmail.com",
]
date: str = datetime.datetime.now().strftime("%d-%m-%Y")
subject: str = f"picks_of_the_day :- {date}"
message = "Analyze_before_investing"
attachment_path = "stocks_analyze.txt"


def sendEmail(
    sender_email_id, pwd, recipsEmailID, subject, message, attachment_path
) -> None:
    msg = MIMEMultipart()
    msg["From"] = sender_email_id
    recips: list = recipsEmailID
    msg["To"] = ",".join(recips)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    # open the file to be sent
    filename: str = os.path.basename(attachment_path)
    attachment = open(attachment_path, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.starttls()
    s.login(sender_email_id, pwd)
    s.sendmail(sender_email_id, recips, msg.as_string())
    s.quit()


sendEmail(
    sender_email_id,
    sender_email_pwd,
    recipients_email_id,
    subject,
    message,
    attachment_path,
)
