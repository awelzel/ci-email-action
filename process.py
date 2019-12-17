#! /usr/bin/env python3

import os
import sys

def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)

def getenv(var):
    rval = os.environ[var]

    if not rval:
        error(f'Error: environment variable not set: {var}')

    return rval

def send_mail(msg):
    import smtplib
    from email.mime.text import MIMEText

    smtp_host = getenv('SMTP_HOST')
    smtp_port = getenv('SMTP_PORT')
    smtp_user = getenv('SMTP_USER')
    smtp_pass = getenv('SMTP_PASS')
    smtp_timeout = 30

    mail_from = getenv('MAIL_FROM')
    mail_to   = getenv('MAIL_TO')

    ci_app_name = getenv('CI_APP_NAME')

    msg  = MIMEText(msg)
    msg['Subject'] = f'Unsuccessful check suite from {ci_app_name}'
    msg['From'] = mail_from
    msg['To'] = mail_to

    s = smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=smtp_timeout)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtp_user, smtp_pass)
    s.sendmail(mail_from, [mail_to], msg.as_string())
    s.quit()

print("Sending email...")
send_mail("Just testing email from the GH action works")
