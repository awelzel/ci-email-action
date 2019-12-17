# ci-email-action
GitHub action to send email via SMTP on CI check_suite failure

Example workflow:

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
          SMTP_HOST: ${{ secrets.MAIL_HOST }}
          SMTP_PORT: ${{ secrets.MAIL_PORT }}
          SMTP_USER: ${{ secrets.MAIL_USER }}
          SMTP_PASS: ${{ secrets.MAIL_PASS }}
          MAIL_FROM: ${{ secrets.MAIL_FROM }}
          MAIL_TO: ${{ secrets.MAIL_TO }}
```

TODO: maintain this repo in zeek org?
TODO: publish this action?
