# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 16:18:12 2018
This is the email sending class, it is called whenever a data update is made or an error occurs
@author: carrie
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError


class SendEmail:
    
    def send_email( self, subject, body_text, body_html):
        author = 'fill in'
        recipient = 'fill in'
        
        try:
            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['From'] = author
            msg['To'] = recipient    
            msg['Subject'] = subject
    
            
            # Create the body of the message (a plain-text and an HTML version).
            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(body_text, 'plain')
            part2 = MIMEText(body_html, 'html')
     
            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)
            
            # Send the message via local SMTP server.
            mail = smtplib.SMTP("smtp.outlook.office365.com", 587, timeout=20)              
            mail.starttls()
            recepients = [recipient]
                        
            mail.login(author, "")        
            mail.sendmail(author, recepients, msg.as_string())        
            mail.quit()
            
        except Exception as e:
            raise e
            
    def send_email_linux(self, subject, body_text, body_html):
        
        # This address must be verified with Amazon SES.
        SENDER = "fill in"
        RECIPIENT = "fill in"
        AWS_REGION = "fill in"
        CHARSET = "UTF-8"
        
        # Create a new SES resource and specify a region.
        client = boto3.client('ses',region_name=AWS_REGION)
        
        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': subject,
                    },
                },
                Source=SENDER
            )
            
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['ResponseMetadata']['RequestId'])
          
