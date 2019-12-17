#! /usr/bin/env python3

import os
import sys

def error(*args, **kwargs):
    # The GitHub UI seems to order stderr badly, so just use stdout.
    print(*args, file=sys.stdout, **kwargs)
    sys.exit(1)

def getenv(var):
    rval = os.environ[var]

    if not rval:
        error(f'Error: environment variable not usable: {var}')

    return rval

def check_env(*keys):
    for k in keys:
        if k not in os.environ:
            error(f'Error: environment variable not set: {k}')

        if not os.environ[k]:
            error(f'Error: environment variable with no value: {k}')

def send_mail(subj, body):
    import smtplib
    from email.mime.text import MIMEText

    smtp_timeout = 30
    smtp_host = getenv('SMTP_HOST')
    smtp_port = getenv('SMTP_PORT')
    smtp_user = getenv('SMTP_USER')
    smtp_pass = getenv('SMTP_PASS')
    mail_from = getenv('MAIL_FROM')
    mail_to   = getenv('MAIL_TO')

    msg = MIMEText(body)
    msg['Subject'] = subj
    msg['From'] = mail_from
    msg['To'] = mail_to

    s = smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=smtp_timeout)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtp_user, smtp_pass)
    s.sendmail(mail_from, [mail_to], msg.as_string())
    s.quit()

check_env('GITHUB_EVENT_PATH',
          'CI_APP_NAME',
          'SMTP_HOST',
          'SMTP_PORT',
          'SMTP_USER',
          'SMTP_PASS',
          'MAIL_FROM',
          'MAIL_TO'
          )

ci_app_name = getenv('CI_APP_NAME')
event_payload_path = getenv('GITHUB_EVENT_PATH')
print(f'Event payload path: {event_payload_path}')

print(f'Sending email regarding {ci_app_name}...')

subject = f'Unsuccessful check suite from {ci_app_name}'
body = 'Just testing email from the GH action works'

send_mail(subject, body)
