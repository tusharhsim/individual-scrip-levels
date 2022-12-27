import imaplib
import email
import re
import time

gmail_host= 'imap.gmail.com'

#TPIN: 151751
#credentials
accounts = {'tusharhsim@gmail.com' : 'tusharhsim'}
#{'rajkumarmahatha1412@gmail.com' : 'Rajmahatha'}#
#login
for username, password in accounts.items():
    try:
        mail = imaplib.IMAP4_SSL(gmail_host)
        mail.login(username, password)
        mail.select("INBOX")

        _, selected_mails = mail.search(None, '(FROM "edis@cdslindia.co.in")')
    #    print("no of mails from edis@cdslindia.co.in:" , len(selected_mails[0].split()))

        email_code = selected_mails[0].split()[-1]
        _, data = mail.fetch(email_code, 'RFC822')
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)
        if 'Transaction OTP' in email_message["subject"]:
            for part in email_message.walk():
                print('latest otp - ', re.findall(r'\d+', part.get_payload())[21])
    except Exception as e:
        print(e)
