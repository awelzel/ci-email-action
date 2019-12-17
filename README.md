# ci-email-action
A GitHub action to send email via SMTP on CI check_suite failures.

- Passing runs also attempt to check if the last run was a failure, and if so,
  sends a "now passing" email.

- Failures triggered by Pull Requests do not send email.

- The CI App name is configurable, but have only tested with Cirrus CI.

- The SMTP / mail configuration requires use of secret variables which can be
  set within the GitHub repository settings.

Example workflow config:

```
name: CI Email Notification
on:
  check_suite:
    types: [completed]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send CI Email Notification
        uses: jsiwek/ci-email-action@master
        env:
          CI_APP_NAME: "Cirrus CI"
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          MAIL_FROM: ${{ secrets.MAIL_FROM }}
          MAIL_TO: ${{ secrets.MAIL_TO }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
