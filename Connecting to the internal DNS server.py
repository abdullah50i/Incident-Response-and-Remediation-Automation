#connect to the internal DNS server
import csv
import pexpect 
#reading through the devices list
def read_devices(filename="network_devices.csv"):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_n = row["Device Name"]
            device_ip = row["Device Address"]
            if device_n not in ["DNS1", "DNS2"]:
                continue
            telnet = connect_telnet(row)
            dns_status(telnet, device_n)
            telnet.close()
# connecting to telnet            
def connect_telnet(device): 
    telnet = pexpect.spawn(f"telnet 127.0.0.1 {device['Access Port']}", timeout=10, encoding="utf-8") #establishing the connection 
    telnet.sendline("") 
    prompt = telnet.expect(["login", r"\$"]) 
    if prompt == 0:
        telnet.sendline(device["Username"]) 
        telnet.expect("Password")
        telnet.sendline(device["Password"]) 
    return telnet
#running checking for dns status
def dns_status(telnet, device_n):
        telnet.sendline("systemctl status named --no-pager")
        telnet.expect(r"[\w.-]+@[\w.-]+:[^$#]*[$#]")
        status = telnet.before
        print(status)
read_devices()