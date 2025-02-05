import os
import threading
from tkinter import *
from tkinter import filedialog, messagebox
import ttkbootstrap as tkb
from ftplib import FTP_TLS

file_lock = threading.Lock()


class Admin:


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
        """Set up the GUI layout."""

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


        self.upload_folder_button = tkb.Button(action_frame, text="Upload Foler", bootstyle="danger-outline",command=self.upload_Folder_thread)
        self.upload_folder_button.pack(side=LEFT, padx=10)

        self.upload_File_button = tkb.Button(action_frame, text="Upload File", bootstyle="danger-outline",command=self.upload_File_thread)
        self.upload_File_button.pack(side=LEFT, padx=10)


        self.download_button = tkb.Button(action_frame, text="Download", bootstyle="danger-outline",command=self.download_item)
        self.download_button.pack(side=LEFT, padx=10)


        self.refresh_button = tkb.Button(action_frame, text="Refresh",bootstyle="danger-outline", command=self.populate_treeview)
        self.refresh_button.pack(side=LEFT, padx=10)


        self.disconnect_button = tkb.Button(action_frame, text="Disconnect", bootstyle="danger-outline",command=self.disconnect)
        self.disconnect_button.pack(side=LEFT, padx=10)

        self.delete_button = tkb.Button(action_frame, text="Delete", bootstyle="danger-outline",command=self.delete_selected)
        self.delete_button.pack(side=LEFT, padx=10)
        
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
            self.upload_folder_button.config(state=NORMAL)
            self.upload_File_button.config(state=NORMAL)
            self.download_button.config(state=NORMAL)
            self.disconnect_button.config(state=NORMAL)
            self.refresh_button.config(state=NORMAL)
            self.delete_button.config(state=NORMAL)
            self.populate_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")



    def upload_File_thread(self):
        def upload_file():
            # Ask the user to select one or more files
            file_paths = filedialog.askopenfilenames(title="Select Files to Upload")
            if not file_paths:  # Exit if no file is selected
                return

            try:
                for file_path in file_paths:
                    file_name = os.path.basename(file_path)  # Extract the file name
                    with open(file_path, "rb") as file:
                        file_size = os.path.getsize(file_path)

                        # Configure progress bar
                        self.prgresbar["maximum"] = file_size
                        self.prgresbar["value"] = 0
                        self.updownlabel.config(text=f"Uploading file: {file_name}")

                        def callback(data):
                            """Update the progress bar as data is sent."""
                            self.prgresbar["value"] += len(data)
                            self.root.update_idletasks()

                        # Upload the file
                        self.ftp.storbinary(f"STOR {file_name}", file, blocksize=8000, callback=callback)
                        self.populate_treeview()  # Refresh server file list if implemented

                # Clear progress bar and label after successful upload
                self.prgresbar["value"] = 0
                self.updownlabel.config(text="Upload completed!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload: {e}")

        # Run the upload process in a separate thread
        server_thread = threading.Thread(target=upload_file, daemon=True)
        server_thread.start()
        print("FTP server thread started.")


    
    def upload_Folder_thread(self):
        def upload_folder():
            folder_path = filedialog.askdirectory(title="Select Folder to Upload")
            """Upload a folder and its contents to the current root directory on the server."""
            if not folder_path:
                self.updownlabel.config(text="No folder selected.")
                return

            base_folder_name = os.path.basename(folder_path.rstrip(os.sep))
            print(f"Uploading folder: {base_folder_name}")

            try:
                # Walk through the local folder structure
                for root, dirs, files in os.walk(folder_path):
                    # Calculate the relative path within the local folder
                    relative_path = os.path.relpath(root, folder_path)

                    # Build the server path for subdirectories or files
                    if relative_path == ".":
                        server_path = base_folder_name  # Root folder being uploaded
                    else:
                        server_path = os.path.join(base_folder_name, relative_path).replace("\\", "/")

                    # Create subdirectories on the server if necessary
                    try:
                        self.ftp.mkd(server_path)
                    except Exception:
                        pass  # Ignore if the directory already exists

                    # Upload files in the current directory
                    for file_name in files:
                        file_path = os.path.join(root, file_name)  # Full path to the local file
                        server_file_path = f"{server_path}/{file_name}".replace("\\", "/")

                        with open(file_path, "rb") as file:
                            file_size = os.path.getsize(file_path)

                            # Configure progress bar
                            self.prgresbar["maximum"] = file_size
                            self.prgresbar["value"] = 0
                            self.updownlabel.config(text=f"Uploading: {server_file_path}")

                            def callback(data):
                                """Update the progress bar as data is sent."""
                                self.prgresbar["value"] += len(data)
                                self.root.update_idletasks()

                            # Upload the file
                            self.ftp.storbinary(f"STOR {server_file_path}", file, blocksize=8000, callback=callback)

                self.updownlabel.config(text="Upload complete.")
                self.prgresbar.config(value=0)
                self.populate_treeview()


            except Exception as e:
                self.updownlabel.config(text=f"Error: {e}")
                raise Exception(f"Error uploading folder '{folder_path}': {e}")
            self.populate_treeview()

        # Run the upload in a separate thread
        server_thread = threading.Thread(target=upload_folder, daemon=True)
        server_thread.start()
        print("FTP server thread started.")






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







    # def downloadfile_thread(self, file_name, download_dir):    
    #     def download_file():
    #         """Download a single file from the FTP server."""
    #         try:
    #             self.ftp.voidcmd("TYPE I")
    #             # Destination path on the local machine
    #             local_path = os.path.join(download_dir, file_name)
                
    #             # Get the file size from the server
    #             file_size = self.ftp.size(file_name)

    #             # Configure progress bar
    #             self.prgresbar["maximum"] = file_size
    #             self.prgresbar["value"] = 0
    #             self.updownlabel.config(text=f"Downloading: {file_name}")

    #             def callback(data):
    #                 """Write data to file and update the progress bar."""
    #                 if not data:
    #                     return  # Prevent handling empty data packets
    #                 local_file.write(data)
    #                 self.prgresbar["value"] += len(data)
    #                 self.root.update_idletasks()


    #             # Open a local file for writing in binary mode
    #             with open(local_path, "wb") as local_file:
    #                 with file_lock:
    #                     self.ftp.retrbinary(f"RETR {file_name}", callback=callback, blocksize=20000) 
                        
    #             self.updownlabel.config(text=f"Download Complete: {file_name}")
    #             self.prgresbar["value"] = 0  # Reset progress bar
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to download '{file_name}': {e}")
                
    #     server_thread = threading.Thread(target=download_file, daemon=True)
    #     server_thread.start()
    #     print("FTP server thread started.")
        
        
    def downloadfile_thread(self, server_file_path, download_dir):    
        def download_file():
            """Download a single file from the FTP server given its full server path."""
            try:
                # Ensure the FTP session is in binary mode
                self.ftp.sendcmd("TYPE I")  

                # Extract the file name from the server path
                file_name = os.path.basename(server_file_path)
                
                # Destination path on the local machine
                local_path = os.path.join(download_dir, file_name)
                
                # Get the file size from the server
                file_size = self.ftp.size(server_file_path)
                
                # Configure progress bar
                self.prgresbar["maximum"] = file_size
                self.prgresbar["value"] = 0
                self.updownlabel.config(text=f"Downloading: {file_name}")

                def callback(data):
                    """Write data to file and update the progress bar."""
                    local_file.write(data)
                    self.prgresbar["value"] += len(data)
                    self.root.update_idletasks()

                # Open a local file for writing in binary mode
                with open(local_path, "wb") as local_file:
                    self.ftp.retrbinary(f"RETR {server_file_path}", callback=callback, blocksize=20000)

                self.updownlabel.config(text=f"Download Complete: {file_name}")
                self.prgresbar["value"] = 0  # Reset progress bar
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download '{server_file_path}': {e}")

        # Run the download process in a separate thread
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
            messagebox.showwarning("Warning", "No item selected for download.")
            return

        item_name = self.file_tree.item(selected_item, "text")  # Get the item's name
        item_type = self.file_tree.item(selected_item, "values")[0]  # 'file' or 'dir'

        # Ask the user to select a local download directory
        download_dir = filedialog.askdirectory(title="Select Download Directory")
        if not download_dir:
            return

        try:
            if item_type == "file":
               self.downloadfile_thread(self.find_file_path(item_name),download_dir)
            elif item_type == "Folder":
                # Download a folder recursively
                self.download_folder_thread(item_name, download_dir)
            else:
                messagebox.showerror("Error", f"Unknown item type for '{item_name}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download '{item_name}': {e}")







    def delete_selected(self):
        """Delete the selected file or folder from the FTP server."""
        # Get the selected item from the Treeview
        selected_item = self.file_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file or folder to delete.")
            return

        # Retrieve the item's details
        item_name = self.file_tree.item(selected_item, "text")
        item_type = self.file_tree.item(selected_item, "values")[0]  # Assuming 'values[0]' is type

        try:
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{item_name}'?")
            if not confirm:
                return

            if item_type == "file":
                # Find the full path of the file
                file_path = self.find_file_path(item_name)
                if file_path:
                    # Delete the file
                    self.ftp.delete(file_path)
                else:
                    messagebox.showerror("Error", f"File '{item_name}' not found on the server.")
                    return
            elif item_type == "Folder":
                # Delete the folder (and its contents recursively)
                self.delete_folder_recursively(item_name)

            # Remove the item from the Treeview
            self.file_tree.delete(selected_item)
            messagebox.showinfo("Success", f"'{item_name}' has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete '{item_name}': {e}")


    def find_file_path(self, file_name, current_path="/"):
        """
        Recursively search for a file on the FTP server and return its full path.

        :param file_name: Name of the file to find
        :param current_path: Current directory path (default is root "/")
        :return: Full path of the file if found, otherwise None
        """
        try:
            # List all items in the current directory
            items = self.ftp.nlst(current_path)

            for item in items:
                # Construct full path for the item
                full_item_path = f"{current_path}/{item}".replace("//", "/")

                try:
                    # Check if it's a folder by attempting to navigate into it
                    self.ftp.cwd(full_item_path)
                    # If successful, recursively search within the folder
                    found = self.find_file_path(file_name, full_item_path)
                    if found:
                        return found
                    # Go back to the parent directory
                    self.ftp.cwd("..")
                except Exception:
                    # If it's not a folder, check if it's the target file
                    if item == file_name:
                        return full_item_path
        except Exception as e:
            print(f"Error while searching: {e}")

        # If the file is not found in this directory
        return None




    def delete_folder_recursively(self, folder_path):
        """Recursively delete a folder and its contents from the FTP server."""
        try:
            # List contents of the folder
            items = self.ftp.mlsd(folder_path)
            for name, details in items:
                item_type = details.get("type", "file")
                full_path = f"{folder_path}/{name}"

                if item_type == "file":
                    # Delete the file
                    self.ftp.delete(full_path)
                elif item_type == "dir":
                    # Recursively delete subfolder
                    self.delete_folder_recursively(full_path)

            # Delete the empty folder
            self.ftp.rmd(folder_path)
        except Exception as e:
            raise Exception(f"Error deleting folder '{folder_path}': {e}")














if __name__ == "__main__":

    root=tkb.Window(themename="superhero")
    app = Admin(root)
    root.mainloop()
