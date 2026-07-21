#Detect and Correct Altered DNS Settings
import csv
import pexpect
import re
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
#looping through devices
def read_devices(filename="network_devices.csv"):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_n = row["Device Name"]
            device_ip = row["Device Address"]
            if device_ip == "None" or device_n in ["ROUTER1", "SMTP", "DNS1", "DNS2"]:
                continue
            telnet = connect_telnet(row)
            if device_ip == "DHCP":
                device_ip = get_dhcp_ip(telnet)
                if device_ip is None:
                    telnet.close()
                    continue
            dns_parser = check_dns(telnet, row)
            exp_dns = ["10.10.10.10", "10.10.10.20"]
            rogue = [dns_ip for dns_ip in dns_parser 
                     if dns_ip not in exp_dns
            ]
            if set(dns_parser) != set(exp_dns):
                print(f"DNS configuration on {device_n} ({device_ip}) is altered!!!")
                tik_id = create_tik(device_n, device_ip)
                email(device_n, device_ip, rogue, exp_dns)
                update_dns(telnet, row, device_ip, tik_id)
            else:
                print(f"{device_n} has the expected DNS configs")  
            telnet.close()
#get the ip for dhcp devices
def connect_telnet(device):
    telnet = pexpect.spawn(f"telnet 127.0.0.1 {device['Access Port']}", timeout=10, encoding="utf-8")  
    telnet.sendline("") #press an enter
    prompt = telnet.expect(["login", r"\$"]) 
    if prompt == 0:
        telnet.sendline(device["Username"])
        telnet.expect("Password")
        telnet.sendline(device["Password"]) 
        telnet.expect(r"\$")
    return telnet
#getting the dhcp_ip
def get_dhcp_ip(telnet):
    telnet.sendline("ip -4 -o addr show") 
    telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
    ip_output = telnet.before 
    match = re.search(r"inet (192\.\d+\.\d+\.\d+)", ip_output) 
    if match:
        return match.group(1)
    return None
#DNS checking
def check_dns(telnet, device):
    print(f"Checking the DNS service for {device['Device Name']} ...")
    telnet.sendline("resolvectl dns") 
    telnet.expect((r"[\w.-]+@[\w.-]+:[^$#]*[$#]"))
    dns_output = telnet.before
    if "Failed to get global data" in dns_output: 
        telnet.sendline("cat /etc/resolv.conf")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        dns_output = telnet.before
    dns_parser =re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", dns_output) 
    dns_parser = [dns_ip for dns_ip in dns_parser if dns_ip != "127.0.0.1"]
    return dns_parser
#auto ticket creating for altered dns config
def create_tik(device_n, device_ip):
    helpdesk_url = f"http://helpdesk.d522.wgu.internal:5000/api/tickets"
    token = 'vGkbXkGLqQSo7YLflp9DutuG8st4xdPPF7wnTcwB0FE'
#building payload
    ticket = {
        "assigned_to": "IT Support",
        "description": f"Device {device_n} ({device_ip}) DNS configuration is altered",
        "priority": "high",
        "requester_email": "network-monitor@d522.wgu.internal",
        "status": "open",
        "title": f"Device {device_n} DNS configuration is altered"}
#payload
    payload = json.dumps(ticket).encode("utf-8") #convert to json text encode into bytes
    req = urllib.request.Request(helpdesk_url, data=payload, method="POST")
#sending the headers 
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    print("sending request for ticket creation")
#sending the req
    with urllib.request.urlopen(req) as response:
        print(f"POST status: {response.status}")
        response_body = response.read().decode("utf-8")
        tik_response = json.loads(response_body)
        print(response_body)
        print(f"Ticket created for {device_n}")
        return tik_response["id"]
 #remediation  
def update_dns(telnet, row, device_ip, tik_id):
        telnet.sendline("")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        telnet.sendline("sudo resolvectl dns ens3 10.10.10.10 10.10.10.20")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        telnet.sendline("sudo resolvectl flush-caches")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        print("DNS configuration for impacted device has been updated")
#verifying updates
        updated_dns = check_dns(telnet, row)
        print(f"Updated DNS {updated_dns}")
        update_tik(row["Device Name"], device_ip, tik_id)
#update ticket
def update_tik(device_n, device_ip, tik_id):
    helpdesk_url = f"http://helpdesk.d522.wgu.internal:5000/api/tickets/{tik_id}"
    token = 'vGkbXkGLqQSo7YLflp9DutuG8st4xdPPF7wnTcwB0FE'
#building payload
    ticket = {
        "assigned_to": "IT Support",
        "description": f"Device {device_n} ({device_ip}) DNS configs is updated",
        "priority": "high",
        "requester_email": "network-monitor@d522.wgu.internal",
        "status": "resolved",
        "title": f"Device {device_n} DNS configuration is updated",
    }
#payload
    payload = json.dumps(ticket).encode("utf-8") #convert to json text encode into bytes
    req = urllib.request.Request(helpdesk_url, data=payload, method="PATCH")
#sending the headers 
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    print("sending request")
#sending the req
    with urllib.request.urlopen(req) as response:
        print(f"PATCH status: {response.status}")
        response_body = response.read().decode("utf-8")
        print(response_body)
        print(f"Ticket UPDATED for {device_n}")
#assigning configs
def email(device_n, device_ip, rogue, exp_dns):
    sender_email = "network-monitor@d522.wgu.internal"
    receiver_email = "stakeholders@d522.wgu.internal"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"DNS Configuration Alter: [{device_n}], [{device_ip}]"
    body = f"""Dear Network Administrator,

This is an automated alert that the DNS configuration for the following device has been altered from the expected settings:

Device Name: [{device_n}]
IP Address: [{device_ip}]
Detected DNS Setting: [{rogue}]
Expected DNS Setting: [{exp_dns}]
Time Detected: [{current_time}]

The system will attempt to automatically correct this configuration.

Best regards,  
Network Monitoring System"""

#configs & send
    notfics = MIMEText(body, "plain") #specify as a plain text
    notfics["from"] = sender_email
    notfics["to"] = receiver_email
    notfics["subject"] = subject
    with smtplib.SMTP("smtp.d522.wgu.internal", 1025) as server:
        server.send_message(notfics) 
        print("Email Alert was Sent Successfully!")


read_devices()