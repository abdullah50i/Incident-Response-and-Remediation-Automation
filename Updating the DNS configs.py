#Updating the DNS configs on the affected devices
import csv
import pexpect
#devices looping
def read_devices(filename="network_devices.csv"):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_n = row["Device Name"]
            if device_n not in ["PC2", "PC3", "SVR1", "SVR2"]:
                continue
            telnet = connect_telnet(row)
            update_dns(telnet)
            check_dns(telnet, row)
            telnet.close()
#telnet connection
def connect_telnet(device):
    telnet = pexpect.spawn(f"telnet 127.0.0.1 {device['Access Port']}", timeout=10, encoding="utf-8") #establishing the connection 
    telnet.sendline("") #press an enter
    prompt = telnet.expect(["login", r"\$"]) 
    if prompt == 0:
        telnet.sendline(device["Username"]) 
        telnet.expect("Password")
        telnet.sendline(device["Password"]) 
        telnet.expect(r"\$")
        print(f"Device {device['Device Name']} is accessed")
    return telnet  
#remediation  
def update_dns(telnet):
        telnet.sendline("")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        telnet.sendline("sudo sed -i 's/203.0.113.10/10.10.10.10/' /etc/resolv.conf")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        telnet.sendline("sudo resolvectl dns ens3 10.10.10.10 10.10.10.20")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        telnet.sendline("sudo resolvectl flush-caches")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        print("DNS configuration for impacted device has been updated")
#dns status
def check_dns(telnet, device):
        print(f"Checking the DNS service for {device['Device Name']} ...")
        telnet.sendline("resolvectl dns")
        telnet.expect((r"[\w.-]+@[\w.-]+:[^$#]*[$#]"))
        status = telnet.before
        print(status)
read_devices()
                 




