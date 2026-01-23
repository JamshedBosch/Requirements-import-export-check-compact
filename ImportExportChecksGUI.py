import sys
import os
from ImportExportChecks import CheckConfiguration
import webbrowser
import tempfile
import html
from quick_start_guide import show_quick_start_guide
from logger_config import logger
import json
from version import __version__, __company__, __product_name__  # Import version info

# Remove the stdout/stderr redirection
# sys.stdout = open(log_path, 'w')
# sys.stderr = sys.stdout

from ReqIF2ExelConverter import ReqIF2ExcelProcessor
from ImportExportChecks import ChecksProcessor, CheckConfiguration
from tkinter import filedialog, ttk, messagebox, PhotoImage
import tkinter as tk
from tkinter import ttk


class ImportExportGui:
    def __init__(self, master):
        logger.info("Initializing Import Export Checker GUI")
        try:
            self.master = master
            master.title("Import Export Checker")
            
            # Load recent paths for both folders and files
            self.recent_folders = self.load_recent_paths('recent_folders.json')
            self.recent_files = self.load_recent_paths('recent_files.json')
            self.max_recent = 5
            
            # Create menu bar
            self.menu_bar = tk.Menu(master)
            master.config(menu=self.menu_bar)
            
            # Create File menu
            self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="File", menu=self.file_menu)
            
            # Add Recent Folders submenu
            self.recent_folders_menu = tk.Menu(self.file_menu, tearoff=0)
            self.file_menu.add_cascade(label="Recent Folders", menu=self.recent_folders_menu)
            
            # Add Recent Files submenu
            self.recent_files_menu = tk.Menu(self.file_menu, tearoff=0)
            self.file_menu.add_cascade(label="Recent Files", menu=self.recent_files_menu)
            
            # Update both menus
            self.update_recent_menus()
            
            # Log icon loading
            icon_path = ImportExportGui.resource_path(os.path.join('icons', 'check.png'))
            logger.debug(f"Loading icon from: {icon_path}")
            img = PhotoImage(file=icon_path)
            master.iconphoto(False, img)

            # Initialize folders
            logger.info("Initializing application folders")
            self.extract_folder, self.excel_folder, _ = CheckConfiguration.initialize_folders()
            logger.debug(f"Folders initialized: extract={self.extract_folder}, excel={self.excel_folder}")

            master.geometry("600x400")  # Reduced height since we removed some widgets
            master.resizable(False, False)

            # Apply custom styles
            style = ttk.Style()
            style.theme_use('default')

            # Set custom colors
            style.configure('TLabel', background='#f0f0f0', foreground='#333333')
            style.configure('TButton', background='#007bff', foreground='#ffffff',
                            padding=8,
                            font=("Helvetica", 10), relief=tk.FLAT)
            style.map('TButton', background=[('active', '#0069d9')])
            style.configure('TRadiobutton', background='#f0f0f0',
                            foreground='#333333')
            style.configure('TEntry', fieldbackground='#ffffff',
                            foreground='#333333')
            style.configure('TFrame', background='#f0f0f0')

            # Configure custom checkbox style with no focus indicators
            style.layout('NoFocus.TCheckbutton',
                         [('Checkbutton.padding', {'children':
                                                       [('Checkbutton.indicator',
                                                         {'side': 'left',
                                                          'sticky': ''}),
                                                        ('Checkbutton.focus',
                                                         {'children':
                                                             [('Checkbutton.label',
                                                               {'sticky': 'nswe'})],
                                                             'side': 'left',
                                                             'sticky': ''})],
                                                   'sticky': 'nswe'})])

            style.configure('NoFocus.TCheckbutton',
                            background='#f0f0f0',
                            foreground='#333333',
                            focuscolor='#f0f0f0',
                            highlightthickness=0,
                            borderwidth=0)

            style.map('NoFocus.TCheckbutton',
                      background=[('active', '#f0f0f0')],
                      foreground=[('active', '#333333')],
                      focuscolor=[('active', '#f0f0f0')],
                      highlightcolor=[('focus', '#f0f0f0')],
                      relief=[('focus', 'flat')])

            # Create the Help menu
            help_menu = tk.Menu(self.menu_bar)
            self.menu_bar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="Quick Start Guide", command=show_quick_start_guide)
            help_menu.add_command(label="About", command=self.show_about_dialog)


            # Project Selection Frame
            self.project_frame = ttk.Frame(master)
            self.project_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

            # Set the label for Select Project
            ttk.Label(self.project_frame, text="Select Project:",
                      font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")

            # Create a dropdown list for project selection
            self.project_var = tk.StringVar(value="PPE/MLBW")
            self.project_dropdown = ttk.Combobox(
                self.project_frame,
                textvariable=self.project_var,
                postcommand=self.print_status,
                values=["PPE/MLBW", "SSP", "SDV01"],
                state="readonly",
                style='TCombobox'
            )
            self.project_dropdown.grid(row=0, column=1, padx=10, sticky="w")
            print(f"project selected is: {self.project_var.get()}")



            # Check Type Selection Frame
            self.check_type_frame = ttk.Frame(master)
            self.check_type_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
            self.check_type_var = tk.IntVar(value=CheckConfiguration.IMPORT_CHECK)

            # Set the label for Select type
            ttk.Label(self.check_type_frame, text="Select Check Type:",
                      font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")

            # Create Radio buttons for import and export
            ttk.Radiobutton(self.check_type_frame, text="Import",
                            variable=self.check_type_var,
                            value=CheckConfiguration.IMPORT_CHECK,
                            style='TRadiobutton').grid(row=0, column=1, padx=10,
                                                       sticky="w")
            ttk.Radiobutton(self.check_type_frame, text="Export",
                            variable=self.check_type_var,
                            value=CheckConfiguration.EXPORT_CHECK,
                            style='TRadiobutton').grid(row=0, column=2, padx=10,
                                                       sticky="w")

            # Add "Select compare file" label and checkbox
            ttk.Label(self.check_type_frame, text="Select compare file:",
                      font=("Helvetica", 12)).grid(row=1, column=0, sticky="w",
                                                   pady=(15, 5))

            # Checkbox variable and button
            self.show_path_var = tk.BooleanVar()
            self.checkbox = ttk.Checkbutton(
                self.check_type_frame,
                text="",
                variable=self.show_path_var,
                command=self.toggle_reference_path,
                style='NoFocus.TCheckbutton',
                takefocus=False  # Prevent focus from keyboard
            )
            self.checkbox.grid(row=1, column=1, sticky="w", pady=(15, 5),
                               padx=(10, 0))

            # Paths Frame
            self.path_frame = ttk.Frame(master)
            self.path_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

            # Add only ReqIF folder path entry
            self.add_path_entry(self.path_frame, "ReqIF folder:",
                                self.browse_reqif, 0)

            # Reference path entry and browse button (initially hidden)
            self.ref_path_var = tk.StringVar()
            self.ref_path_label = ttk.Label(self.path_frame, text="Compare file:",
                                            font=("Helvetica", 12))
            self.ref_path_entry = ttk.Entry(
                self.path_frame,
                textvariable=self.ref_path_var,
                width=40,
                font=("Helvetica", 10)
            )
            self.ref_browse_button = tk.Button(
                self.path_frame,
                text="Browse",
                command=self.browse_reference_path,
                font=("Helvetica", 10),
                width=10  # Match width with other browse buttons
            )

            # Buttons Frame
            self.button_frame = ttk.Frame(master)
            self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=20)

            self.convert_button = ttk.Button(self.button_frame, text="Convert",
                                             command=self.convert_files,
                                             style='TButton')
            self.convert_button.pack(side=tk.LEFT, padx=20)

            self.execute_button = ttk.Button(self.button_frame,
                                             text="Execute Checks",
                                             command=self.execute_checks,
                                             style='TButton', stat=tk.DISABLED)
            self.execute_button.pack(side=tk.LEFT, padx=20)

            # Report Type Selection Frame
            self.report_type_frame = ttk.Frame(master)
            self.report_type_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

            # Report Type Label
            ttk.Label(self.report_type_frame, text="Report Type:",
                      font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")

            # Report Type Variable
            self.report_type_var = tk.StringVar(value="HTML")  # Default: HTML

            # Excel Report Radio Button
            ttk.Radiobutton(self.report_type_frame, text="HTML",
                            variable=self.report_type_var,
                            value="HTML",
                            style='TRadiobutton').grid(row=0, column=1, padx=10,
                                                       sticky="w")

            # HTML Report Radio Button
            ttk.Radiobutton(self.report_type_frame, text="Excel",
                            variable=self.report_type_var,
                            value="Excel",
                            style='TRadiobutton').grid(row=0, column=2, padx=10,
                                                       sticky="w")

            # Status bar
            self.status_bar = ttk.Label(master, text="", relief=tk.SUNKEN,
                                        anchor=tk.W, font=("Helvetica", 10))
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        except Exception as e:
            logger.error(f"Error during GUI initialization: {str(e)}", exc_info=True)
            raise

    def resource_path(relative_path):
        """ Get the absolute path to a resource, works for development and PyInstaller bundling. """
        try:
            # PyInstaller creates a temporary folder to store the bundled resources
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def show_about_dialog(self):
        about_text = (
            f"{__product_name__}\n\n"
            f"Version: {__version__}\n"
            f"© {__company__}\n\n"
            "This tool allows users to perform Import and Export checks for ReqIF files.\n\n"
            "Features:\n"
            "- Convert ReqIF files to Excel format\n"
            "- Execute Import/Export checks\n"
            "\nInstructions for use will be added here."
        )
        messagebox.showinfo("About", about_text)

    def add_path_entry(self, parent, label_text, browse_command, row):
        """Helper function to add label, entry, and browse button."""
        label = tk.Label(parent, text=label_text, font=("Helvetica", 12))
        label.grid(row=row, column=0, sticky="w", padx=5, pady=10)

        # Hold the text entered(folder path) in the entry field.
        entry_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=entry_var, width=40,
                         font=("Helvetica", 10))
        entry.grid(row=row, column=1, padx=5, pady=10)

        browse_button = tk.Button(parent, text="Browse",
                                  command=browse_command,
                                  font=("Helvetica", 10), width=10)
        browse_button.grid(row=row, column=2, padx=5, pady=10)

        # Save reference to the entry variable
        if label_text == "ReqIF folder:":
            self.reqif_path_var = entry_var

    def browse_reqif(self):
        """Browse for ReqIF folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.reqif_path_var.set(folder)
            self.add_recent_folder(folder)

    def browse_reference_path(self):
        """Open file dialog to select reference Excel file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx;*.xls")]
        )
        if file_path:
            self.ref_path_var.set(file_path)
            self.add_recent_file(file_path)

    def operation_type(self):
        """Execute the conversion logic based on the selected radio button."""
        check_type = self.check_type_var.get()  # Get the selected radio button value
        operation_type = {CheckConfiguration.IMPORT_CHECK: "Import",
                          CheckConfiguration.EXPORT_CHECK: "Export"}

        # Ensure the check type is valid
        if check_type not in operation_type:
            self.update_status_bar(
                "No valid option selected. Please select Import or Export.")
            return
        else:
            return operation_type[check_type]

    def convert_files(self):
        """Convert files without progress bar"""
        try:
            reqif_folder = self.reqif_path_var.get()
            if not reqif_folder:
                logger.warning("No ReqIF folder selected")
                messagebox.showerror("Error", "Please select ReqIF folder")
                return

            logger.info(f"Starting conversion of files from: {reqif_folder}")
            
            # Process files
            self.processor = ReqIF2ExcelProcessor(reqif_folder, self.extract_folder, self.excel_folder)
            self.processor.process()
            
            logger.info("Conversion completed successfully")
            self.execute_button.config(state=tk.NORMAL)
            self.status_bar.config(text="Conversion completed successfully")
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
            self.status_bar.config(text="Error during conversion")

    def execute_checks(self):
        """Execute checks without progress bar"""
        try:
            project_type = self.project_var.get()
            check_type = self.check_type_var.get()
            report_type = self.report_type_var.get()
            
            logger.info(f"Executing checks for Project: {project_type}")
            logger.info(f"Check type: {check_type}")
            logger.info(f"Report type: {report_type}")

            self.update_status_bar(f"{self.operation_type()} Checks processing started...")

            reference_file = self.ref_path_var.get() if self.show_path_var.get() else None
            logger.debug(f"Reference file path: {reference_file}")

            processor = ChecksProcessor(project_type, check_type, self.excel_folder,
                                     reference_file, report_type)
            reports = processor.process_folder()
            
            logger.info(f"Processed {len(reports)} files")
            self.update_status_bar(
                f"Processed {len(reports)} files. Check reports in {CheckConfiguration.REPORT_FOLDER}")
                
        except Exception as e:
            error_msg = f"Error during check execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
            self.status_bar.config(text="Error during check execution")

    def toggle_reference_path(self):
        """Show or hide the reference path entry and browse button based on checkbox state"""
        if self.show_path_var.get():
            self.ref_path_label.grid(row=3, column=0, sticky="w", pady=10)
            self.ref_path_entry.grid(row=3, column=1, padx=5, pady=10)
            self.ref_browse_button.grid(row=3, column=2, padx=5, pady=10)
        else:
            self.ref_path_label.grid_remove()
            self.ref_path_entry.grid_remove()
            self.ref_browse_button.grid_remove()
            self.ref_path_var.set("")

    def update_status_bar(self, message):
        self.status_bar.config(text=message)

    def print_status(self):
        print(f"Status: {self.project_var.get()}")

    def load_recent_paths(self, filename):
        """Load recent paths from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_recent_paths(self, paths, filename):
        """Save recent paths to JSON file"""
        with open(filename, 'w') as f:
            json.dump(paths, f)

    def add_recent_folder(self, path):
        """Add a folder to recent folders list"""
        if path in self.recent_folders:
            self.recent_folders.remove(path)
        self.recent_folders.insert(0, path)
        self.recent_folders = self.recent_folders[:self.max_recent]
        self.save_recent_paths(self.recent_folders, 'recent_folders.json')
        self.update_recent_menus()

    def add_recent_file(self, path):
        """Add a file to recent files list"""
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:self.max_recent]
        self.save_recent_paths(self.recent_files, 'recent_files.json')
        self.update_recent_menus()

    def update_recent_menus(self):
        """Update both recent folders and files menus"""
        # Update folders menu
        self.recent_folders_menu.delete(0, tk.END)
        if not self.recent_folders:
            self.recent_folders_menu.add_command(label="No recent folders", state=tk.DISABLED)
        else:
            for path in self.recent_folders:
                self.recent_folders_menu.add_command(
                    label=path,
                    command=lambda p=path: self.use_recent_folder(p)
                )

        # Update files menu
        self.recent_files_menu.delete(0, tk.END)
        if not self.recent_files:
            self.recent_files_menu.add_command(label="No recent files", state=tk.DISABLED)
        else:
            for path in self.recent_files:
                self.recent_files_menu.add_command(
                    label=path,
                    command=lambda p=path: self.use_recent_file(p)
                )

    def use_recent_folder(self, path):
        """Use a path from the recent folders menu"""
        if os.path.exists(path):
            self.reqif_path_var.set(path)
        else:
            messagebox.showerror("Error", f"Folder not found: {path}")
            self.recent_folders.remove(path)
            self.save_recent_paths(self.recent_folders, 'recent_folders.json')
            self.update_recent_menus()

    def use_recent_file(self, path):
        """Use a path from the recent files menu"""
        if os.path.exists(path):
            # Only set the path if the compare file checkbox is enabled
            if self.show_path_var.get():
                self.ref_path_var.set(path)
            else:
                messagebox.showinfo("Info", "Please enable 'Select compare file' checkbox first to use this path")
        else:
            messagebox.showerror("Error", f"File not found: {path}")
            self.recent_files.remove(path)
            self.save_recent_paths(self.recent_files, 'recent_files.json')
            self.update_recent_menus()


def main():
    root = tk.Tk()
    app = ImportExportGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
