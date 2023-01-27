import contextlib
import io
import os
import unittest
import unittest.mock

import process

TEST_ENVIRON = {
    "GITHUB_EVENT_PATH": "/dev/null",
    "GITHUB_TOKEN": "TOOOKEN",
    "CI_APP_NAME": "Cirrus CI",
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "25",
    "SMTP_USER": "unittest",
    "SMTP_PASS": "test",
    "MAIL_FROM": "from@localhost",
    "MAIL_TO": "to@localhost",
}


@unittest.mock.patch.dict(os.environ, TEST_ENVIRON)
@unittest.mock.patch("smtplib.SMTP")
@unittest.mock.patch("requests.get")
class Test(unittest.TestCase):

    def setUp(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def data(self, fn):
        return os.path.join("test_data", fn)

    def test_normal_pr(self, api_mock, smtp_mock):
        os.environ["GITHUB_EVENT_PATH"] = self.data("normal_pr.json")

        with contextlib.redirect_stdout(self.stdout):
            with self.assertRaises(SystemExit) as exit_exc:
                process.main()

        self.assertEqual(
            "Skip processing check_suite triggered via Pull Request\n",
            self.stdout.getvalue(),
        )
        self.assertEqual(0, exit_exc.exception.code)
        smtp_mock.assert_not_called()

    def test_pr_merged(self, api_mock, smtp_mock):
        os.environ["GITHUB_EVENT_PATH"] = self.data("merged_pr.json")
        os.environ["SKIP_CONCLUSIONS"] = "none"

        with contextlib.redirect_stdout(self.stdout):
            process.main()

        api_mock.assert_called_with(
            "https://api.github.com/repos/awelzel/zeek-ci/check-suites/10621428778/check-runs",
            headers=unittest.mock.ANY,
        )

        self.assertEqual(
            'Sending email for success check_suite "Cirrus CI"...\n',
            self.stdout.getvalue(),
        )
        smtp_mock.assert_called_with(host="localhost", port="25", timeout=30)
        smtp_mock.return_value.ehlo.assert_called()
        smtp_mock.return_value.sendmail(
            "from@localhost", ["to@localhost"], unittest.mock.ANY
        )

    def test_pr_other_repo(self, api_mock, smtp_mock):
        os.environ["GITHUB_EVENT_PATH"] = self.data("pr_in_other_repo.json")
        with contextlib.redirect_stdout(self.stdout):
            process.main()

        self.assertEqual(
            'Sending email for failure check_suite "Cirrus CI"...\n',
            self.stdout.getvalue(),
        )
        smtp_mock.assert_called_with(host="localhost", port="25", timeout=30)
        smtp_mock.return_value.ehlo.assert_called()
        smtp_mock.return_value.sendmail(
            "from@localhost", ["to@localhost"], unittest.mock.ANY
        )
