#DNS Logging
import csv
import pexpect
import re
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
            else:
                print(f"{device_n} has the expected DNS configs")
                dns_log(device_n)
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
def dns_log(device_n):
    with open("dns_status.log", "a") as log:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{current_time} - {device_n} - DNS service functioning correctly.\n")
read_devices()