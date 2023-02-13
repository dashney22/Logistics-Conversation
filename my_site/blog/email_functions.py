from django.core import mail 
from django.conf import settings
import os
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from django.utils.html import strip_tags



def query_notification(request,email,name,phone,subject,body):
	subject = name +" : "+ subject
	message = body
	message = message +"\n\n From: \n {}".format(email)
	email_from = settings.EMAIL_PBS_RECEIVER
	recipient_list = [settings.EMAIL_PBS_RECEIVER,email]
	with mail.get_connection() as connection:
		email = mail.EmailMessage(subject=subject,body=message,from_email=email_from,to=recipient_list,connection=connection)
		email.send()
	# send_mail( subject, message, email_from, recipient_list )
	return 
