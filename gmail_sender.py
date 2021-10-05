import smtplib

def send_email(to, msg):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("gmail.username@gmail.com", "password")
    server.sendmail("gmail.username@gmail.com", to, msg)
    server.quit()

# send_email("gmail.username@gmail.com", "hi")