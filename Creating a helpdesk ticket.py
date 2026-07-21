import urllib.request
import json #to convert to json text then bytes for http 
#configurations
helpdesk_url = "http://helpdesk.d522.wgu.internal:5000/api/tickets" #the ticketing system url
token = 'vGkbXkGLqQSo7YLflp9DutuG8st4xdPPF7wnTcwB0FE'
compromised_devices = [ #to loop throu
    ("PC2", "192.168.20.101"),
    ("PC3", "192.168.30.101"),
    ("SRV1", "192.168.20.210"),
    ("SRV2", "192.168.30.210")
]
for device_n, device_ip in compromised_devices:
#building payload
    ticket = {
        "assigned_to": "IT Support",
        "description": "Rogue DNS detected on {device_n} ({device_ip})",
        "priority": "high",
        "requester_email": "network-monitor@d522.wgu.internal",
        "status": "open",
        "title": "Compromised device detected {device_n} "
    }
    payload = json.dumps(ticket).encode("utf-8") #convert to json text encode into bytes
req = urllib.request.Request(helpdesk_url, data=payload, method="POST")
#sending the headers 
req.add_header("Authorization", f"Bearer {token}")
req.add_header("content-Type", "application/json")
print("sending request")
#sending the req
with urllib.request.urlopen(req) as response:
  print(response.status)
  response = response.read().decode("utf-8")
  print("tickets created")
  