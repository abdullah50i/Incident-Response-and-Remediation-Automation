#Task2 C2 device availability & email notification
import csv
import pexpect
import subprocess
import re
import smtplib #through 1025
from email.mime.text import MIMEText
from datetime import datetime
from task2_c3_ticket import create_tik
#looping through devices
def read_devices(filename="network_devices.csv"):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_n = row["Device Name"]
            device_ip = row["Device Address"]
            if device_ip == "None":
                continue
            if device_ip == "DHCP":
                device_ip = connect_telnet(row)
                if device_ip is None:
                    continue
            ping_devices(device_n, device_ip)

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
    telnet.sendline("ip -4 -o addr show") 
    telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
    ip_output = telnet.before #save the output 
    match = re.search(r"inet (192\.\d+\.\d+\.\d+)", ip_output) 
    telnet.close()
    if match:
        dhcp_ip = match.group(1)
        return dhcp_ip
    return None
  
#avalaibility check
def ping_devices(device_n, device_ip):
    ping_r = subprocess.run(["ping", "-c", "2", device_ip], 
                            capture_output=True 
                            )
    if ping_r.returncode == 0:
        print(f"Device {device_n} ({device_ip}) is reachable")
    else:
        print(f"Device {device_n} ({device_ip}) is unreachable")
        email(device_n, device_ip)
        create_tik(device_n, device_ip)
#assigning configs
def email(unavailable_d, unavailable_ip):
    sender_email = "network-monitor@d522.wgu.internal"
    receiver_email = "stakeholders@d522.wgu.internal"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"Network Device Unavailable: [{unavailable_d} {unavailable_ip}]"
    body = f"""Dear Network Administrator,

This is an automated notification that the following network device is currently unavailable:

Device Name: {unavailable_d}
IP Address: {unavailable_ip}
Last Checked: {current_time}

Please investigate this issue at your earliest convenience.

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