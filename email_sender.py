import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import settings

port = 465
sender_email = "some email"
mail_app_password = settings.email_app_pass
subject_string = "Extracted Text From"
text_temp = "Here is a link to download a .txt file with the extraction you requested. This link expires in 7 days."


def sendEmail(receiver_email, file_link, video_title):
  message = MIMEMultipart("alternative")

  message["Subject"] = f"{subject_string} {video_title}"
  message["From"] = sender_email
  message["To"] = receiver_email

  html = f"""\
  <html>
    <body>
      <p>Hello,<br>
        Here is <a href="{file_link}">a link</a> to download a .txt file with the extraction you requested<br>
        This link expires in <b>7 days</b>.
      </p>
    </body>
  </html>
  """
  text = f"{text_temp}\n{file_link}"

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
      server.login(sender_email, mail_app_password)
      server.sendmail(
          sender_email, receiver_email, message.as_string()
    )