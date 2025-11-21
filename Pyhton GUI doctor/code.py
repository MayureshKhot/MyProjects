import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
import sys
import subprocess # To open files

# --- Configuration ---
# Determine base path (especially for PyInstaller's temporary folder)
if getattr(sys, 'frozen', False):
    # Running as a bundled exe (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
    # Place data outside the potentially temporary _MEIPASS folder
    DATA_DIR = os.path.join(os.environ['APPDATA'], 'LocalPatientData') if os.name == 'nt' else os.path.join(os.path.expanduser("~"), '.local', 'share', 'LocalPatientData')
else:
    # Running as a script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = BASE_DIR # Store data alongside script for development

DB_NAME = "patients.db"
DOCS_FOLDER_NAME = "PatientDocuments"

# Construct full paths
DATABASE_PATH = os.path.join(DATA_DIR, DB_NAME)
DOCUMENTS_BASE_PATH = os.path.join(DATA_DIR, DOCS_FOLDER_NAME)

# --- Database Setup ---
def initialize_database():
    """Creates the database and table if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True) # Ensure data directory exists
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            contact TEXT UNIQUE,
            address TEXT,
            medical_history TEXT,
            consent_form_path TEXT,
            id_proof_path TEXT,
            report_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Document Folder Setup ---
def initialize_documents_folder():
    """Creates the documents folder if it doesn't exist."""
    os.makedirs(DOCUMENTS_BASE_PATH, exist_ok=True)

# --- Helper Function to Safely Copy Files ---
def safe_copy_file(source_path, patient_id, file_type_prefix):
    """Copies a file to the documents folder with a unique name, returns the destination path."""
    if not source_path or not os.path.exists(source_path):
        return None

    _, extension = os.path.splitext(source_path)
    # Create a more robust unique name: patientID_filetype_originalName.ext
    original_filename = os.path.basename(source_path)
    # Sanitize original filename slightly (replace spaces, etc.) - basic example
    safe_original_filename = "".join(c if c.isalnum() or c in ['.', '_'] else '_' for c in original_filename)

    destination_filename = f"{patient_id}_{file_type_prefix}_{safe_original_filename}"
    destination_path = os.path.join(DOCUMENTS_BASE_PATH, destination_filename)

    try:
        # Ensure the target directory exists (should be handled by initialize_documents_folder, but good practice)
        os.makedirs(DOCUMENTS_BASE_PATH, exist_ok=True)
        shutil.copy2(source_path, destination_path) # copy2 preserves metadata
        return destination_path
    except Exception as e:
        messagebox.showerror("File Copy Error", f"Could not copy {file_type_prefix} file: {e}")
        return None

# --- Helper Function to Safely Delete Files ---
def safe_delete_file(file_path):
    """Deletes a file if it exists."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
            # Optionally show a warning messagebox, but might be annoying if many files fail
            # messagebox.showwarning("File Deletion Warning", f"Could not delete file:\n{file_path}\nError: {e}")

# --- Main Application Class ---
class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Patient Data Management")
        self.root.geometry("950x650") # Adjusted size

        # --- Temporary storage for selected file paths before saving ---
        self.selected_consent_path = tk.StringVar()
        self.selected_id_proof_path = tk.StringVar()
        self.selected_report_path = tk.StringVar()

        # --- Database Connection ---
        # Keep connection open while app runs for simplicity, ensure it's closed on exit
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # --- Styling ---
        style = ttk.Style()
        style.theme_use('clam') # Or 'vista', 'xpnative' if available
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("Treeview.Heading", font=('Calibri', 10,'bold'))
        style.configure("Treeview", rowheight=25)

        # --- Frames ---
        input_frame = ttk.Frame(root, padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        button_frame = ttk.Frame(root, padding="10")
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        tree_frame = ttk.Frame(root, padding="10")
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        search_frame = ttk.Frame(button_frame) # Put search within button frame
        search_frame.pack(side=tk.RIGHT, padx=10)

        # Configure grid weights for resizing
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Input Fields ---
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.age_entry = ttk.Entry(input_frame, width=10)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w") # Align left

        ttk.Label(input_frame, text="Contact:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.contact_entry = ttk.Entry(input_frame, width=40)
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.address_entry = tk.Text(input_frame, width=30, height=3, wrap=tk.WORD) # Use Text for multi-line
        self.address_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        # Add scrollbar for address if needed
        address_scroll = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.address_entry.yview)
        address_scroll.grid(row=3, column=2, sticky='ns')
        self.address_entry['yscrollcommand'] = address_scroll.set

        ttk.Label(input_frame, text="Medical History:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.history_entry = tk.Text(input_frame, width=30, height=4, wrap=tk.WORD) # Use Text for multi-line
        self.history_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        # Add scrollbar for history
        history_scroll = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.history_entry.yview)
        history_scroll.grid(row=4, column=2, sticky='ns')
        self.history_entry['yscrollcommand'] = history_scroll.set

        # --- File Upload Buttons and Labels ---
        # Consent Form
        ttk.Button(input_frame, text="Upload Consent", command=lambda: self.upload_file("consent")).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        self.consent_label = ttk.Label(input_frame, text="No file selected", foreground="grey", width=30, anchor='w', wraplength=200)
        self.consent_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # ID Proof
        ttk.Button(input_frame, text="Upload ID Proof", command=lambda: self.upload_file("id_proof")).grid(row=1, column=3, padx=10, pady=5, sticky="w")
        self.id_proof_label = ttk.Label(input_frame, text="No file selected", foreground="grey", width=30, anchor='w', wraplength=200)
        self.id_proof_label.grid(row=1, column=4, padx=5, pady=5, sticky="w")

        # Report
        ttk.Button(input_frame, text="Upload Report", command=lambda: self.upload_file("report")).grid(row=2, column=3, padx=10, pady=5, sticky="w")
        self.report_label = ttk.Label(input_frame, text="No file selected", foreground="grey", width=30, anchor='w', wraplength=200)
        self.report_label.grid(row=2, column=4, padx=5, pady=5, sticky="w")

        # Buttons to open selected patient's documents
        ttk.Button(input_frame, text="Open Consent", command=lambda: self.open_document('consent_form_path')).grid(row=3, column=3, padx=10, pady=5, sticky="w")
        ttk.Button(input_frame, text="Open ID", command=lambda: self.open_document('id_proof_path')).grid(row=4, column=3, padx=10, pady=5, sticky="w")
        ttk.Button(input_frame, text="Open Report", command=lambda: self.open_document('report_path')).grid(row=5, column=3, padx=10, pady=5, sticky="w")


        # Make input frame columns resizable (optional, but good for different screen sizes)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(4, weight=1)

        # --- Action Buttons ---
        ttk.Button(button_frame, text="Add Patient", command=self.add_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Patient", command=self.update_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Patient", command=self.delete_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # --- Search ---
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_by_var = tk.StringVar(value="Name") # Default search by Name
        search_options = ["Name", "Contact"]
        search_dropdown = ttk.OptionMenu(search_frame, self.search_by_var, search_options[0], *search_options)
        search_dropdown.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_patients).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="View All", command=self.populate_list).pack(side=tk.LEFT, padx=5)


        # --- Patient List (Treeview) ---
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Age", "Contact", "Address", "History"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Age", text="Age")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Address", text="Address")
        self.tree.heading("History", text="Med History")

        # Set column widths
        self.tree.column("ID", width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("Name", width=150, anchor=tk.W)
        self.tree.column("Age", width=50, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("Contact", width=120, anchor=tk.W)
        self.tree.column("Address", width=200, anchor=tk.W)
        self.tree.column("History", width=200, anchor=tk.W)

        # Scrollbars for Treeview
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        # --- Populate Initial List ---
        self.populate_list()

    # --- CRUD and Helper Methods ---

    def on_closing(self):
        """Handle window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.conn:
                self.conn.close()
            self.root.destroy()

    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        """Executes a query and handles potential connection issues."""
        try:
            self.cursor.execute(query, params)
            if commit:
                self.conn.commit()
            if fetchone:
                return self.cursor.fetchone()
            if fetchall:
                return self.cursor.fetchall()
            # Check if it was an INSERT/UPDATE/DELETE to return lastrowid or rowcount
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                 # For INSERT, lastrowid is useful. For UPDATE/DELETE, rowcount.
                 # Returning lastrowid for INSERT is particularly helpful.
                 if query.strip().upper().startswith('INSERT'):
                     return self.cursor.lastrowid
                 else:
                     return self.cursor.rowcount
            return None # Or True if commit was the only action
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}\nQuery: {query}\nParams: {params}")
            # Consider attempting to reconnect or handle specific errors if needed
            return None # Indicate failure

    def populate_list(self, data=None):
        """Populates the treeview with patient data."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        if data is None: # If no specific data (like search results) is provided, fetch all
             records = self.execute_query("SELECT id, name, age, contact, address, medical_history FROM patients ORDER BY name ASC", fetchall=True)
        else:
             records = data

        if records:
            for row in records:
                # Ensure address and history are strings, handle None
                address = row[4] if row[4] else ""
                history = row[5] if row[5] else ""
                # Truncate long text for display in Treeview if desired
                display_address = (address[:30] + '...') if len(address) > 30 else address
                display_history = (history[:30] + '...') if len(history) > 30 else history
                self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], display_address, display_history))

    def clear_fields(self, clear_files=True):
        """Clears all input fields and optionally file selections."""
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.address_entry.delete('1.0', tk.END)
        self.history_entry.delete('1.0', tk.END)
        if clear_files:
            self.selected_consent_path.set("")
            self.selected_id_proof_path.set("")
            self.selected_report_path.set("")
            self.consent_label.config(text="No file selected", foreground="grey")
            self.id_proof_label.config(text="No file selected", foreground="grey")
            self.report_label.config(text="No file selected", foreground="grey")
        # Deselect item in treeview
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(selection)

    def get_selected_patient_id(self):
        """Returns the ID of the selected patient in the treeview, or None."""
        selected_item = self.tree.focus() # Get selected item
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a patient from the list first.")
            return None
        item_values = self.tree.item(selected_item, 'values')
        if not item_values:
             messagebox.showwarning("Selection Error", "Could not retrieve patient data. Please try again.")
             return None
        return item_values[0] # ID is the first value

    def on_item_select(self, event):
        """Handles item selection in the treeview, populates fields."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            # If selection is cleared, clear fields but keep file selections from potential update intent
            self.clear_fields(clear_files=False)
            return

        # Fetch full data including file paths for the selected patient
        patient_data = self.execute_query("SELECT * FROM patients WHERE id = ?", (patient_id,), fetchone=True)

        if patient_data:
            # Clear previous entries first, keep file selections until explicitly cleared/updated
            self.clear_fields(clear_files=False)

            # Populate basic fields
            self.name_entry.insert(0, patient_data[1]) # Name
            self.age_entry.insert(0, patient_data[2] if patient_data[2] is not None else "") # Age
            self.contact_entry.insert(0, patient_data[3] if patient_data[3] else "") # Contact
            self.address_entry.insert('1.0', patient_data[4] if patient_data[4] else "") # Address
            self.history_entry.insert('1.0', patient_data[5] if patient_data[5] else "") # History

            # Update file labels based on stored paths (don't reset selected_..._path vars yet)
            consent_path = patient_data[6]
            id_proof_path = patient_data[7]
            report_path = patient_data[8]

            self.consent_label.config(text=os.path.basename(consent_path) if consent_path else "No file stored",
                                      foreground="black" if consent_path else "grey")
            self.id_proof_label.config(text=os.path.basename(id_proof_path) if id_proof_path else "No file stored",
                                       foreground="black" if id_proof_path else "grey")
            self.report_label.config(text=os.path.basename(report_path) if report_path else "No file stored",
                                     foreground="black" if report_path else "grey")

            # Store the *current* paths from DB temporarily in case user wants to open them
            # We don't put these into self.selected_..._path unless user uploads a *new* file
            self._current_consent_db_path = consent_path
            self._current_id_proof_db_path = id_proof_path
            self._current_report_db_path = report_path

        else:
            messagebox.showerror("Error", f"Could not find patient data for ID: {patient_id}")
            self.clear_fields() # Clear everything if data fetch fails


    def upload_file(self, file_type):
        """Opens file dialog to select a file and updates the corresponding label and variable."""
        filepath = filedialog.askopenfilename(
            title=f"Select {file_type.replace('_', ' ').title()} File",
            filetypes=(("PDF files", "*.pdf"), ("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
        )
        if filepath:
            filename = os.path.basename(filepath)
            if file_type == "consent":
                self.selected_consent_path.set(filepath)
                self.consent_label.config(text=filename, foreground="blue") # Blue indicates newly selected
            elif file_type == "id_proof":
                self.selected_id_proof_path.set(filepath)
                self.id_proof_label.config(text=filename, foreground="blue")
            elif file_type == "report":
                self.selected_report_path.set(filepath)
                self.report_label.config(text=filename, foreground="blue")

    def add_patient(self):
        """Adds a new patient record to the database."""
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        contact = self.contact_entry.get().strip()
        address = self.address_entry.get("1.0", tk.END).strip()
        history = self.history_entry.get("1.0", tk.END).strip()

        # --- Input Validation ---
        if not name:
            messagebox.showerror("Input Error", "Patient Name is required.")
            return
        if not contact:
             messagebox.showwarning("Input Warning", "Contact number is recommended.")
             # Allow adding without contact if desired, otherwise return

        age = None
        if age_str:
            try:
                age = int(age_str)
                if age < 0 or age > 150: # Basic age sanity check
                     messagebox.showerror("Input Error", "Please enter a valid age.")
                     return
            except ValueError:
                messagebox.showerror("Input Error", "Age must be a number.")
                return

        # --- Insert basic data first to get the patient ID ---
        try:
            insert_query = """
                INSERT INTO patients (name, age, contact, address, medical_history)
                VALUES (?, ?, ?, ?, ?)
            """
            patient_id = self.execute_query(insert_query, (name, age, contact, address, history), commit=True) # Get last inserted ID

            if patient_id is None: # Check if execute_query indicated an error (e.g., UNIQUE constraint)
                 # Error message already shown by execute_query
                 return

            # --- Handle File Copying ---
            consent_dest_path = None
            id_proof_dest_path = None
            report_dest_path = None

            # Copy files using the obtained patient_id for unique naming
            consent_src = self.selected_consent_path.get()
            if consent_src:
                consent_dest_path = safe_copy_file(consent_src, patient_id, "consent")

            id_proof_src = self.selected_id_proof_path.get()
            if id_proof_src:
                id_proof_dest_path = safe_copy_file(id_proof_src, patient_id, "id_proof")

            report_src = self.selected_report_path.get()
            if report_src:
                report_dest_path = safe_copy_file(report_src, patient_id, "report")

            # --- Update the record with file paths ---
            update_paths_query = """
                UPDATE patients
                SET consent_form_path = ?, id_proof_path = ?, report_path = ?
                WHERE id = ?
            """
            self.execute_query(update_paths_query, (consent_dest_path, id_proof_dest_path, report_dest_path, patient_id), commit=True)

            messagebox.showinfo("Success", "Patient added successfully!")
            self.clear_fields()
            self.populate_list()

        except sqlite3.IntegrityError as e:
             if "UNIQUE constraint failed: patients.contact" in str(e):
                 messagebox.showerror("Database Error", f"A patient with contact number '{contact}' already exists.")
             else:
                 messagebox.showerror("Database Error", f"An integrity error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def update_patient(self):
        """Updates the selected patient's record."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return

        # Get potentially updated data from fields
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        contact = self.contact_entry.get().strip()
        address = self.address_entry.get("1.0", tk.END).strip()
        history = self.history_entry.get("1.0", tk.END).strip()

        # --- Input Validation ---
        if not name:
            messagebox.showerror("Input Error", "Patient Name cannot be empty.")
            return

        age = None
        if age_str:
            try:
                age = int(age_str)
                if age < 0 or age > 150:
                     messagebox.showerror("Input Error", "Please enter a valid age.")
                     return
            except ValueError:
                messagebox.showerror("Input Error", "Age must be a number.")
                return

        # --- Fetch current file paths before update ---
        current_data = self.execute_query("SELECT consent_form_path, id_proof_path, report_path FROM patients WHERE id = ?", (patient_id,), fetchone=True)
        if not current_data:
             messagebox.showerror("Error", "Could not retrieve current patient data for update.")
             return
        current_consent_path, current_id_proof_path, current_report_path = current_data

        # --- Handle File Updates ---
        consent_dest_path = current_consent_path
        id_proof_dest_path = current_id_proof_path
        report_dest_path = current_report_path

        new_consent_src = self.selected_consent_path.get()
        if new_consent_src: # If a new file was selected via "Upload"
            # Delete the old file *before* copying the new one
            safe_delete_file(current_consent_path)
            consent_dest_path = safe_copy_file(new_consent_src, patient_id, "consent")
            if consent_dest_path is None: # Check if copy failed
                 messagebox.showwarning("File Warning", "Failed to update consent form file. Keeping the old one if it exists.")
                 consent_dest_path = current_consent_path # Revert to old path if copy failed

        new_id_proof_src = self.selected_id_proof_path.get()
        if new_id_proof_src:
            safe_delete_file(current_id_proof_path)
            id_proof_dest_path = safe_copy_file(new_id_proof_src, patient_id, "id_proof")
            if id_proof_dest_path is None:
                 messagebox.showwarning("File Warning", "Failed to update ID proof file. Keeping the old one if it exists.")
                 id_proof_dest_path = current_id_proof_path

        new_report_src = self.selected_report_path.get()
        if new_report_src:
            safe_delete_file(current_report_path)
            report_dest_path = safe_copy_file(new_report_src, patient_id, "report")
            if report_dest_path is None:
                 messagebox.showwarning("File Warning", "Failed to update report file. Keeping the old one if it exists.")
                 report_dest_path = current_report_path


        # --- Update Database ---
        try:
            update_query = """
                UPDATE patients
                SET name = ?, age = ?, contact = ?, address = ?, medical_history = ?,
                    consent_form_path = ?, id_proof_path = ?, report_path = ?
                WHERE id = ?
            """
            params = (name, age, contact, address, history,
                      consent_dest_path, id_proof_dest_path, report_dest_path,
                      patient_id)
            rows_affected = self.execute_query(update_query, params, commit=True)

            if rows_affected is not None: # Check if query execution was successful
                messagebox.showinfo("Success", "Patient updated successfully!")
                self.clear_fields()
                self.populate_list()
            # else: Error message already shown by execute_query

        except sqlite3.IntegrityError as e:
             if "UNIQUE constraint failed: patients.contact" in str(e):
                 messagebox.showerror("Database Error", f"Another patient with contact number '{contact}' already exists.")
             else:
                 messagebox.showerror("Database Error", f"An integrity error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during update: {e}")


    def delete_patient(self):
        """Deletes the selected patient record and associated files."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient record and all associated documents? This action cannot be undone."):
            # --- Get file paths BEFORE deleting the record ---
            file_paths = self.execute_query("SELECT consent_form_path, id_proof_path, report_path FROM patients WHERE id = ?", (patient_id,), fetchone=True)

            # --- Delete record from database ---
            rows_affected = self.execute_query("DELETE FROM patients WHERE id = ?", (patient_id,), commit=True)

            if rows_affected is not None and rows_affected > 0:
                # --- Delete associated files ---
                if file_paths:
                    safe_delete_file(file_paths[0]) # Consent
                    safe_delete_file(file_paths[1]) # ID Proof
                    safe_delete_file(file_paths[2]) # Report

                messagebox.showinfo("Success", "Patient record deleted successfully.")
                self.clear_fields()
                self.populate_list()
            elif rows_affected == 0:
                 messagebox.showwarning("Delete Warning", "Patient record not found or already deleted.")
                 self.clear_fields() # Clear fields even if delete didn't happen in DB
                 self.populate_list() # Refresh list
            # else: Error message shown by execute_query


    def search_patients(self):
        """Searches patients by name or contact and updates the list."""
        search_term = self.search_var.get().strip()
        search_by = self.search_by_var.get()

        if not search_term:
            messagebox.showwarning("Search", "Please enter a search term.")
            return

        query = f"SELECT id, name, age, contact, address, medical_history FROM patients WHERE {search_by.lower()} LIKE ? ORDER BY name ASC"
        params = (f'%{search_term}%',) # Add wildcards for partial matching

        results = self.execute_query(query, params, fetchall=True)

        if results:
            self.populate_list(data=results)
        else:
            messagebox.showinfo("Search Result", f"No patients found matching '{search_term}' by {search_by}.")
            self.populate_list(data=[]) # Clear list if no results

    def open_document(self, path_column_name):
        """Opens the document associated with the selected patient using the default OS application."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return

        # Fetch the specific document path
        file_path_data = self.execute_query(f"SELECT {path_column_name} FROM patients WHERE id = ?", (patient_id,), fetchone=True)

        if file_path_data and file_path_data[0]:
            file_path = file_path_data[0]
            if os.path.exists(file_path):
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin": # macOS
                        subprocess.run(["open", file_path], check=True)
                    else: # Linux and other POSIX
                        subprocess.run(["xdg-open", file_path], check=True)
                except FileNotFoundError:
                     messagebox.showerror("Error", f"Could not find the application to open the file.\nPath: {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}\nPath: {file_path}")
            else:
                messagebox.showwarning("File Not Found", f"The document file does not exist at the stored path:\n{file_path}\nIt might have been moved or deleted.")
        else:
            messagebox.showinfo("No Document", f"No document of this type is stored for the selected patient.")


# --- Main Execution ---
if __name__ == "__main__":
    # Perform initial setup
    print(f"Database Path: {DATABASE_PATH}")
    print(f"Documents Path: {DOCUMENTS_BASE_PATH}")
    initialize_database()
    initialize_documents_folder()

    # Create and run the Tkinter app
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()