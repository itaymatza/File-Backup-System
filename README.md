# File-backup-system

Note: In this redme doc, we are referring to Windows environment.

Installation
------------
cryptography


SSL
---
#Normally you’d use a server certificate from a Certificate Authority such as Let’s Encrypt, and would setup your own Certificate Authority so you can sign and revoke client certificates.

For this example, we’ll create Self-signed server and client certificates - 

Install OpenSSL for certificate generating:
1) Download the latest OpenSSL windows installer file from https://slproweb.com/products/Win32OpenSSL.html.
2) Run OpenSSL Installer and install OpenSSL.
3) Open a Command Prompt (CMD) as Administrator.
4) Use the following commands to set the environment variables to function OpenSSL properly on your system:
   4.1) set OPENSSL_CONF=C:\OpenSSL-Installation-Path\bin\openssl.cfg
   4.2) set Path=%Path%;C:\OpenSSL-Installation-Path\bin

Create server certificate:


