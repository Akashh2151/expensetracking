from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.rest import Client

# Twilio Account SID and Auth Token
account_sid = 'AC721f196f11f22a010e25801b88b3b1f0'
auth_token = '5f58066f166d1178ac5d76779825e30e'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Create a MessagingResponse object to build the response message
response = MessagingResponse()

# Create buttons and attach them to a message
buttons = [
    {"type": "text", "title": "Option 1", "payload": "option1"},
    {"type": "text", "title": "Option 2", "payload": "option2"}
]

# Add buttons to the message
response.message(
    "Please select an option:",
    buttons=buttons
)

# Send the TwiML response as a WhatsApp message
twiml = str(response)
user_whatsapp_number = '+919776254722'  # Replace with the recipient's WhatsApp number

message = client.messages.create(
    body=twiml,
    from_='whatsapp:+16189360813',  # Replace with your Twilio WhatsApp number
    to='whatsapp:' + user_whatsapp_number
)

print("Message sent. SID:", message.sid)
