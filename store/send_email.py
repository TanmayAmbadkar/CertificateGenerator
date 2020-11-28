import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd

def send_mail(params, email, password):

    print(params['name'])
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Certificate for {params['event']} {params['year']}"
    msg['From'] = email
    msg['To'] = params['email']

    # Create the body of the message (a plain-text and an HTML version).
    html = """\
    <html lang="en">
      <body>
        <p>Dear """ + params['name'] + """,<p>
        </br>
        <p>Thank you for participating in """ + params['event'] + " " + params['year'] + """! We are very happy to award you
        with the following certificate, please find the <a href="http://cert-iiit.tk/certificate/""" +params['id'] + """">link</a> to download the certificate with this mail. This link can be given to
        any authority which they can use to verify the certificate. </p>
        <p>We hope to see you participate in other events organised by IIIT Vadodara!<p>

        <p>Thanks and Regards,</p>
        <p>PIC Student Affairs</p>
        <p>IIIT Vadodara</p>
        </br>

      </body>
    </html>

    """

    # Record the MIME types of both parts - text/plain and text/html.
    part = MIMEText(html, 'html')

    msg.attach(part)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(email, password)
    mail.sendmail(email, params['email'], msg.as_string())
    mail.quit()
