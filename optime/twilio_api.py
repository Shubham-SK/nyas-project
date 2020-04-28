import twilio
from twilio.rest import Client
from instance import config

# Your Account SID from twilio.com/console
account_sid = config.TWILIO_SID
# Your Auth Token from twilio.com/console
auth_token  = config.TWILIO_AUTH_TOKEN

client = Client(account_sid, auth_token)

message = client.messages.create(

    to="+14089967710",
    from_="+16098628484",
    body="Hello from Python!")

print(message.sid)
