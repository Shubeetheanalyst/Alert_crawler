import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import ast
import pandas as pd
import re
import requests

##============= Read Config File =====================#
f                                     = open(r"config.txt",'r')
last_id_                         = f.read()
dx                                 = ast.literal_eval(last_id_)
email                            = dx['email']
password                     = dx['password']
Rec_email                    = dx['Rec_email']
excel_file_path              = dx['excel_file_path']
f.close()

# Load the CSV file containing the list of URLs
df = pd.read_csv(excel_file_path)
urls = df['URLS'].tolist()


# Loop through the list of URLs and search for the company name
results = []
company_name = input('Enter the company name to search for: ')
for url in urls:
    response = requests.get(url)
    html_text = response.text
    if re.search(company_name, html_text, re.IGNORECASE):
        # Company name was found on this page
        last_modified = response.headers.get('Date', '')
        results.append({'URL': url, 'Last Modified': last_modified, 'Found': 'Yes'})
    else:
        results.append({'URL': url, 'Last Modified': '', 'Found': 'No'})
        

# Write the results to a new CSV file using pandas
df_results = pd.DataFrame(results)
df_results.to_csv('crawler_results.csv', index=False)    




# Email Setup
sender = email
recipient = Rec_email
subject = 'Web crawler results'
body = 'Please see the attached file.'

filename = 'crawler_results.csv'
attachment = open(filename, 'rb')
# Create a message object and add the email content
message = MIMEMultipart()
message['From'] = email
message['To'] = Rec_email
message['Subject'] = 'Web crawler results'
message.attach(MIMEText(body, 'plain'))


# Add the attachment to the message
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', f"attachment; filename= {filename}")
message.attach(part)


# Send the email
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = email
smtp_password = password
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender, recipient, message.as_string())
# Close the file and print confirmation
attachment.close()
print(f'Email with attachment {filename} sent successfully to {recipient}.')



