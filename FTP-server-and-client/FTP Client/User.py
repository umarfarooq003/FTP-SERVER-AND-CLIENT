import os
import threading
from tkinter import *
from tkinter import filedialog, messagebox
import ttkbootstrap as tkb

file_lock = threading.Lock()


class User:


    def __init__(self, root,ftp):

        self.root = root
        self.root.title("FTP Client")
        self.center_window( 1000,800)
        
        # FTP connection details
        self.ftp = ftp

        # UI setup
        self.setup_ui()
        self.populate_treeview()



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

        # File List
        file_frame = tkb.LabelFrame(self.root, text="Files on Server", padding=10)
        file_frame.pack(fill="both", padx=10, pady=5, expand=True)

        # Create a Treeview widget
        self.file_tree = tkb.Treeview(
            file_frame,
            columns=("Type", "Size"),
            show="tree headings",
            selectmode="extended",
        )
        self.file_tree.bind("<<TreeviewOpen>>", self.on_folder_open)

        self.file_tree.heading("#0", text="Name", anchor="w")
        self.file_tree.heading("Type", text="Type", anchor="w")
        self.file_tree.heading("Size", text="Size (KB)", anchor="e")

        self.file_tree.column("#0", width=600, anchor="w")  # Main tree column
        self.file_tree.column("Type", width=50, anchor="w")  # Type column
        self.file_tree.column("Size", width=100, anchor="e")  # Size column
        


        # Add vertical scrollbar
        scrollbar = tkb.Scrollbar(file_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscroll=scrollbar.set)

        # Pack Treeview and scrollbar
        self.file_tree.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")

    # Populate with server files (example placeholder)


        # Action Buttons
        action_frame = tkb.Frame(self.root)
        action_frame.pack(fill="y", padx=10, pady=20)



        self.download_button = tkb.Button(action_frame, text="Download", bootstyle="danger-outline",command=self.download_item )
        self.download_button.pack(side=LEFT, padx=10)


        self.refresh_button = tkb.Button(action_frame, text="Refresh",bootstyle="danger-outline", command=self.populate_treeview )
        self.refresh_button.pack(side=LEFT, padx=10)


        self.disconnect_button = tkb.Button(action_frame, text="Disconnect", bootstyle="danger-outline",command=self.disconnect )
        self.disconnect_button.pack(side=LEFT, padx=10)
        
        self.disconnect_button = tkb.Button(action_frame, text="Logout", bootstyle="danger-outline",command= self.logout)
        self.disconnect_button.pack(side=LEFT, padx=10)

        # Create a frame to hold the label and progress bar
        frame = tkb.Frame(self.root)
        frame.pack(pady=0)

        # Create the label
        self.updownlabel = tkb.Label(frame, text="",width=50)
        self.updownlabel.pack(padx=20, pady=0, side="bottom")  # Place it on the left

        # Create the progress bar
        self.prgresbar = tkb.Progressbar(frame,bootstyle="danger",maximum=100,mode="determinate",length=300,value=0)
        self.prgresbar.pack(padx=20, pady=10, side="bottom")  # Place it to the right of the label






    def logout(self):
        """Logout and return to the login page."""
        try:
            self.disconnect()  # Ensure the FTP connection is closed
        except Exception as e:
            print(f"Error during disconnect: {e}")

        self.root.destroy()  # Close the User window
        self.root.master.deiconify()  # Show the hidden login window







    def disconnect(self):
        """Disconnect from the FTP server."""
        try:
            if self.ftp:
                self.ftp.quit()
            messagebox.showinfo("Info", "Disconnected from the FTP server.")
            self.file_tree.delete(*self.file_tree.get_children())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")






    def populate_treeview(self):
        """Populate the Treeview with the contents of the current server directory."""
        try:
            # Clear existing entries in the tree
            self.file_tree.delete(*self.file_tree.get_children())

            # List the current working directory's contents
            items = self.ftp.mlsd()

            for name, details in items:
                item_type = details.get("type", "file")  # 'dir' or 'file'
                size = int(details.get("size", 0)) / 1024 if "size" in details else ""

                if item_type == "dir":
                    # Add folder with a placeholder for dynamic loading
                    full_path = name  # Use just the name since we are in the current directory
                    parent_node = self.file_tree.insert(
                        "", "end", text=name, values=("Folder", full_path)
                    )
                    self.file_tree.insert(parent_node, "end", text="Loading...", values=("", ""))
                else:
                    # Add files directly
                    self.file_tree.insert(
                        "", "end", text=name, values=("file", f"{size:.2f}" if size else "")
                    )
        except Exception as e:
            print(f"Error retrieving files: {e}")






    def on_folder_open(self, event):
        """Load the contents of a folder dynamically when it is expanded."""
        # Get the selected item ID and folder path
        selected_item = self.file_tree.focus()
        folder_name = self.file_tree.item(selected_item, "text")
        folder_path = self.file_tree.item(selected_item, "values")[1]  # Full path to the folder

        # Check if the folder already has loaded contents (not just 'Loading...')
        children = self.file_tree.get_children(selected_item)
        if len(children) == 1 and self.file_tree.item(children[0], "text") == "Loading...":
            self.file_tree.delete(children[0])  # Remove the placeholder

            try:
                # List the folder's contents using the full path
                items = self.ftp.mlsd(folder_path)  # Explicitly specify the full path
                for name, details in items:
                    item_type = details.get("type", "file")
                    size = int(details.get("size", 0)) / 1024 if "size" in details else ""

                    # Add folders and files to the tree
                    if item_type == "dir":
                        sub_path = f"{folder_path}/{name}"  # Construct full path for subfolder
                        sub_node = self.file_tree.insert(
                            selected_item, "end", text=name, values=("dir", sub_path)
                        )
                        self.file_tree.insert(sub_node, "end", text="Loading...", values=("", ""))
                    else:
                        self.file_tree.insert(
                            selected_item, "end", text=name, values=("file", f"{size:.2f}" if size else "")
                        )
            except Exception as e:
                print(f"Error loading folder contents: {e}")







    def downloadfile_thread(self, file_name, download_dir):    
        def download_file():
            """Download a single file from the FTP server."""
            try:
                self.ftp.voidcmd("TYPE I")
                # Destination path on the local machine
                local_path = os.path.join(download_dir, file_name)
                
                # Get the file size from the server
                file_size = self.ftp.size(file_name)

                # Configure progress bar
                self.prgresbar["maximum"] = file_size
                self.prgresbar["value"] = 0
                self.updownlabel.config(text=f"Downloading: {file_name}")

                def callback(data):
                    """Write data to file and update the progress bar."""
                    if not data:
                        return  # Prevent handling empty data packets
                    local_file.write(data)
                    self.prgresbar["value"] += len(data)
                    self.root.update_idletasks()


                # Open a local file for writing in binary mode
                with open(local_path, "wb") as local_file:
                    with file_lock:
                        self.ftp.retrbinary(f"RETR {file_name}", callback=callback, blocksize=8192) 
                        
                self.updownlabel.config(text=f"Download Complete: {file_name}")
                self.prgresbar["value"] = 0  # Reset progress bar
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download '{file_name}': {e}")
                
        server_thread = threading.Thread(target=download_file, daemon=True)
        server_thread.start()
        print("FTP server thread started.")
        
        
    def download_folder_thread(self, folder_name, download_dir):
        def download_folder():
            try:
                # Create the local folder path
                local_folder_path = os.path.join(download_dir, folder_name)
                os.makedirs(local_folder_path, exist_ok=True)

                # Navigate into the folder on the server
                print(f"Changing to folder: {folder_name}")
                self.ftp.cwd(folder_name)

                # List the folder contents on the server
                items = list(self.ftp.mlsd())
                total_items = len(items)
                current_item = 0

                for name, details in items:
                    item_type = details.get("type", "file").lower()

                    # Update progress bar
                    self.prgresbar["maximum"] = total_items
                    self.prgresbar["value"] = current_item
                    self.updownlabel.config(text=f"Downloading: {name} ({current_item + 1}/{total_items})")
                    self.root.update_idletasks()

                    if item_type in ["dir", "folder"]:
                        # Recursively download the folder
                        print(f"Found folder: {name}")
                        self.download_folder_thread(self, name, local_folder_path)
                    else:
                        # Download the file
                        print(f"Downloading file: {name}")
                        local_file_path = os.path.join(local_folder_path, name)

                        with open(local_file_path, "wb") as local_file:
                            def callback(data):
                                """Write data to file and update the progress bar."""
                                local_file.write(data)
                                self.root.update_idletasks()

                            self.ftp.retrbinary(f"RETR {name}", callback=callback)

                    current_item += 1

                # Return to the parent directory on the server
                print(f"Returning to parent directory from {folder_name}")
                self.ftp.cwd("..")
                self.updownlabel.config(text=f"Download Complete: {folder_name}")
                self.prgresbar["value"] = 0  # Reset progress bar

            except Exception as e:
                messagebox.showerror("Error", f"Failed to download folder '{folder_name}': {e}")

        # Start the download process in a separate thread
        threading.Thread(target=download_folder, daemon=True).start()








    def download_item(self):
        """Download the selected item (file or folder) from the FTP server."""
        # Get the selected item from the Treeview
        selected_item = self.file_tree.focus()
        if not selected_item:
            return

        item_name = self.file_tree.item(selected_item, "text")  # Get the item's name
        item_type = self.file_tree.item(selected_item, "values")[0]  # 'file' or 'dir'

        # Ask the user to select a local download directory
        download_dir = filedialog.askdirectory(title="Select Download Directory")
        if not download_dir:
            return

        try:
            if item_type == "file":
                # Download a single file
                
                self.downloadfile_thread(item_name, download_dir)
            elif item_type == "Folder":
                # Download a folder recursively
                self.download_folder_thread(item_name, download_dir)
            else:
                print("Unknown item type.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download '{item_name}': {e}")






if __name__ == "__main__":
    root = tkb.Window(themename="superhero")
    
    # Assuming ftp is initialized somewhere
    ftp = "your_ftp_connection_or_data_here"
    
    app = User(root, ftp)
    root.mainloop()
