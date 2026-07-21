#notifying stakeholders
import smtplib #through 1025
from email.mime.text import MIMEText
#assigning configs
sender_email = "network-monitor@d522.wgu.internal"
receiver_email = "stakeholders@d522.wgu.internal"
subject = "URGENT: Device Compromise Detected—Immediate Attention Required"
body = """Dear Stakeholders,

This is an automated alert to inform you that the following device(s) have been identified as compromised during the recent network scan:

Device Name: [PC2]
IP Address: [192.168.20.101]
Last Checked: [15:30]

Device Name: [PC3]
IP Address: [192.168.30.101]
Last Checked: [15:30]

Device Name: [SRV1]
IP Address: [192.168.20.210]
Last Checked: [15:30]

Device Name: [SRV2]
IP Address: [192.168.30.210]
Last Checked: [15:30]

Immediate investigation and remediation are recommended to prevent further impact.

If you have any questions or require additional information, please contact the IT support team.

Best regards,  
Network Monitoring System"""
notfics = MIMEText(body, "plain") #specify as a plain text
notfics["from"] = sender_email
notfics["to"] = receiver_email
notfics["subject"] = subject
with smtplib.SMTP("smtp.d522.wgu.internal", 1025) as server:
    server.send_message(notfics) #send the notification to stakeholder
    print("Email Alert was Sent Successfully!")