# File-backup-system
Client-Server program that allows clients, to register and connect to a server and supports backup, and restore encrypted files.

## Server
- The server is implemented in Python and using SSL sockets and multithreading.
- The role of the server is to manage the list of users registered for the service and allow them to send files to it for backup and retrieve these files at a later date.
- The server supports stateless protocol - will not store data between requests, each request stands on its own.
- The server supports multiple users and performs an authentication process with a hashed password for each client connection.
- The server saves the data by SQL (sqlite3) tables while protecting against SQL injection, and will maintain databases in a file named server.db:
  - Client's information will be stored in a table named clients while client's passwords will be stored encrypted by the sha256 algorithm.
  - File information will be saved in a table named files.
- The server supports on the following requests:
  - Backup file.
  - Recover file.
  - Get files list.
  - Delete file from backup.
- After success, the server returns a success status. Otherwise, returns an error status.

### Configuration files
- port.info - The server reads the port number from an info file in the same folder of the server's code files.


## Client
- The client is implemented in Python and using SSL sockets.
- The client will run from the console and receive user input to perform various actions.
- Requests the client to enter credentials to authenticate with the server.
- Allows an interface to perform operations in front of the server:
  - Backup file - Gets a file name from the client, encrypting the file using AES symmetric encryption, and sending it to the server. 
    - The files will be stored encrypted at the server and the server will not be exposed to the encrypted information.
  - Recover file - Gets a file name from the client, pulls the file from the server, decrypting the file using AES symmetric decryption, and saving it to the client's folder.
  - Get files list.
  - Delete file from backup.
- The data and files for each client are stored in separate folders.

### Configuration files
- server.info - The client reads the server IP address and port from an info file in the same folder of the client's code files.

## Requirements
- Cryptography.
- SSL Certificates.

### Cryptography
Install using pip:
pip install cryptography

Note: If you are using pycharm, you can add the module in the follwing way - 
Settings -> Project -> python Interpreter -> Add (The plus sign) -> cryptography -> Install Package -> OK.

### SSL Certificates
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


