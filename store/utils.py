import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
import time
import datetime
from backend import settings
import os

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
        with the following certificate, please find the <a href="http://mycertificatesgymkhana.iiitvadodara.ac.in/certificate/""" + params['id'] + """">link</a> to download the certificate with this mail. This link can be given to
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


def id_generate(dataset, count, year, event_name):
    emails = dataset['Email']
    dataset = dataset.drop('Email', axis = 1)
    details = dataset.iloc[:,1:].values
    cert_id = []
    filenames = []
    i = count
    today = datetime.date.today().strftime('%d-%m-%Y')
    date = []
    counts = []
    for detail in details:

        detail[0]=str(detail[0])
        x = f"IIITV/STUD-GYMKHANA/CERT/{year}/{i:06}"
        fname = f"IIITV-STUD-GYMKHANA-CERT-{year}-{i}.pdf"
        i+=1
        filenames.append(fname)
        cert_id.append(x)
        date.append(today)
        counts.append(i-1)

    dataset['Certificate ID']=cert_id
    dataset['Date'] = date
    rollno = dataset['RollNo']
    dataset = dataset.drop('RollNo', axis = 1)


    dataset['RollNo']=rollno
    dataset['Filename']=filenames
    dataset['Email'] = emails
    dataset['Number']=counts
    media_path = os.path.join(settings.MEDIA_ROOT, f'csv/{event_name}_{year}.csv')
    dataset.to_csv(os.path.join(settings.MEDIA_ROOT, f'csv/{event_name}_{year}.csv'),index=False)

    return dataset
