from twilio import rest


# Twilio API credentials
from core.settings import TWILIO_ACCOUNT_SID , TWILIO_AUTH_TOKEN

# Initialize Twilio client
client = rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Send a message
message = client.messages.create(
    body='Hello, this is a test message from Twilio!',
    from_='whatsapp:+919315989356',  # Your Twilio WhatsApp number
    to='whatsapp:+918960843600'  # Recipient's WhatsApp number
)

print('Message SID:', message.sid)