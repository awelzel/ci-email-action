#! /usr/bin/env python3

import re
import os
import sys
import json
import requests

def error(*args, **kwargs):
    # The GitHub UI seems to order stderr badly, so just use stdout.
    print(*args, file=sys.stdout, **kwargs)

def fatal(*args, **kwargs):
    error(*args, **kwargs)
    sys.exit(1)

def optenv(var):
    if var in os.environ:
        return os.environ[var]

    return ''

def getenv(var):
    rval = os.environ[var]

    if not rval:
        fatal(f'Error: environment variable not usable: {var}')

    return rval

def check_env(*keys):
    err = False

    for k in keys:
        if k not in os.environ:
            err = True
            error(f'Error: environment variable not set: {k}')
            continue

        if not os.environ[k]:
            err = True
            error(f'Error: environment variable with no value: {k}')

        # print(f'Found usable environment variable: {k}')

    if err:
        fatal(f'Error: required environment variables are not available')

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
    mail_reply_to = optenv('MAIL_REPLY_TO')

    msg = MIMEText(body)
    msg['Subject'] = subj
    msg['From'] = mail_from
    msg['To'] = mail_to

    if mail_reply_to:
        msg['Reply-To'] = mail_reply_to

    s = smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=smtp_timeout)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtp_user, smtp_pass)
    s.sendmail(mail_from, [mail_to], msg.as_string())
    s.quit()

def skip(msg):
    print(msg)
    sys.exit(0)

def api_request(request_url):
    token = getenv('GITHUB_TOKEN')
    # TODO: remove "preview" header once API is stable
    accept_header = 'application/vnd.github.antiope-preview+json'
    authorization_header = f'Bearer {token}'
    headers = {'Authorization': authorization_header, 'Accept': accept_header}
    response = requests.get(request_url, headers=headers)
    return response

check_env('GITHUB_EVENT_PATH',
          'GITHUB_TOKEN',
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

with open(event_payload_path) as epp:
    payload = json.load(epp)

if 'check_suite' not in payload:
    skip('Skip processing non-check_suite action')

if payload['action'] != 'completed':
    skip(f"Skip processing check_suite action type: {payload['action']}")

check_suite = payload['check_suite']
repo = payload['repository']
app = check_suite['app']

if app['name'] != ci_app_name:
    skip(f"Skip processing check_suite for app: {app['name']}")

pull_requests = check_suite['pull_requests']

if pull_requests:
    skip('Skip processing check_suite triggered via Pull Request')

# Docs at https://developer.github.com/v3/checks/suites/ seem to indicate
# that 'pull_requests' will also be empty for checks that run on PRs coming
# from forked repos.  But in that case, 'head_branch' is null.
if not check_suite['head_branch']:
    skip('Skip processing check_suite triggered via Pull Request (from fork)')

# Skip conclusions that aren't interesting.
skip_conclusions_env = optenv('SKIP_CONCLUSIONS') or 'success,cancelled,neutral'
skip_conclusions = skip_conclusions_env.replace(',', ' ').split()

conclusion = check_suite['conclusion']
if conclusion in skip_conclusions:
    skip(f'Skip processing {conclusion} check_suite')

branch = check_suite['head_branch']

branch_regex = optenv('BRANCH_REGEX') or optenv('BRANCH_WHITELIST')
if branch_regex and not re.match(branch_regex, branch):
    skip(f"Skip processing branch '{branch}': does not match '{branch_regex}'")

check_runs_url = check_suite['check_runs_url']
check_runs_response = api_request(check_runs_url)
failed_check_urls = dict()

successful_checks = 0
if check_runs_response.status_code == 200:
    try:
        json = check_runs_response.json()
        runs = json['check_runs']

        for run in runs:
            if run['app']['name'] != ci_app_name:
                continue

            if run['conclusion'] == 'success':
                successful_checks += 1
                continue

            failed_check_urls[run['name']] = run['html_url']

    except:
        import traceback
        traceback.print_exc()
        print('Skip processing check_runs: failed to parse response')

print(f'Sending email for {conclusion} check_suite "{ci_app_name}"...')

repo_name = repo['name']
repo_url = repo['html_url']
sha = check_suite['head_sha']
short_sha = sha[:8]
commit_url = f'{repo_url}/commit/{sha}'
commit_msg = check_suite['head_commit']['message']

subject = f'[ci/{repo_name}] {ci_app_name}: {conclusion.capitalize()} ({branch} - {short_sha})'
body = f'''
{ci_app_name} conclusion: {conclusion}
repo: {repo_url}
branch: {branch}
commit: {commit_url}
message: {commit_msg}

successful: {successful_checks}
'''

if failed_check_urls:
    body += f'failures: {len(failed_check_urls)}\n'
    for name, url in failed_check_urls.items():
        body += f'    {name}: {url}\n'

send_mail(subject, body)
