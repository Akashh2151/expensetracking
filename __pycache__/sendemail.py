# from flask import render_template, request, session
# import app 
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


# def send_email(subject, recipient, message):
#     sender_email = "akashdesai2151@gmail.com"
#     sender_password = "okhnsnnviavjfsej"

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = recipient
#     msg['Subject'] = subject
#     msg.attach(MIMEText(message, 'plain'))

#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(sender_email, sender_password)
#     server.sendmail(sender_email, recipient, msg.as_string())
#     server.quit()



#  @app.route('/forgot_password', methods=['POST'])
# def forgot_password():
#     email = request.json.get('email')

#     userin_db = forgetmodel.get_user_by_email(email)
#     if not userin_db:
#         return jsonify({'error': 'user is not found in db'})
#     else:
#         otp_code = generate_numeric_otp()
#         session['otp_code'] = otp_code
#         session['email'] = email

#         otp_message = f"Your OTP for password reset is: {otp_code}"
#         send_email("Password Reset OTP", email, otp_message)

#         return render_template('otp.html', email=email)
