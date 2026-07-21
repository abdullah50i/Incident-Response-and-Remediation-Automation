import csv
import subprocess
import pexpect
import re
#version 2 of b2 (final)
def ping_devices(device_ip):
    ping_r = subprocess.run(["ping", "-c", "2", device_ip], #run the ping
                            capture_output=True #clean the terminal
                            )
    return ping_r.returncode == 0 #is the ping success?
def connect_telnet(device): #function crated for telnet to back later
    telnet = pexpect.spawn(f"telnet 127.0.0.1 {device['Access Port']}", timeout=10, encoding="utf-8") #establishing the connection 
    telnet.sendline("") #press an enter
    prompt = telnet.expect(["login", r"\$"]) #if not sure whitch promt it's expecting
    if prompt == 0:
        telnet.sendline(device["Username"]) #enter the username for the devicees that get dhcp ips
        telnet.expect("Password")
        telnet.sendline(device["Password"]) # '' ''    password
        telnet.expect(r"\$")
    return telnet    
def read_devices(filename="network_devices.csv"):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_n = row["Device Name"]
            device_ip = row["Device Address"]
            if device_ip == "None":
                print(f"{device_n} {device_ip} has no IP set")
                continue
            if device_n in ["ROUTER1", "SMTP"]:
                continue
            telnet = connect_telnet(row)
            if device_ip == "DHCP":
                telnet.sendline("ip -4 -o addr show") #get the ip 
                telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
                ip_output = telnet.before #save the output 
                match = re.search(r"inet (192\.\d+\.\d+\.\d+)", ip_output) #extract the ip for the ens3 
                if match:
                    dhcp_ip = match.group(1)
                    print(f"{device_n} IP is {dhcp_ip}")
                    if ping_devices(dhcp_ip):
                        print(f"{device_n} ({dhcp_ip}) is reachable")
                    else:
                        print(f"{device_n} ({dhcp_ip}) unreachable")
            else:
                if ping_devices(device_ip):
                    print(f"{device_n} {device_ip} is reachable")
                else:
                    print(f"{device_n} ({device_ip}) is unreachable")
            telnet.sendline("resolvectl dns") #check for real DNS not the local resolver 
            telnet.expect((r"[\w.-]+@[\w.-]+:[^$#]*[$#]"))
            dns_output = telnet.before
            if "Failed to get global data" in dns_output: #for the rogue infected that resovectl will fail
                telnet.sendline("cat /etc/resolv.conf")
                telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
                dns_output = telnet.before
            dns_parser =re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", dns_output) #dns_parser is the ip cut from the dns output
            dns_parser = [dns_ip for dns_ip in dns_parser if dns_ip != "127.0.0.1"]
            if dns_parser:
                print(f"{device_n} DNS server IP is {dns_parser}")
                exp_dns = ["10.10.10.10", "10.10.10.20"]
                rogue = [dns_ip for dns_ip in dns_parser 
                         if dns_ip not in exp_dns
                    ]         
                if rogue:
                    print(f"{device_n} is impacted by the rogue DNS server: {rogue}")
                else:
                    print(f"{device_n} has the expected DNS configs")        
            else:
                print(f"")    
            telnet.sendline("exit")
read_devices()



