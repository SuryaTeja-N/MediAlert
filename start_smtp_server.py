import asyncore
from smtpd import SMTPServer

class DebuggingServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print('Receiving message from:', peer)
        print('Message addressed from:', mailfrom)
        print('Message addressed to  :', rcpttos)
        print('Message length        :', len(data))
        print('Message content:')
        print(data.decode('utf-8'))
        print('-' * 50)
        return

server = DebuggingServer(('localhost', 1025), None)
print('SMTP Debugging Server running on localhost:1025')
try:
    asyncore.loop()
except KeyboardInterrupt:
    print("\nShutting down SMTP server") 