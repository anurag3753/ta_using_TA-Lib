import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders

sender_email_id = "modi.anurag1992@gmail.com"
sender_email_pwd = "Sainik@3755"
recipients_email_id = [
    "modi.anurag1992@gmail.com",
    "poojamangal.imtn@gmail.com",
    "agrawaldrnitin@gmail.com",
]
date    = datetime.datetime.now().strftime("%d-%m-%Y")
subject = f"picks_of_the_day :- {date}"
message = "Analyze_before_investing"
attachment_path = "stocks_analyze.txt"

def sendEmail(sender_email_id, pwd, recipsEmailID, subject, message, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email_id
    recips = recipsEmailID
    msg['To'] = ",".join(recips)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, 'plain'))
    # open the file to be sent
    filename = os.path.basename(attachment_path)
    attachment = open(attachment_path, "rb") 
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(sender_email_id, pwd) 
    s.sendmail(sender_email_id, recips, msg.as_string())
    s.quit()

sendEmail(sender_email_id, sender_email_pwd, recipients_email_id, subject, message, attachment_path)
