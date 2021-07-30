# File-backup-system

About
-----
Backup system..

Configuration files
-------------------
Server:
- port.info

Client:
- server.info

Requirements
------------
- Cryptography.
- SSL Certificates.

Cryptography
------------
Install using pip:

pip install cryptography

Note: If you are using pycharm, you can add the module in the follwing way -


In the project - Settings -> Project -> python Interpreter -> Add (The plus sign) -> cryptography -> Install Package -> OK.

SSL Certificates
----------------
Note: In this redme doc, we are referring to Windows environment.

Normally you’d use a server certificate from a Certificate Authority such as Let’s Encrypt, and would setup your own Certificate Authority so you can sign and revoke client certificates.

For this example, we’ll create Self-signed server and client certificates - 

Install OpenSSL for certificate generating:
1) Download the latest OpenSSL windows installer file from https://slproweb.com/products/Win32OpenSSL.html.
2) Run OpenSSL Installer and install OpenSSL.
3) Open a Command Prompt (CMD) as Administrator.
4) Use the following commands to set the environment variables to function OpenSSL properly on your system:

set OPENSSL_CONF=C:\OpenSSL-Installation-Path\bin\openssl.cfg

set Path=%Path%;C:\OpenSSL-Installation-Path\bin

From the same opened CMD:
1) Use cd command and nevigate to your certificate dirctory.
2) Create server certificate by runnig the command, and fill your server detailes. #Common Name=backupserver.com:

openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt

3) Create client certificate by runnig the command, and fill your server detailes:

openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt


