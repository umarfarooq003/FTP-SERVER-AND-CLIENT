FTP Client and Server

This project consists of an FTP Client and FTP Server developed using Python, with a focus on secure data transfer using OpenSSL and TLS protocols. The project also includes a Graphical User Interface (GUI) built with Tkinter and ttkbootstrap for ease of use.
Features

    Secure file transfer with TLS and OpenSSL for encryption.
    GUI built with Tkinter and ttkbootstrap for an easy-to-use experience.
    File uploads/downloads with FTPLib in the client and pyftpdlib in the server.
    Direct communication between client and server, ensuring robust security and performance.

Prerequisites

Before running the project, ensure that you have the following installed:
Python Libraries

To install the necessary libraries, run the following commands:

pip install tkinter
pip install ttkbootstrap
pip install ftplib
pip install pyftpdlib

WAMP Server

For the database setup, you need WAMP Server. Follow these steps to set it up:

    Download and Install WAMP Server:
        Download WAMP Server from WAMP Server Official Website.
        Install it by following the on-screen instructions.

    Configure the Database:
        Open WAMP Server and ensure it is running (the icon in the system tray should be green).
        Click on the WAMP icon and go to phpMyAdmin (this will open in your browser).
        Create a new database by clicking on the Databases tab, entering a name (e.g., ftp_database), and clicking Create.
        Set up the necessary tables based on your project requirements (if any). You can define tables for storing file logs or metadata as needed.

Other Software Requirements

Ensure that you have OpenSSL installed for encryption. It is usually included in most systems, but if not, you can download and install it from OpenSSL Website.
Installation Steps

    Clone this repository:

git clone https://github.com/WelaMasroof/FTP-server-and-client.git
cd ftp-client-server

Install the necessary libraries:

pip install -r requirements.txt

Alternatively, install each library manually as mentioned above.

Set up WAMP Server for the database. Ensure that it is running and your database is configured properly.

Run the FTP Server:

    Navigate to the server directory and run:

    python ftp_server.py

Run the FTP Client:

    Navigate to the client directory and run:

        python ftp_client.py

        The GUI will open, and you can start transferring files securely between the server and the client.

Usage
FTP Client

    Connect to the server using the provided IP address and port.
    Upload or Download files via the graphical interface.
    Monitor transfer status and logs directly through the interface.

FTP Server

    Listen for incoming client connections.
    Handle file uploads and downloads securely.

Contribution

Feel free to fork this repository, submit issues, or make pull requests for improvements!
Acknowledgments

    Special thanks to my teacher for the guidance and support throughout the development of this project.
    Thanks to my team: Muneeb, Zain, Umar Javaid, Faaez Usmani, and Danial Shan for their collaboration and hard work.
