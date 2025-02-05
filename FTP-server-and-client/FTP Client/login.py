import threading
from tkinter import *
from tkinter import  messagebox
import ttkbootstrap as tkb
from ftplib import FTP_TLS


file_lock = threading.Lock()

loged_in="admin"

class Login:


    def __init__(self, root):

        self.root = root
        self.root.title("FTP Client")
        self.center_window( 500,400)
        
        # FTP connection details
        self.ftp = None
        
        self.setup_ui()
        



    def center_window(self, width, height):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate x and y coordinates for the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Set geometry with calculated x and y
        self.root.geometry(f"{width}x{height}+{x}+{y}")





    def setup_ui(self):
        """Set up the GUI layout."""
        # Server Details
        frame = LabelFrame(self.root, text="FTP Server Details", padx=10, pady=10 )
        frame.pack(fill="y", padx=5, pady=5)


        Label(frame, text="Server:").grid(row=0, column=0, padx=5, pady=5)
        self.server_entry = Entry(frame, width=30)
        self.server_entry.insert(0, "127.0.0.1")
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)


        Label(frame, text="Port:").grid(row=1, column=0, padx=5, pady=5)
        self.port_entry = Entry(frame, width=30)
        self.port_entry.insert(0, "2121")  # Default FTP port
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)


        Label(frame, text="Username:").grid(row=2, column=0, padx=5, pady=5)
        self.username_entry = Entry(frame, width=30)
        self.username_entry.insert(0, "user") 
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)


        Label(frame, text="Password:").grid(row=3, column=0, padx=5, pady=5)
        self.password_entry = Entry(frame, width=30, show="*")
        self.password_entry.insert(0, "password")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)


        self.connect_button = tkb.Button(frame, text="Connect", bootstyle="danger-outline",command=self.connect)
        self.connect_button.grid(row=5, columnspan=4, pady=20)
        
        
        

    def open_user_form(self):
        """Open the User or Admin form window after successful connection."""
        self.root.withdraw()  # Hide the login window

        if loged_in == "user":
            from User import User
            user_window = tkb.Toplevel(self.root)  # Create a new Toplevel window
            User(user_window, self.ftp)  # Pass the new window and FTP connection

        elif loged_in == "admin":
            from Admin import Admin
            admin_window = tkb.Toplevel(self.root)  # Create a new Toplevel window
            Admin(admin_window, self.ftp)  # Pass the new window and FTP connection




    def connect(self):
        """Connect to the FTP server using TLS."""
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
        
            self.ftp = FTP_TLS()  # Use FTP_TLS for encrypted connections
            self.ftp.connect(server, port)
            self.ftp.login(username, password)
            self.ftp.prot_p()
            messagebox.showinfo("Success", "Connected to FTP server!")
            self.open_user_form()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

            

if __name__ == "__main__":

    root=tkb.Window(themename="superhero")
    app = Login(root)
    root.mainloop()
