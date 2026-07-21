#Resolution Notification Email
import smtplib #through 1025
from email.mime.text import MIMEText
#assigning configs
device_list = [{"PC2": "(192.168.20.101)", "PC3": "(192.168.20.101)", "SRV1": "(192.168.20.210)", "SRV2": "(192.168.30.210)"}]
sender_email = "network-monitor@d522.wgu.internal"
receiver_email = "stakeholders@d522.wgu.internal"
subject = "RESOLVED: DNS Service Issue and Device Compromise—All Issues Remediated"
body = f"""Dear Stakeholders,

This is an automated notification to inform you that the DNS service issue and all related device compromises have been successfully resolved. The following devices were affected and have now been remediated:

{device_list}

No further action is required at this time. If you have any questions or concerns, please contact the IT support team.

Thank you for your attention.

Best regards,  
Network Monitoring System"""
#email object and header
resolution = MIMEText(body, "plain") 
resolution["from"] = sender_email
resolution["to"] = receiver_email
resolution["subject"] = subject
with smtplib.SMTP("smtp.d522.wgu.internal", 1025) as server:
    server.send_message(resolution) #send the email to stakeholder
    print("Resolution Notification Email was Sent")