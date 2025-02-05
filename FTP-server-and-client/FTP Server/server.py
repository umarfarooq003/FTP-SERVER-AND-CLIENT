import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from tkinter import *
import mysql.connector as mysql
import ttkbootstrap as tkb
from tkinter import messagebox


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FTP_DIR = os.path.join(SCRIPT_DIR, "ftp_dir")
SSL_CERT = os.path.join(SCRIPT_DIR, "server.crt")
SSL_KEY = os.path.join(SCRIPT_DIR, "server.key")
global server


class FTPServerGUI:
    Serveron = 0
    
    def center_window(self, width, height):
        """Center the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        self.root.geometry(f'{width}x{height}+{position_right}+{position_top}')

    def setup_ui(self):
        """Set up the user interface."""
        # Server status label
        self.mylabel = tkb.Label(
            text="Server is off", font=("Comic Sans MS", 28), bootstyle="default"
        )
        self.mylabel.pack(pady=50)

        # Action frame for the server toggle button
        action_frame = tkb.Frame(self.root)
        action_frame.pack(fill="y", padx=10, pady=20)

        # Toggle server button
        self.refresh_button = tkb.Button(
            action_frame,
            text="CLICK ME TO SWITCH ON SERVER",
            bootstyle="danger-outline",
            width=30,  # Adjusted width to make the button longer
            command=self.switchon,  # Placeholder function
        )
        self.refresh_button.pack(pady=10)

        # User management section
        user_frame = tkb.LabelFrame(self.root, text="User Management", padding=10)
        user_frame.pack(fill="both", expand=True,  padx=10, pady=20)  # Allow expansion and better use of space

        # Column headers for username and password
        tkb.Label(user_frame, text="Username", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)
        tkb.Label(user_frame, text="Password", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=5)

        # Input fields for username and password
        self.username_entry = tkb.Entry(user_frame, width=25)
        self.username_entry.grid(row=1, column=0, padx=10, pady=5)

        self.password_entry = tkb.Entry(user_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Add radio buttons for selecting role
        self.role_var = StringVar(value="User")  # Default to 'User'
        self.admin_radio = tkb.Radiobutton(user_frame, text="Admin", variable=self.role_var, value="Admin", bootstyle="primary")
        self.admin_radio.grid(row=2, column=0, padx=10, pady=5)

        self.user_radio = tkb.Radiobutton(user_frame, text="User", variable=self.role_var, value="User", bootstyle="secondary")
        self.user_radio.grid(row=2, column=1, padx=10, pady=5)   # Aligns to the left

        # Create user button
        self.create_user_button = tkb.Button(
            user_frame,
            text="Create User",
            bootstyle="success-outline",
            command=self.create_user,  # Placeholder function
        )
        self.create_user_button.grid(row=1, column=2, padx=10, pady=5)

        # Listbox to display existing users
        self.user_list = Listbox(user_frame, height=10, width=50)  # Increased height for more space
        self.user_list.grid(row=3, column=0, columnspan=3, pady=10)

        # Load users from DB into Listbox
        self.load_users_from_db()

        # Bind the listbox selection to load user data into entry fields
        self.user_list.bind("<ButtonRelease-1>", self.on_user_select)

        # Delete user button
        self.delete_user_button = tkb.Button(
            user_frame,
            text="Delete Selected User",
            bootstyle="danger-outline",
            command=self.delete_user,  # Placeholder function
        )
        self.delete_user_button.grid(row=4, column=0, columnspan=3, pady=10)

        # Configure grid expansion in the user frame
        user_frame.grid_rowconfigure(0, weight=0)
        user_frame.grid_rowconfigure(1, weight=1)  # Make the row containing the entry fields expandable
        user_frame.grid_rowconfigure(2, weight=0)
        user_frame.grid_rowconfigure(3, weight=3)  # Give more space to the Listbox
        user_frame.grid_columnconfigure(0, weight=1)  # Make the columns flexible
        user_frame.grid_columnconfigure(1, weight=1)
        user_frame.grid_columnconfigure(2, weight=0)

    def __init__(self, root):
        self.root = root
        self.root.title("FTP Server")
        self.center_window(1000, 800)

        # UI Setup
        self.setup_ui()


    def switchon(self):
        """Simulates toggling the server on or off."""
        if self.mylabel.cget("text") == "Server is off":
            # Update the label and button to reflect the server being
            self.mylabel.config(text="Server is running", bootstyle="success")
            self.refresh_button.config(
                text="CLICK ME TO SWITCH OFF SERVER", bootstyle="danger-outline"
            )
            start_ftp_server()
            print("Server is now ON.")
        else:
            # Update the label and button to reflect the server being off
            self.mylabel.config(text="Server is off", bootstyle="default")
            self.refresh_button.config(
                text="CLICK ME TO SWITCH ON SERVER", bootstyle="success-outline"
            )
            stop_ftp_server()
            print("Server is now OFF.")

    def load_users_from_db(self):
        """Load users from the database and display them in the Listbox.""" 
        con = mysql.connect(host="localhost", user="root", password="", database="ftp")
        cursor = con.cursor()
        cursor.execute("SELECT Username, Password, Role FROM Data")  # Query to fetch users and roles
        users = cursor.fetchall()  # Fetch all the results
        con.close()

        # Clear existing listbox content
        self.user_list.delete(0, tkb.END)

        # Insert the users from the database into the listbox
        for user in users:
            self.user_list.insert(tkb.END, f"{user[0]}: {user[1]} (Role: {user[2]})")
    def create_user(self):
        name = self.username_entry.get()
        key = self.password_entry.get()
        role = self.role_var.get()
        if name == "" or key == "":
             messagebox.showwarning("Input Error", "Please fill in both fields.")
        elif len(key) < 8:
            messagebox.showwarning("Input Error", "Password should be atleast 8 charachters.")
        else:
            # Assign role based on radio button selection
            access_level = "elradfmw" if role == "Admin" else "rl"
            
            # Insert user and their role into the database
            con = mysql.connect(host="localhost", user="root", password="", database="ftp")
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO Data (Username, Password, Role) VALUES (%s, %s, %s)", 
                (name, key, access_level)
            )
            cursor.execute("commit")
            messagebox.showinfo("Success", "User Created Successfully")
            self.username_entry.delete(0, tkb.END)
            self.password_entry.delete(0, tkb.END)
            con.close()
            self.load_users_from_db()

    def delete_user(self):
        """Delete the selected user from the Listbox."""  # Added confirmation prompt to be triggered by button press
        selected_index = self.user_list.curselection()  # Get the index of the selected item
        if selected_index:
            selected_user = self.user_list.get(selected_index)
            username = selected_user.split(":")[0]  # Extract the username part
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user '{username}'?")
            if confirm:
                # Remove user from the database
                con = mysql.connect(host="localhost", user="root", password="", database="ftp")
                cursor = con.cursor()
                cursor.execute("DELETE FROM Data WHERE Username = %s", (username,))
                con.commit()  # Commit the transaction
                con.close()

                # Reload the user list from the database after deletion
                self.load_users_from_db()
    def on_user_select(self, event):
        """When a user is selected in the Listbox, display their details in the entry fields."""
        selected_index = self.user_list.curselection()  # Get the index of the selected item
        if selected_index:
            selected_user = self.user_list.get(selected_index)
            username, password = selected_user.split(":")  # Split the username and password
            self.username_entry.delete(0, tkb.END)  # Clear the username field
            self.username_entry.insert(0, username)  # Insert the selected username
            self.password_entry.delete(0, tkb.END)  # Clear the password field
            self.password_entry.insert(0, password)

def start_ftp_server():
    def run_server():
        global server
        # Step 1: Set up user authorization
        authorizer = DummyAuthorizer()

        # Getting users from database
        con = mysql.connect(host="localhost", user="root", password="", database="ftp")
        cursor = con.cursor()
        cursor.execute("SELECT Username, Password, Role FROM Data")  # Query to fetch users
        users = cursor.fetchall()  # Fetch all the results
        con.close()

        # Adding user with permissions
        for user in users:
            username, password, role = user
            authorizer.add_user(username, password, FTP_DIR, perm=role)
 
        # Step 2: Set up FTP handler with SSL
        handler = TLS_FTPHandler
        handler.certfile = SSL_CERT  # Path to SSL certificate
        handler.keyfile = SSL_KEY    # Path to SSL private key
        handler.authorizer = authorizer
        handler.tls_control_required = True  # Require TLS for control channel
        handler.tls_data_required = True     # Require TLS for data channel

        # Step 3: Configure server
        server = FTPServer(("0.0.0.0", 21), handler)
        print("FTP server is running on port 21 with SSL/TLS...")

        # Step 4: Start the server
        server.serve_forever()

    # Run the FTP server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("FTP server thread started.")

def stop_ftp_server():
    global server
    if server:
        print("Shutting down the FTP server...")
        server.close_all()
        server = None
        print("FTP server has been stopped.")


if __name__ == "__main__":

    # Create a directory to serve files if it doesn't exist
    if not os.path.exists(FTP_DIR):
        os.makedirs(FTP_DIR)
        print(f"Created directory: {FTP_DIR}")

    # Ensure SSL certificate and key exist
    if not os.path.exists(SSL_CERT) or not os.path.exists(SSL_KEY):
        print("Error: SSL certificate or key file not found.")
        print("Generate them using the following command:")
        print("  openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes")
        exit(1)

    root = tkb.Window(themename="vapor")
    app = FTPServerGUI(root)
    root.mainloop()
