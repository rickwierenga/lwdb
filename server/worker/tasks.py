import os

import sendgrid


def send_email(to_email, subject, text):
  # little wasteful to create a new instance for each task, but there is no good way to share
  # the instance across workers. see https://github.com/rq/rq/issues/720
  if "SENDGRID_API_KEY" in os.environ:
    sg_api_key = os.environ["SENDGRID_API_KEY"]
  elif "SENDGRID_API_KEY_FILE" in os.environ:
    with open(os.environ["SENDGRID_API_KEY_FILE"], encoding="utf-8") as sgf:
      sg_api_key = sgf.read().strip()
  else:
    raise Exception("No sendgrid api key specified")
  sg = sendgrid.SendGridAPIClient(api_key=sg_api_key)

  from_email = sendgrid.helpers.mail.Email("noreply@lwdb.pylabrobot.org")
  to_email = sendgrid.helpers.mail.To(to_email)
  content = sendgrid.helpers.mail.Content("text/plain", text)
  mail = sendgrid.helpers.mail.Mail(from_email, to_email, subject, content)
  response = sg.client.mail.send.post(request_body=mail.get())

  if response.status_code not in range(200, 203):
    print("Error sending email")
    print(response.status_code)
    print(response.body)
    print(response.headers)
