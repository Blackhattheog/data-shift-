# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font
import customtkinter as ctk
import os
import sys
import subprocess
from datetime import datetime, timedelta
import random
import string

def generate_license_key():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    part3 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"{part1}-{part2}-{part3}"

def get_hard_disk_serial():
    """
    Returns the best available unique hardware ID:
    1. Disk/SSD Serial
    2. C: Volume Serial
    3. Machine UUID
    """

    # 1️⃣ Try Disk / SSD Serial Number
    try:
        output = subprocess.check_output(
            "wmic diskdrive get serialnumber",
            shell=True
        ).decode(errors="ignore")

        lines = [l.strip() for l in output.split("\n") if l.strip()]
        if len(lines) >= 2 and lines[1] not in ["", "UNKNOWN"]:
            return f"DISK-{lines[1]}"
    except:
        pass

    # 2️⃣ Try Volume Serial Number (C Drive)
    try:
        output = subprocess.check_output(
            "vol C:",
            shell=True
        ).decode(errors="ignore")

        if "Serial Number is" in output:
            serial = output.split("Serial Number is")[-1].strip()
            return f"VOL-{serial}"
    except:
        pass

    # 3️⃣ Fallback → Machine UUID
    try:
        output = subprocess.check_output(
            "wmic csproduct get uuid",
            shell=True
        ).decode(errors="ignore")

        lines = [l.strip() for l in output.split("\n") if l.strip()]
        if len(lines) >= 2:
            return f"UUID-{lines[1]}"
    except:
        pass

    return "UNKNOWN"









class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()   # Hide main window

        self.splash = tk.Toplevel(root)
        self.splash.title("D-SHIFT Loading")

        # --- Center Window ---
        width, height = 1200, 800
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        self.splash.overrideredirect(True)
        self.splash.configure(bg="white")
        self.splash.attributes("-topmost", True)

        self.main_container = tk.Frame(self.splash, bg="white")
        self.main_container.pack(expand=True)

        # Logo / Title
        try:
            img = Image.open("logo.PNG").resize((150, 150))
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self.main_container, image=self.photo, bg="white").pack(pady=10)
        except Exception:
            tk.Label(
                self.main_container,
                text="D-SHIFT",
                font=("Arial", 45, "bold"),
                bg="white",
                fg="#2c3e50"
            ).pack(pady=20)

        # Progress %
        self.lbl_pct = tk.Label(
            self.main_container,
            text="Loading 0%",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        )
        self.lbl_pct.pack(pady=5)

        # Progress Bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            thickness=12,
            troughcolor="#f0f0f0",
            background="#3498db"
        )

        self.progress = ttk.Progressbar(
            self.main_container,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=15)

        self.current_val = 0
        self.update_loader()

    def update_loader(self):
        if self.current_val < 100:
            self.current_val += 2
            self.progress["value"] = self.current_val
            self.lbl_pct.config(text=f"Loading {self.current_val}%")
            self.splash.after(30, self.update_loader)

    # ✅ IMPORTANT: add destroy method
    def destroy(self):
        if self.splash.winfo_exists():
            self.splash.destroy()
# --- End of Splash Class ---










from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pandas as pd

import re
import pdfplumber
import camelot
import requests
import xml.etree.ElementTree as ET
import shutil

import warnings
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import numpy as np 

from lxml import etree

import firebase_admin
from firebase_admin import credentials, firestore


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 🔐 Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate(resource_path("firebase_key.json"))

 # same folder as P.PY
    firebase_admin.initialize_app(cred)

# 🔥 Firestore DB object (GLOBAL)
db = firestore.client()







# =======================================================

# =======================================================
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        """Set completion list and sort alphabetically"""
        self._completion_list = sorted(completion_list, key=str.lower)
        self["values"] = self._completion_list
        self.bind("<KeyRelease>", self._check_input)

    def _check_input(self, event):
        """Filter dropdown values as user types"""
        value = self.get().lower()
        if value == "":
            data = self._completion_list
        else:
            data = [item for item in self._completion_list if value in item.lower()]
        self["values"] = data
        if data:
            self.event_generate("<Down>")

# -------------------------------------------------------
import customtkinter as ctk
from tkinter import messagebox

# Set default appearance mode and color theme for a fresh, attractive look.
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")



# =======================================================
# २. MainApp Class (Already CTK, but enhancements added)
# =======================================================
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D-SHIFT Utility")
        self.root.geometry("1000x600")

        # ===== HEADER =====
        title_frame = ctk.CTkFrame(root, fg_color="#34495e", corner_radius=0)
        title_frame.pack(fill="x")

        ctk.CTkLabel(
            title_frame,
            text="D-SHIFT",
            font=ctk.CTkFont("Arial", 28, "bold"),
            text_color="white",
            pady=15
        ).pack(fill="x")

        # ===== MAIN FRAME =====
        main_frame = ctk.CTkFrame(root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== LEFT MENU =====
        self.menu_frame = ctk.CTkFrame(
            main_frame,
            width=220,
            fg_color="#ecf0f1",
            corner_radius=15
        )
        self.menu_frame.pack(side="left", fill="y", padx=(0, 15))
        self.menu_frame.pack_propagate(False)

        # ===== LEFT MENU BUTTONS =====
        ctk.CTkButton(
            self.menu_frame,
            text="Reports",
            height=45,
            corner_radius=15,
            fg_color="#34495e",
            hover_color="#2c3e50",
            text_color="white",
            command=self.open_reports
        ).pack(fill="x", padx=10, pady=(20, 5))

        ctk.CTkButton(
            self.menu_frame,
            text="Settings",
            height=45,
            corner_radius=15,
            fg_color="#34495e",
            hover_color="#2c3e50",
            text_color="white",
            command=self.open_settings
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            self.menu_frame,
            text="Downloads",
            height=45,
            corner_radius=15,
            fg_color="#34495e",
            hover_color="#2c3e50",
            text_color="white",
            command=self.open_downloads
        ).pack(fill="x", padx=10, pady=5)

        # RIGHT CONTENT
        self.right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # ===== TOP RIGHT INFO =====
        self.balance_title = ctk.CTkLabel(
            self.right_frame,
            text="💼 Account",
            font=ctk.CTkFont("Arial", 16, "bold")
        )
        self.lbl_balance = ctk.CTkLabel(
            self.right_frame,
            text="Please Login",
            font=ctk.CTkFont("Arial", 15),
            text_color="#27ae60"
        )

        self.login_btn = ctk.CTkButton(
            self.right_frame,
            text="Login",
            command=self.show_login_form,
            width=100,
            corner_radius=25,
            fg_color="#3498db"
        )

        # ===== MAIN ACTION BUTTONS =====
        self.btn_pdf = ctk.CTkButton(
            self.right_frame,
            text="📄 PDF To Tally",
            corner_radius=25,
            fg_color="#27ae60",
            command=self.open_pdf_app
        )

        self.btn_ledger = ctk.CTkButton(
            self.right_frame,
            text="🧾 Create Ledger",
            corner_radius=25,
            fg_color="#27ae60",
            command=self.open_create_ledger_window 
        )

        # Store main widgets
        self.main_widgets = [
            self.balance_title,
            self.lbl_balance,
            self.login_btn,
            self.btn_pdf,
            self.btn_ledger
        ]

        self.login_frame = None
        self.current_user = None

        # 🔒 START WITH LOGIN
        self.show_login_form()

    # ================= MAIN UI SHOW/HIDE =================
    def hide_main_ui(self):
        for w in self.main_widgets:
            w.pack_forget()

    def show_main_ui(self):
        self.balance_title.pack(anchor="ne", padx=25, pady=(25, 0))
        self.lbl_balance.pack(anchor="ne", padx=25)
        self.btn_pdf.pack(anchor="nw", padx=25, pady=20)
        self.btn_ledger.pack(anchor="nw", padx=25)
        self.login_btn.pack_forget()

    # ================= LOGIN FORM =================
    def show_login_form(self):
        self.hide_main_ui()

        if self.login_frame:
            self.login_frame.destroy()

        self.login_frame = ctk.CTkFrame(
            self.right_frame,
            fg_color="#ecf0f1",
            corner_radius=15
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.login_frame,
            text="🔐 Login",
            font=ctk.CTkFont("Arial", 20, "bold")
        ).grid(row=0, columnspan=2, pady=20)

        ctk.CTkLabel(self.login_frame, text="Email").grid(row=1, column=0, padx=10, sticky="w")
        self.ent_email = ctk.CTkEntry(self.login_frame, width=250)
        self.ent_email.grid(row=1, column=1, pady=5)

        ctk.CTkLabel(self.login_frame, text="Password").grid(row=2, column=0, padx=10, sticky="w")
        self.ent_pass = ctk.CTkEntry(self.login_frame, width=250, show="*")
        self.ent_pass.grid(row=2, column=1, pady=5)

        ctk.CTkButton(
            self.login_frame,
            text="Login",
            command=self.do_login,
            fg_color="#27ae60"
        ).grid(row=3, columnspan=2, pady=15)

        ctk.CTkButton(
            self.login_frame,
            text="Register",
            command=self.show_register_form,
            fg_color="transparent",
            text_color="#2980b9"
        ).grid(row=4, columnspan=2)

        ctk.CTkButton(
            self.login_frame,
            text="Forgot Password?",
            command=self.show_forgot_password,
            fg_color="transparent",
            text_color="#e67e22"
        ).grid(row=5, columnspan=2)

    # ================= LOGIN LOGIC =================
    def do_login(self):
        email = self.ent_email.get().strip()
        password = self.ent_pass.get().strip()

        doc = db.collection("Users").document(email).get()
        if not doc.exists:
            messagebox.showerror("Error", "User not found")
            return

        user = doc.to_dict()

        # 🔐 Password check
        if user["password"] != password:
            messagebox.showerror("Error", "Wrong password")
            return

        # 🚫 License activation check
        if user["status"] != "active":
            messagebox.showerror("Blocked", "License not activated")
            return

        # 📅 Expiry check
        today = datetime.today().date()
        expiry_date = datetime.strptime(user["expiry"], "%Y-%m-%d").date()

        if today > expiry_date:
            messagebox.showerror(
                "License Expired",
                f"Your license expired on {expiry_date}"
            )
            return

        remaining_days = (expiry_date - today).days

        # 🖥️ One-PC-One-License check
        current_disk = get_hard_disk_serial()
        stored_disk = user.get("hard_disk")

        if stored_disk not in [None, "UNKNOWN", current_disk]:
            messagebox.showerror(
                "License Error",
                "This license is already used on another system"
            )
            return

        # 🔐 Auto bind for old users
        if stored_disk in [None, "UNKNOWN"]:
            db.collection("Users").document(email).update({
                "hard_disk": current_disk
            })

        # ✅ SUCCESS
        self.current_user = user
        self.login_frame.destroy()
        self.login_frame = None
        self.show_main_ui()

        # 🔥 SHOW EXPIRY INFO
        self.balance_title.configure(text=f"💼 {user['name']}")
        self.lbl_balance.configure(
            text=f"Expiry Date: {expiry_date} | Remaining Days: {remaining_days}"
        )

    # ================= REGISTER =================
    def show_register_form(self):
        self.hide_main_ui()
        self.login_frame.destroy()

        self.login_frame = ctk.CTkFrame(self.right_frame, fg_color="#ecf0f1", corner_radius=15)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        fields = ["Name", "Email", "Password", "Mobile", "DOB (YYYY-MM-DD)", "License Key"]
        self.reg = {}

        ctk.CTkLabel(
            self.login_frame,
            text="📝 Register",
            font=ctk.CTkFont("Arial", 20, "bold")
        ).grid(row=0, columnspan=2, pady=15)

        for i, f in enumerate(fields, start=1):
            ctk.CTkLabel(self.login_frame, text=f).grid(row=i, column=0, padx=10, sticky="w")
            e = ctk.CTkEntry(self.login_frame, width=260, show="*" if f == "Password" else "")
            e.grid(row=i, column=1, pady=5)
            self.reg[f] = e

        ctk.CTkButton(
            self.login_frame,
            text="Register",
            command=self.register_user,
            fg_color="#27ae60"
        ).grid(row=len(fields)+1, columnspan=2, pady=15)

        ctk.CTkButton(
            self.login_frame,
            text="Back to Login",
            command=self.show_login_form,
            fg_color="transparent"
        ).grid(row=len(fields)+2, columnspan=2)

    def register_user(self):
        data = {k: v.get().strip() for k, v in self.reg.items()}
        ref = db.collection("Users").document(data["Email"])

        if ref.get().exists:
            messagebox.showerror("Error", "User already exists")
            return

        # 📅 Dates
        start_date = datetime.today().date()
        expiry_date = start_date + timedelta(days=365)

        # 🔑 License key generate
        license_key = generate_license_key()

        # 🖥️ Hardware ID
        hardware_id = get_hard_disk_serial()

        ref.set({
            "name": data["Name"],
            "email": data["Email"],
            "password": data["Password"],
            "mobile": data["Mobile"],
            "dob": data["DOB (YYYY-MM-DD)"],

            "license_key": license_key,
            "hard_disk": hardware_id,

            # 📅 Dates
            "start_date": start_date.strftime("%Y-%m-%d"),
            "expiry": expiry_date.strftime("%Y-%m-%d"),

            "status": "inactive"
        })

        messagebox.showinfo(
            "Registered",
            f"Registration Date : {start_date}\n"
            f"Expiry Date       : {expiry_date}\n\n"
            f"License Key:\n{license_key}\n\n"
            "Wait for activation."
        )

        self.show_login_form()

    # ================= FORGOT PASSWORD =================
    def show_forgot_password(self):
        self.hide_main_ui()
        self.login_frame.destroy()

        self.login_frame = ctk.CTkFrame(self.right_frame, fg_color="#ecf0f1", corner_radius=15)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        labels = ["Email", "Mobile", "DOB (YYYY-MM-DD)", "New Password"]
        self.fp = {}

        ctk.CTkLabel(
            self.login_frame,
            text="🔑 Reset Password",
            font=ctk.CTkFont("Arial", 18, "bold")
        ).grid(row=0, columnspan=2, pady=15)

        for i, l in enumerate(labels, start=1):
            ctk.CTkLabel(self.login_frame, text=l).grid(row=i, column=0, padx=10, sticky="w")
            e = ctk.CTkEntry(self.login_frame, width=260, show="*" if "Password" in l else "")
            e.grid(row=i, column=1, pady=5)
            self.fp[l] = e

        ctk.CTkButton(
            self.login_frame,
            text="Reset",
            command=self.reset_password,
            fg_color="#e67e22"
        ).grid(row=len(labels)+1, columnspan=2, pady=15)

    def reset_password(self):
        email = self.fp["Email"].get().strip()
        doc = db.collection("Users").document(email).get()

        if not doc.exists:
            messagebox.showerror("Error", "User not found")
            return

        user = doc.to_dict()

        if user["mobile"] != self.fp["Mobile"].get() or user["dob"] != self.fp["DOB (YYYY-MM-DD)"].get():
            messagebox.showerror("Error", "Verification failed")
            return

        db.collection("Users").document(email).update({
            "password": self.fp["New Password"].get()
        })

        messagebox.showinfo("Success", "Password reset")
        self.show_login_form()

    # ===== Other Page Functions =====
    # ============================================================
    # MAIN APP → OPEN PDF APP & CREATE LEDGER WINDOW (FULL LOGIC)
    # ============================================================
    def open_pdf_app(self):
        """Open PDFApp window and hide the main window."""
        
        # 1️⃣ Hide Main Window
        self.root.withdraw()

        # 2️⃣ Create New Window
        new_win = tk.Toplevel(self.root)
        new_win.title("PDF to Tally - Bank Statement Converter")

        # 3️⃣ Maximize Window
        new_win.after(10, lambda: new_win.wm_state('zoomed'))
        new_win.resizable(True, True)

        # 4️⃣ Load PDFApp Class
        pdf_window = PDFApp(new_win)

        # 5️⃣ Define Close Action
        def on_close():
            new_win.destroy()              # Close PDF window
            self.root.deiconify()          # Show Main Window again
            self.root.after(10, lambda: self.root.wm_state('zoomed'))

        # 6️⃣ Attach close event
        new_win.protocol("WM_DELETE_WINDOW", on_close)



    # ============================================================
    # OPEN CREATE LEDGER WINDOW (EXCEL → TALLY LEDGER)
    # ============================================================
    def open_create_ledger_window(self):
        """Open CreateLedgerWindow and hide main window."""

        # 1️⃣ Hide Main Window
        self.root.withdraw()

        # 2️⃣ Create New Window
        new_win = tk.Toplevel(self.root)
        new_win.title("Create Ledger From Excel")

        # 3️⃣ Maximize
        new_win.after(10, lambda: new_win.wm_state('zoomed'))
        new_win.resizable(True, True)

        # 4️⃣ Load Class
        CreateLedgerWindow(new_win)

        # 5️⃣ Close Event
        def on_close():
            new_win.destroy()
            self.root.deiconify()
            self.root.after(10, lambda: self.root.wm_state('zoomed'))

        # 6️⃣ Attach close protocol
        new_win.protocol("WM_DELETE_WINDOW", on_close)




    def open_reports(self):
        messagebox.showinfo("Reports", "Reports section coming soon!")

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings section coming soon!")


    # ============================================
    # 🔽 DOWNLOAD SECTION (Built-in Excel)
    # ============================================
    def open_downloads(self):
        # Create new window for Excel download section
        win = tk.Toplevel(self.root)
        win.title("Download Excel Files")
        win.geometry("420x280")
        win.resizable(False, False)

        ctk.CTkLabel(
            win,
            text="📂 Available Excel Files",
            font=ctk.CTkFont("Arial", 16, "bold"),
            text_color="#34495e"
        ).pack(pady=10)

        # ✅ Files embedded inside the EXE or same folder
        # Use resource_path with the file name (e.g., 'Bank Statement.xlsx')
        self.files_dict = {
            "J K Bank Statement Format": "J K Bank Statment format.xlsm",
            "Bank Statement": "Bank Statment.xlsx",
        }

        listbox = tk.Listbox(win, font=("Arial", 12))
        for name in self.files_dict.keys():
            listbox.insert(tk.END, name)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)

        def download_selected():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a file to download.")
                return

            file_name_key = list(self.files_dict.keys())[selected[0]]

            # 1. Get the actual source path inside EXE/temp folder
            relative_path = self.files_dict[file_name_key]
            src_path = self.resource_path(relative_path)

            # 2. Check whether the file exists inside EXE package
            if not os.path.exists(src_path):
                messagebox.showerror("Error", f"Embedded file not found:\n{src_path}")
                return

            # 3. Ask user where to save the selected file (Save As dialog)
            default_filename = os.path.basename(relative_path)

            # Show Save As dialog to user
            dst_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(default_filename)[1],   # Keep original file extension
                initialfile=default_filename,
                title="Save the Excel File",
                filetypes=(("Excel files", "*.xlsx *.xlsm"), ("All files", "*.*"))
            )

            # If user cancelled the dialog
            if not dst_path:
                return

            try:
                # 4. Copy file from PyInstaller temp folder to user-selected location
                shutil.copy(src_path, dst_path)
                messagebox.showinfo(
                    "Downloaded",
                    f"✅ '{file_name_key}' saved to:\n{dst_path}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file.\n{e}")

        ctk.CTkButton(
            win,
            text="⬇ Download Selected File",
            command=download_selected,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            text_color="white",
            corner_radius=25,
            height=40
        ).pack(pady=10)

    # ============================================
    # ✅ Helper to access files inside EXE or Folder
    # ============================================




class CreateLedgerWindow:
    """
    Manages the UI for creating Tally Ledgers, including data entry via Treeview, 
    Excel import, Tally connectivity, and data validation.
    Enhanced with auto-scroll and auto-fit column width features.
    """

    REQUIRED_COLUMNS = [
        "*LEDGER NAME",
        "TYPE / GROUP (Names As Per Tally)",
        "*ALIAS",
        "ADDRESS (Bldg / No)",
        "ADDRESS (Road / Area)",
        "ADDRESS (City)",
        "*ADDRESS (State)", # Dropdown for States
        "ADDRESS (Pin)",
        "ADDRESS (Country)",
        "*GST REG. TYPE", # Dropdown for GST Types
        "GST REG. GSTIN / UIN",
        "GST REG. ECOMMERCE",
        "BILL WISE", # Dropdown for Yes/No
        "INVENTORY EFFECT", # Dropdown for Yes/No
        "COST CENTRE", # Dropdown for Yes/No
        "MOBILE NUMBER",
        "EMAIL ID - 1",
        "IT PAN",
        "VAT NO",
        "CST NO",
        "BILL CREDIT PERIOD",
        "FAX NUMBER",
        "DEBIT BALANCE",
        "CREDIT BALANCE",
        "*OPENING BALANCE"
    ]
    
    # Dropdown Options
    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
        "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", 
        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
        "Uttarakhand", "West Bengal", 
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]
    GST_REG_TYPES = ["Composition", "Consumer", "Regular", "Unregistered"]
    YES_NO_OPTIONS = ["Yes", "No"]
    
    # Map of column names to their dropdown options
    DROPDOWN_COLUMNS = {
        "TYPE / GROUP (Names As Per Tally)": [], # Tally Groups (dynamic)
        "*ADDRESS (State)": INDIAN_STATES,
        "*GST REG. TYPE": GST_REG_TYPES,
        "BILL WISE": YES_NO_OPTIONS,
        "INVENTORY EFFECT": YES_NO_OPTIONS,
        "COST CENTRE": YES_NO_OPTIONS
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Create Ledger From Excel")
        self.root.geometry("1200x700")
        self.company_name = "COMPANY"

        # Tally data stores
        self.tally_ledgers = []       # List of existing ledger names from Tally
        self.parent_groups = []       # List of parent group names from Tally
        # Dictionary to hold combobox widgets for each row/column
        self.item_comboboxes = {} 

        # State to track Tally connection
        self._tally_connected = False 

        # UI State for Editing and Navigation
        self._edit_widget = None
        self._current_edit_row = None
        self._current_edit_col_index = None

        # --- UI Building ---
        title = ctk.CTkLabel(
            root,
            text="🧾 Create Ledger From Excel",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#34495e"
        )
        title.pack(pady=12)

        top_frame = ctk.CTkFrame(root, fg_color="transparent")
        top_frame.pack(fill="x", padx=15)

        self.btn_import = ctk.CTkButton(
            top_frame, text="📂 Import Excel (Append)", corner_radius=18,
            fg_color="#3498db", hover_color="#2980b9",
            command=self.import_excel, width=200, height=38
        )
        self.btn_import.pack(side="left", padx=(0, 10))

        self.btn_add = ctk.CTkButton(
            top_frame, text="➕ Add Blank Row", corner_radius=18,
            fg_color="#27ae60", hover_color="#2ecc71",
            command=self.add_blank_row, width=160, height=38
        )
        self.btn_add.pack(side="left", padx=8)

        self.btn_delete = ctk.CTkButton(
            top_frame, text="🗑️ Delete Selected Row", corner_radius=18,
            fg_color="#e67e22", hover_color="#d35400",
            command=self.delete_selected_row, width=200, height=38
        )
        self.btn_delete.pack(side="left", padx=8)

        # Tally Connect + Validate buttons
        self.btn_tally = ctk.CTkButton(
            top_frame, text="🔌 Connect to Tally", corner_radius=18,
            fg_color="#8e44ad", hover_color="#732d91",
            command=self.connect_to_tally, width=180, height=38
        )
        self.btn_tally.pack(side="left", padx=8)

        self.btn_validate = ctk.CTkButton(
            top_frame, text="✔ Validate Ledger Names", corner_radius=18,
            fg_color="#2c3e50", hover_color="#1f2d3a",
            command=self.validate_ledgers, width=200, height=38
        )
        self.btn_validate.pack(side="left", padx=8)
        # CREATE XML button (Hidden by default)
        self.btn_create_xml = ctk.CTkButton(
            top_frame,
            text="🧾 Create XML",
            corner_radius=18,
            fg_color="#16a085",
            hover_color="#138d75",
            command=self.create_xml,   # तुझा XML function
            width=160,
            height=38
        )
        self.btn_create_xml.pack_forget()

        # Validation state flag
        self._validation_passed = False

        # NEW: Auto-fit columns button
        self.btn_autofit = ctk.CTkButton(
            top_frame, text="📏 Auto-fit Columns", corner_radius=18,
            fg_color="#16a085", hover_color="#138d75",
            command=self.autofit_columns, width=180, height=38
        )
        self.btn_autofit.pack(side="left", padx=8)

        # Table frame
        self.table_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
        self.table_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        self._build_treeview()
        self._build_context_menu()

        # Bindings for navigation (Tab/Arrow Keys)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Tab>", self._on_tab)
        self.tree.bind("<Shift-Tab>", self._on_shift_tab)
        self.tree.bind("<Right>", self._on_right_arrow)
        self.tree.bind("<Left>", self._on_left_arrow)
        self.tree.bind("<Down>", self._on_down_arrow)
        self.tree.bind("<Up>", self._on_up_arrow)
        # Bind mouse click to ensure the treeview focus is on the clicked cell
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Reposition comboboxes when the treeview is scrolled or resized
        self.tree.bind("<Configure>", lambda e: self._reposition_all_comboboxes())
        self.tree.bind("<ButtonRelease-1>", lambda e: self._reposition_all_comboboxes())

        # Add the first blank row on startup
        self.add_blank_row()
        
        # Auto-fit columns on startup
        self.root.after(100, self.autofit_columns)

    # ==================== EXCEL-LIKE AUTO-FIT WITH SMART SCROLLING ====================
    def autofit_columns(self):
        """
        AutoFit Treeview columns based on header and cell width.
        Safe: Uses ttk.Style to get Treeview font (Treeview has no -font option)
        """

        import tkinter.font as tkfont
        style = ttk.Style()

        # Get the Treeview font safely
        tv_font_name = style.lookup("Treeview", "font")
        font = tkfont.Font(font=tv_font_name)

        for col in self.REQUIRED_COLUMNS:

            # measure header width
            max_width = font.measure(col) + 30

            # measure all cell values
            for item in self.tree.get_children():
                text = self.tree.set(item, col)
                if text:
                    w = font.measure(text) + 30
                    if w > max_width:
                        max_width = w

            # minimum width
            if max_width < 120:
                max_width = 120

            # apply column width
            self.tree.column(col, width=int(max_width), minwidth=120, stretch=False)

        # redraw + reposition
        self.tree.update_idletasks()
        self._reposition_all_comboboxes()





    
    # ==================== SMART SCROLLING - EXCEL BEHAVIOR (FIXED) ====================
    def _ensure_column_visible(self, col_index):
        """
        Ensures horizontal scrolling automatically moves so that the given column becomes visible.
        Exactly like Excel behaviour.
        """
        try:
            # Width of all columns before target column
            target_left = sum(self.tree.column(self.REQUIRED_COLUMNS[i], "width") for i in range(col_index))

            # Width of all columns up to target column
            target_right = target_left + self.tree.column(self.REQUIRED_COLUMNS[col_index], "width")

            # Current visible area
            x0 = self.tree.xview()[0]
            x1 = self.tree.xview()[1]

            # Convert to pixel range
            total_width = sum(self.tree.column(c, "width") for c in self.REQUIRED_COLUMNS)
            visible_left = x0 * total_width
            visible_right = x1 * total_width

            # If target column is left side invisible → scroll left
            if target_left < visible_left:
                fraction = target_left / total_width
                self.tree.xview_moveto(fraction)

            # If target column is right side invisible → scroll right
            elif target_right > visible_right:
                fraction = (target_right - (visible_right - visible_left)) / total_width
                self.tree.xview_moveto(fraction)

            self.root.after(5, self._reposition_all_comboboxes)

        except Exception as e:
            pass


    # =========================================================================
        
    def _on_tree_click(self, event):
        """Sets the internal tracking index when a cell is clicked, and saves active edit."""
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        
        # Calculate the NEW index
        new_col_index = 0
        if row_id and col_id and col_id.startswith("#"):
            new_col_index = int(col_id.replace("#", "")) - 1
        
        self.tree.selection_set(row_id)
        
        # Stop any active edit session if clicking outside the widget
        # Save active edit, which relies on the OLD self._current_edit_col_index
        if self._edit_widget:
            try:
                self._save_active_edit()
            except:
                pass                

        # Update global state AFTER save is done
        self._current_edit_col_index = new_col_index
        
    # --------------------------


    def _save_active_edit(self):
        if not self._edit_widget:
            return
        
        try:
            if isinstance(self._edit_widget, ttk.Combobox):
                val = self._edit_widget.get()
                col_index = self._current_edit_col_index
                row_id = self._current_edit_row
                self._save_combobox_value(row_id, col_index, val)

            elif isinstance(self._edit_widget, tk.Entry):
                val = self._edit_widget.get()
                col_index = self._current_edit_col_index
                row_id = self._current_edit_row
                self._save_entry_value(row_id, col_index, val)
        except:
            pass
    
        try:
            self._edit_widget.destroy()
        except:
            pass
        self._edit_widget = None
        
        
    def _finalize_entry_edit(self, entry, row_id, col_index):
        # This function is used by navigation bindings which are replaced by _start_edit_cell logic,
        # but kept for completeness if other bindings still use it.
        try:
            value = entry.get()
            
            # --- APPLY FIX 2 HERE TOO for redundancy ---
            if value.strip():
                 self.tree.set(row_id, self.REQUIRED_COLUMNS[col_index], value)
        except:
            pass
        try:
            entry.destroy()
        except:
            pass
        self._edit_widget = None        

    # --------------------------
    # Treeview UI Methods
    # --------------------------
    def _build_treeview(self):
        """Sets up the Treeview widget with required columns and scrollbars."""
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, background="white", fieldbackground="white")
        style.map("Treeview", background=[("selected", "#3498db")])

        container = tk.Frame(self.table_frame, bg="white")
        container.pack(fill="both", expand=True, padx=8, pady=8)

        self._tv_container = container

        self.tree = ttk.Treeview(
            container,
            columns=self.REQUIRED_COLUMNS,
            show="headings",
            selectmode="browse" 
        )

        for col in self.REQUIRED_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="w", minwidth=100, stretch=False)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Both vertical and horizontal scrollbars for Excel-like behavior
        self.vsb = ttk.Scrollbar(container, orient="vertical", command=self._on_vscroll)
        self.hsb = ttk.Scrollbar(container, orient="horizontal", command=self._on_hscroll)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Tags for styling
        self.tree.tag_configure("oddrow", background="#b3c6ff")
        self.tree.tag_configure("evenrow", background="#a6b8ff")
        self.tree.tag_configure("duplicate", background="#ff7f7f") # Red for Tally duplicates
        self.tree.tag_configure("balance_error", background="#ffcccc")  # light red
        self.tree.tag_configure("gst_error", background="#ffd9b3")
        
    def _on_vscroll(self, *args):
        """Handles vertical scrolling and repositions comboboxes."""
        self.tree.yview(*args)
        self._reposition_all_comboboxes()

    def _on_hscroll(self, *args):
        """Handles horizontal scrolling and repositions comboboxes."""
        self.tree.xview(*args)
        self._reposition_all_comboboxes()

    # --------------------------
    # Context Menu
    # --------------------------
    def _build_context_menu(self):
        """Creates the right-click context menu."""
        self.ctx_menu = tk.Menu(self.root, tearoff=0)
        self.ctx_menu.add_command(label="Add Blank Row", command=self.add_blank_row)
        self.ctx_menu.add_command(label="Delete Selected Row(s)", command=self.delete_selected_row)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Edit Cell", command=self._edit_selected_cell)
        self.ctx_menu.add_command(label="Auto-fit Columns", command=self.autofit_columns)
        self.tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Displays the context menu at the mouse position."""
        try:
            self.ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx_menu.grab_release()

    def _edit_selected_cell(self):
        """Starts editing the cell identified by selection and mouse position."""
        selected = self.tree.selection()
        if not selected:
            return
        row_id = selected[0]
        
        # Identify column based on mouse position
        col_id = self.tree.identify_column(self.tree.winfo_pointerx() - self.tree.winfo_rootx() - self.tree.winfo_x())
        if col_id:
            col_index = int(col_id.replace("#", "")) - 1
        else:
            col_index = 0 
        self._start_edit_cell(row_id, col_index)
        
    # --------------------------
    # Navigation & Edit Bindings (Tab/Arrows) - UPDATED WITH AUTO-SCROLL
    # --------------------------
    def _get_selected_cell_info(self):
        """
        Gets the currently selected row_id and determines the column index
        based on the last known edit index or the Treeview's internal focus.
        """
        selected = self.tree.selection()
        row_id = selected[0] if selected else None
        
        if not row_id:
             return None, 0

        # --- FIX: Use the currently stored edit index if available, otherwise try to identify from focus ---
        if self._current_edit_col_index is not None:
            col_index = self._current_edit_col_index
        else:
            # Fallback: Identify column based on where the mouse/focus might be (less reliable but necessary)
            col_id_str = self.tree.identify_column(self.tree.winfo_width() / 2) # Use center of treeview area
            
            if col_id_str and col_id_str.startswith("#"):
                col_index = int(col_id_str.replace("#", "")) - 1
            else:
                col_index = 0 # Default to the first column

        return row_id, col_index

    def _on_tab(self, event):
        """
        Excel सारखं - Tab दाबल्यावर next column वर जातो आणि 
        जर column visible नसेल तर scrollbar automatically shift होतो.
        Moves to the next cell and starts editing with smart scrolling.
        """
        
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"
        
        next_col_index = (col_index + 1) % len(self.REQUIRED_COLUMNS)
        
        # EXCEL BEHAVIOR: First ensure the column is visible
        self._ensure_column_visible(next_col_index)
        
        # Then start editing (with small delay for scroll to complete)
        self.root.after(30, lambda: self._start_edit_cell(row_id, next_col_index))
        return "break" # Stop the default Tab behavior

    def _on_shift_tab(self, event):
        """
        Excel सारखं - Shift+Tab दाबल्यावर previous column वर जातो आणि 
        जर column visible नसेल तर scrollbar automatically shift होतो.
        Moves to the previous cell and starts editing with smart scrolling.
        """
        
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"
        
        prev_col_index = (col_index - 1) % len(self.REQUIRED_COLUMNS)
        
        # EXCEL BEHAVIOR: First ensure the column is visible
        self._ensure_column_visible(prev_col_index)
        
        # Then start editing (with small delay for scroll to complete)
        self.root.after(30, lambda: self._start_edit_cell(row_id, prev_col_index))
        return "break"

    def _on_right_arrow(self, event):
        """
        Excel-like behavior:
        Moves the cursor to the next column in the same row.
        Automatically scrolls horizontally if the column is not visible.
        """
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"

        # Calculate next column index
        next_col_index = (col_index + 1) % len(self.cols)

        # Ensure the target column is visible
        self._ensure_column_visible(next_col_index)

        # Start editing the next cell after a short delay
        self.root.after(
            30,
            lambda: self._start_edit_cell(row_id, next_col_index)
        )
        return "break"

    
    def _on_left_arrow(self, event):
        """
        Excel-like behavior:
        Moves the cursor to the previous column in the same row.
        Automatically scrolls horizontally if the column is not visible.
        """
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"

        # Calculate previous column index
        prev_col_index = (col_index - 1) % len(self.cols)

        # Ensure the target column is visible
        self._ensure_column_visible(prev_col_index)

        # Start editing the previous cell after a short delay
        self.root.after(
            30,
            lambda: self._start_edit_cell(row_id, prev_col_index)
        )
        return "break"

        
    
    def _on_down_arrow(self, event):
        """
        Excel-like behavior:
        Pressing Down Arrow moves to the same column in the next row.
        If the next row is not visible, the Treeview scrolls automatically.
        """
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"

        # Get the next row
        next_row = self.tree.next(row_id)
        if next_row:
            # Select the next row
            self.tree.selection_set(next_row)

            # Ensure the row is visible (auto-scroll)
            self._ensure_row_visible(next_row)

            # Start editing the cell after scroll completes
            self.root.after(
                50,
                lambda: self._start_edit_cell(next_row, col_index)
            )
        return "break"


    def _on_up_arrow(self, event):
        """
        Excel-like behavior:
        Pressing Up Arrow moves to the same column in the previous row.
        If the previous row is not visible, the Treeview scrolls automatically.
        """
        row_id, col_index = self._get_selected_cell_info()
        if not row_id:
            return "break"

        # Get the previous row
        prev_row = self.tree.prev(row_id)
        if prev_row:
            # Select the previous row
            self.tree.selection_set(prev_row)

            # Ensure the row is visible (auto-scroll)
            self._ensure_row_visible(prev_row)

            # Start editing the cell after scroll completes
            self.root.after(
                50,
                lambda: self._start_edit_cell(prev_row, col_index)
            )
        return "break"

        
    # --------------------------
    # Editing System Core Logic
    # --------------------------
    def _on_double_click(self, event):
        """Starts editing on double click."""
        if self.tree.identify("region", event.x, event.y) != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if not row_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        self._start_edit_cell(row_id, col_index)

    def _start_edit_cell(self, row_id, col_index):
        """
        Initializes editing for the specified cell, handling widget destruction 
        and value saving of the *previous* active widget.
        """
        
        # --- Save and destroy the previous active widget (Entry or Combobox) ---
        if self._edit_widget:
             
             # 1. Save Combobox value
             if isinstance(self._edit_widget, ttk.Combobox): 
                 try:
                     # Check if the widget is alive before calling get()
                     val = self._edit_widget.get()
                     self._save_combobox_value(self._current_edit_row, self._current_edit_col_index, val)
                 except tk.TclError:
                    pass 
             
             # 2. Save Entry value
             elif isinstance(self._edit_widget, tk.Entry):
                 try:
                     self._save_entry_value(self._current_edit_row, self._current_edit_col_index, self._edit_widget.get())
                 except tk.TclError:
                     pass
                 
             # 3. Destroy the widget
             try:
                 self._edit_widget.destroy()
             except tk.TclError:
                 pass # Widget might have been destroyed by focus out handler

             self._edit_widget = None
        # -------------------------------------------------------------------------
        
        col_name = self.REQUIRED_COLUMNS[col_index]
        # 🔒 LOCK OPENING BALANCE COLUMN (NO EDIT ALLOWED)
        if col_name == "*OPENING BALANCE":
            return        
        
        # Store current editing position
        self._current_edit_row = row_id
        self._current_edit_col_index = col_index
        self.tree.selection_set(row_id) 
        
        # --- FIX: Set focus on the row for navigation continuity ---
        self.tree.focus(row_id)
        # ----------------------------------------------------------

        # --- Get BBOX ---
        col_id = f"#{col_index+1}"
        bbox = self.tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox
        # --------------------------------

        # Check if a Combobox is required for this column
        is_dropdown_col = col_name in self.DROPDOWN_COLUMNS and (self._tally_connected or col_name != "TYPE / GROUP (Names As Per Tally)")
        
        if is_dropdown_col:
            # 1. Ensure comboboxes are created for this row
            if row_id not in self.item_comboboxes or col_name not in self.item_comboboxes[row_id]:
                self._create_comboboxes_for_item(row_id)
            
            # 2. Position the combobox
            self._position_combobox_for_col(row_id, col_name)

            cb = self.item_comboboxes.get(row_id, {}).get(col_name)
            if cb:
                # *** FIX: Check if the widget exists before interacting ***
                if cb.winfo_exists(): 
                    try:
                        # Focus and open the dropdown if the widget is visible
                        if cb.winfo_ismapped():
                            cb.focus_set()
                        
                        self._edit_widget = cb # Track Combobox as the active edit widget
                        # Open dropdown after a short delay
                        self.root.after(100, lambda: self._open_combobox_dropdown(cb))
                    except tk.TclError:
                        pass
            return

        # Regular Text-Entry Editing
        value = self.tree.set(row_id, col_name)

        entry = tk.Entry(self.tree, relief="flat")
        entry.insert(0, value)
        
        # Calculate position relative to the Treeview container
        tree_x = self.tree.winfo_x()
        tree_y = self.tree.winfo_y()
        entry.place(x=tree_x + x, y=tree_y + y, width=width, height=height)

        entry.focus_set()
        entry.select_range(0, tk.END)
        self._edit_widget = entry

        # --- Entry Bindings ---
        def on_exit(event, should_navigate=False):
            """Saves value, destroys entry, and optionally navigates."""
            if self._edit_widget == entry: # Only run if this entry is still active
                try:
                    # _save_entry_value will handle the blank check now
                    self._save_entry_value(row_id, col_index, entry.get())
                    entry.destroy()
                    self._edit_widget = None
                    # IMPORTANT: Do NOT set self._current_edit_row/col_index to None here
                    # The navigation logic needs it for the next step.
                except tk.TclError:
                    pass # Ignore if already destroyed

            if should_navigate:
                # Handle navigation (Tab/Shift-Tab/Up/Down)
                if event.keysym == "Tab" or event.keysym == "Right":
                    self._on_tab(event)
                elif event.keysym == "Shift_L" or event.keysym == "Left":
                    self._on_shift_tab(event)
                elif event.keysym == "Down":
                    self._on_down_arrow(event)
                elif event.keysym == "Up":
                    self._on_up_arrow(event)
            return "break"

        # Focus lost (clicking away)
        entry.bind("<FocusOut>", lambda e: on_exit(e, should_navigate=False))
        
        entry.bind("<Return>", lambda e: on_exit(e, should_navigate=False))
        # Navigation keys destroy the entry, save value, and then call navigation logic
        entry.bind("<Tab>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Shift-Tab>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Right>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Left>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Down>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Up>", lambda e: on_exit(e, should_navigate=True))
        entry.bind("<Escape>", lambda e: entry.destroy())

    # --- FIX 2 APPLIED HERE ---
    def _save_entry_value(self, row_id, col_index, val):
        """Save Entry text to Treeview cell and AutoFit column."""

        col_name = self.REQUIRED_COLUMNS[col_index]

        # ✅ ALLOW BLANK (important for Debit / Credit delete)
        self.tree.set(row_id, col_name, val.strip())

        # AutoFit only this column
        self._autofit_single_column(col_name)
        
        self._on_data_changed()
        
        # validate ledger if needed
        if col_name == "*LEDGER NAME":
            self._validate_single_row(row_id)



    def _save_combobox_value(self, row_id, col_index, val):
        """Save Combobox selection and AutoFit column."""
        
        col_name = self.REQUIRED_COLUMNS[col_index]
        self.tree.set(row_id, col_name, val)

        # AutoFit this column
        self._autofit_single_column(col_name)
        self._on_data_changed()

    def _autofit_single_column(self, col_name):
        """AutoFit only one column for better performance."""
        import tkinter.font as tkfont
        style = ttk.Style()

        font = tkfont.Font(font=style.lookup("Treeview", "font"))

        # header width
        max_width = font.measure(col_name) + 30

        # rows
        for item in self.tree.get_children():
            txt = self.tree.set(item, col_name)
            if txt:
                w = font.measure(txt) + 30
                if w > max_width:
                    max_width = w

        # minimum
        if max_width < 120:
            max_width = 120

        # Apply width
        self.tree.column(col_name, width=int(max_width), minwidth=120, stretch=False)

        # update visuals
        self.tree.update_idletasks()
        self._reposition_all_comboboxes()
        self._on_data_changed()
    def _open_combobox_dropdown(self, cb):
        """Simulates a click to open the Combobox dropdown."""
        try:
            cb.event_generate('<Button-1>')
        except Exception:
            pass

    # --------------------------
    # Row Operations
    # --------------------------
    def add_blank_row(self):
        """Adds a new blank row to the Treeview and starts editing the first cell."""
        values = ["" for _ in self.REQUIRED_COLUMNS]
        item = self.tree.insert("", "end", values=values)
        self._apply_striped_colors()
        
        self.tree.see(item) # Make sure the new row is visible

        self._create_comboboxes_for_item(item)
        
        # Select and start editing the new row immediately
        self.tree.selection_set(item)
        self._start_edit_cell(item, 0)
        self._on_data_changed()        
        return item

    def delete_selected_row(self):
        """Deletes all selected rows and cleans up associated combobox widgets."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete Row", "Please select one or more rows to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} selected row(s)?"):
            return

        # Clean up active edit widget if the row is being deleted
        if self._edit_widget and self._current_edit_row in selected:
             try: self._edit_widget.destroy()
             except: pass
             self._edit_widget = None

        for it in selected:
            # Destroy and remove associated comboboxes
            cbs = self.item_comboboxes.pop(it, {})
            for cb in cbs.values():
                try:
                    cb.destroy()
                except:
                    pass
            self.tree.delete(it)

        self._apply_striped_colors()
        self._reposition_all_comboboxes()
        self._current_edit_row = None
        self._current_edit_col_index = None
        self._on_data_changed()
        

    # --------------------------
    # Excel Import 
    # --------------------------
    def import_excel(self):
        """Opens a file dialog to import data from an Excel file."""
        path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")]
        )
        if not path:
            return

        try:
            df = pd.read_excel(path, dtype=str)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read Excel file: {e}")
            return

        df_cols = [str(c).strip() for c in df.columns]
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df_cols]

        if missing:
            messagebox.showerror("Format Error", 
                                 f"The Excel file is missing the following required columns:\n\n{'\n'.join(missing)}")
            return

        # Only use the required columns in the correct order
        df = df[self.REQUIRED_COLUMNS]

        for _, row in df.iterrows():
            vals = ["" if pd.isna(row[c]) else str(row[c]) for c in self.REQUIRED_COLUMNS]
            item = self.tree.insert("", "end", values=vals)
            self._create_comboboxes_for_item(item) 

        self._apply_striped_colors()
        self._reposition_all_comboboxes()
        
        
        # Auto-fit columns after import
        self.root.after(100, self.autofit_columns)
        self._on_data_changed()
        messagebox.showinfo("Import Success", f"Successfully appended {len(df)} rows from Excel.")

    # --------------------------
    # Combobox per row: creation & positioning
    # --------------------------
    def _create_comboboxes_for_item(self, item_id):
        """Creates/updates all necessary comboboxes for a given row item_id."""
        if item_id not in self.item_comboboxes:
            self.item_comboboxes[item_id] = {}

        for col_name, options in self.DROPDOWN_COLUMNS.items():
            
            # Skip Tally Groups if not connected
            if col_name == "TYPE / GROUP (Names As Per Tally)" and not self._tally_connected:
                continue
                
            # Set dynamic options (Tally Groups)
            if col_name == "TYPE / GROUP (Names As Per Tally)":
                 current_options = self.parent_groups
            else:
                 current_options = options
            
            # Destroy old combobox before creating new one
            old = self.item_comboboxes[item_id].pop(col_name, None)
            if old:
                try: 
                    old.destroy()
                except: 
                    pass # Ignore if already destroyed

            # Create the combobox widget
            cb = ttk.Combobox(self._tv_container, values=current_options, state="readonly")
            cb.configure(width=20)
            
            def on_select(event, name=col_name, item=item_id, combobox=cb):
                """Callback when an option is selected from the dropdown."""
                val = combobox.get()
                self.tree.set(item, name, val)
                self._edit_widget = None
                
                # Navigate to the next column immediately after selection
                try:
                    col_index = self.REQUIRED_COLUMNS.index(name)
                    # Use a short delay to allow the Combobox to fully close before navigating
                    self.root.after(1, lambda: self._start_edit_cell(item, (col_index + 1) % len(self.REQUIRED_COLUMNS)))
                except ValueError:
                    pass

            cb.bind("<<ComboboxSelected>>", on_select)
            
            self.item_comboboxes[item_id][col_name] = cb

            # Set current value
            current = self.tree.set(item_id, col_name)
            if current:
                try: cb.set(current)
                except: pass

            self._position_combobox_for_col(item_id, col_name)

    def _position_combobox_for_col(self, item_id, col_name):
        """Places a combobox widget over its corresponding cell."""
        cb = self.item_comboboxes.get(item_id, {}).get(col_name)
        if not cb: return
            
        try:
            col_index = self.REQUIRED_COLUMNS.index(col_name)
        except ValueError:
            return 
            
        col_id = f"#{col_index+1}"
        bbox = self.tree.bbox(item_id, col_id)
        
        if not bbox:
            try: cb.place_forget()
            except: pass
            return
            
        x, y, width, height = bbox
        tree_x = self.tree.winfo_x()
        tree_y = self.tree.winfo_y()
        
        try:
            # Place the widget relative to the container frame
            cb.place(x=tree_x + x, y=tree_y + y, width=width, height=height)
        except Exception:
            # Fallback (less reliable)
            try: cb.place(x=x, y=y, width=width, height=height)
            except: pass

    def _reposition_all_comboboxes(self):
        """Recalculates and repositions all active comboboxes (called on scroll/resize)."""
        
        items_to_delete = []
        # Cleanup: Remove comboboxes for rows that no longer exist
        for item in self.item_comboboxes.keys():
            if item not in self.tree.get_children():
                items_to_delete.append(item)
                
        for item in items_to_delete:
            cbs = self.item_comboboxes.pop(item, {})
            for cb in cbs.values():
                try: cb.destroy()
                except: pass
        
        # Position the remaining active comboboxes
        for item in self.tree.get_children():
            # Recreate/Update comboboxes if needed (e.g., Tally connected/disconnected)
            if item not in self.item_comboboxes or self._tally_connected:
                self._create_comboboxes_for_item(item) 

            for col_name in self.item_comboboxes.get(item, {}).keys():
                self._position_combobox_for_col(item, col_name)

    # --------------------------
    # Helpers (Color, Tally Connect, Validation)
    # --------------------------
    def _apply_striped_colors(self):
        """Applies alternating row background colors (striping), avoiding error rows."""
        non_striped_items = []

        # Separate rows which should get striping
        for item in self.tree.get_children():
            current_tags = list(self.tree.item(item, "tags"))

            # ❌ Error rows ला striping लागू करू नको
            if (
                "duplicate" in current_tags or
                "gst_error" in current_tags or
                "balance_error" in current_tags
            ):
                # Remove old striping if present, keep other tags
                self.tree.item(
                    item,
                    tags=tuple(t for t in current_tags if t not in ("oddrow", "evenrow"))
                )
            else:
                non_striped_items.append(item)
                # Remove old striping tags
                self.tree.item(
                    item,
                    tags=tuple(t for t in current_tags if t not in ("oddrow", "evenrow"))
                )

        # Apply new striping only to valid rows
        for i, item in enumerate(non_striped_items):
            current_tags = list(self.tree.item(item, "tags"))
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            current_tags.append(tag)
            self.tree.item(item, tags=tuple(current_tags))

            
            


    # --------------------------
    # Tally Connection & Fetch
    # --------------------------
    def connect_to_tally(self):
        """Attempts to connect to Tally and fetch Ledgers and Groups."""
        from tkinter import messagebox

        # ---------- PRE-CHECK : Is Tally running & company open ----------
        if not self._is_tally_running():
            messagebox.showwarning(
                "Tally Not Available",
                "Tally is not running or no company is open.\n\n"
                "Please open Tally and load a company before connecting."
            )
            return

        try:
            # Fetch data from Tally
            self._fetch_ledgers()
            self._fetch_parent_groups()

            self._tally_connected = True
            self.btn_tally.configure(text="🔌 Tally Connected ✓")

            self._validation_passed = False
            self.btn_create_xml.pack_forget()
            
            messagebox.showinfo(
                "Tally Connected",
                "Successfully connected to Tally.\n\n"
                "Ledgers and Parent Groups have been loaded."
            )

            # Recreate comboboxes to include Tally Groups
            for item in self.tree.get_children():
                self._create_comboboxes_for_item(item)

            self._reposition_all_comboboxes()

        except Exception:
            # Friendly error (no raw exception)
            messagebox.showerror(
                "Tally Connection Failed",
                "Unable to retrieve data from Tally.\n\n"
                "Please make sure:\n"
                "• Tally is running\n"
                "• A company is open\n"
                "• Tally port 9000 is enabled"
            )

            self._tally_connected = False
            self.btn_tally.configure(text="🔌 Connect to Tally")

            # Clean up Tally-dependent Comboboxes
            for item, cbs in self.item_comboboxes.items():
                if "TYPE / GROUP (Names As Per Tally)" in cbs:
                    cb = cbs.pop("TYPE / GROUP (Names As Per Tally)")
                    try:
                        cb.destroy()
                    except:
                        pass

            self._reposition_all_comboboxes()


    def _fetch_ledgers(self):
        """
        Fetch only ledger names from Tally via a Collection request.
        """
        envelope = """<ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Ledger Coll</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES>
                <SVEXPORTFORMAT>$SysName:XML</SVEXPORTFORMAT>
              </STATICVARIABLES>
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="Ledger Coll" ISMODIFY="No">
                    <TYPE>Ledger</TYPE>
                    <NATIVEMETHOD>NAME</NATIVEMETHOD>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>""".encode("utf-8")

        r = requests.post("http://127.0.0.1:9000", data=envelope, headers={"Content-Type": "text/xml"}, timeout=5)
        r.raise_for_status()
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(r.text.encode("utf-8", "ignore"), parser=parser)

        names = []
        for tag in root.iter():
            if tag.tag.upper() == "NAME" and tag.text:
                names.append(tag.text.strip())
        self.tally_ledgers = sorted(set(names))

    def _fetch_parent_groups(self):
        """
        Fetch Group names (ParentGroupList) from Tally.
        """
        envelope = """<ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>ParentGroupColl</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="ParentGroupColl" ISMODIFY="No">
                                <TYPE>Group</TYPE>
                                <NATIVEMETHOD>NAME</NATIVEMETHOD>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>""".encode("utf-8")

        r = requests.post("http://127.0.0.1:9000", data=envelope, headers={"Content-Type": "text/xml"}, timeout=5)
        r.raise_for_status()
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(r.text.encode("utf-8", "ignore"), parser=parser)

        names = []
        for tag in root.iter():
            if tag.tag.upper() == "NAME" and tag.text:
                names.append(tag.text.strip())
        self.parent_groups = sorted(set(names))
        

    # --------------------------
    # Single Row Validation (Duplicate check while typing)
    # --------------------------
    def _validate_single_row(self, item):
        if not self.tally_ledgers:
            return

        ledger_name = (self.tree.set(item, "*LEDGER NAME") or "").strip()
        ledger_set = set(n.strip().lower() for n in self.tally_ledgers)
        current_tags = list(self.tree.item(item, "tags"))

        if ledger_name and ledger_name.lower() in ledger_set:
            if "duplicate" not in current_tags:
                current_tags = [t for t in current_tags if t not in ("oddrow", "evenrow")]
                current_tags.append("duplicate")
        else:
            if "duplicate" in current_tags:
                current_tags.remove("duplicate")

        self.tree.item(item, tags=tuple(current_tags))
        self._apply_striped_colors()


    # --------------------------
    # STEP-5 Helper:
    # Debit / Credit → Opening Balance
    # --------------------------
    def _sync_opening_balance_from_dr_cr(self, item):
        debit = (self.tree.set(item, "DEBIT BALANCE") or "").strip()
        credit = (self.tree.set(item, "CREDIT BALANCE") or "").strip()

        def to_float(v):
            try:
                return float(v)
            except:
                return None

        d = to_float(debit)
        c = to_float(credit)

        # both empty
        if not debit and not credit:
            self.tree.set(item, "*OPENING BALANCE", "")
            return

        # debit → negative opening
        if d is not None and not credit:
            self.tree.set(item, "*OPENING BALANCE", f"-{abs(d)}")
            return

        # credit → positive opening
        if c is not None and not debit:
            self.tree.set(item, "*OPENING BALANCE", f"{abs(c)}")
            return

    def validate_ledgers(self):
        import re
        from tkinter import messagebox

        # --------------------------
        # Check Tally Connection (NO AUTO CONNECT)
        # --------------------------
        if not self._tally_connected or not self.tally_ledgers:
            messagebox.showwarning(
                "Validation",
                "Tally is not connected.\nPlease click 'Connect to Tally' first."
            )
            return


    def _is_tally_running(self):
        """
        Checks whether Tally is running and a company is open.
        """
        import requests

        try:
            r = requests.get("http://127.0.0.1:9000", timeout=2)
            return r.status_code == 200
        except:
            return False
    def _on_data_changed(self):
        if getattr(self, "_validation_passed", False):
            self._validation_passed = False
            self.btn_create_xml.pack_forget()

    def create_xml(self):
        import os
        from datetime import datetime
        from tkinter import messagebox

        if not self._validation_passed:
            messagebox.showwarning("XML", "Please validate data before creating XML")
            return

        def xs(v):
            """XML safe"""
            if not v:
                return ""
            return (
                str(v)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .strip()
            )

        company = self.company_name or "COMPANY"
        ts = datetime.now().strftime("%d%m%Y%H%M%S")

        folder = os.path.join(os.path.expanduser("~"), "Desktop", "Tally_XML")
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"LEDGER_{ts}.xml")

        xml = []
        xml.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml.append("<ENVELOPE>")
        xml.append(" <HEADER>")
        xml.append("  <TALLYREQUEST>Import Data</TALLYREQUEST>")
        xml.append(" </HEADER>")
        xml.append(" <BODY>")
        xml.append("  <IMPORTDATA>")
        xml.append("   <REQUESTDESC>")
        xml.append("    <REPORTNAME>All Masters</REPORTNAME>")
        xml.append("    <STATICVARIABLES>")
        xml.append(f"     <SVCURRENTCOMPANY>{xs(company)}</SVCURRENTCOMPANY>")
        xml.append("    </STATICVARIABLES>")
        xml.append("   </REQUESTDESC>")
        xml.append("   <REQUESTDATA>")

        for item in self.tree.get_children():
            g = lambda c: xs(self.tree.set(item, c))

            xml.append('    <TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml.append(f'     <LEDGER NAME="{g("*LEDGER NAME")}" RESERVEDNAME="">')

            # ---------------- ADDRESS (Legacy – optional) ----------------
            xml.append('      <ADDRESS.LIST TYPE="String">')
            xml.append(f'       <ADDRESS>{g("ADDRESS (Bldg / No)")}</ADDRESS>')
            xml.append(f'       <ADDRESS>{g("ADDRESS (Road / Area)")}</ADDRESS>')
            xml.append(f'       <ADDRESS>{g("ADDRESS (City)")}</ADDRESS>')
            xml.append('      </ADDRESS.LIST>')

            xml.append('      <MAILINGNAME.LIST TYPE="String">')
            xml.append(f'       <MAILINGNAME>{g("*LEDGER NAME")}</MAILINGNAME>')
            xml.append('      </MAILINGNAME.LIST>')

            # ---------------- BASIC ----------------
            xml.append(f'      <EMAIL>{g("EMAIL ID - 1")}</EMAIL>')
            xml.append(f'      <PINCODE>{g("ADDRESS (Pin)")}</PINCODE>')
            xml.append(f'      <INCOMETAXNUMBER>{g("IT PAN")}</INCOMETAXNUMBER>')
            xml.append(f'      <INTERSTATESTNUMBER>{g("CST NO")}</INTERSTATESTNUMBER>')
            xml.append(f'      <VATTINNUMBER>{g("VAT NO")}</VATTINNUMBER>')
            xml.append(f'      <COUNTRYNAME>{g("ADDRESS (Country)")}</COUNTRYNAME>')
            xml.append(f'      <GSTREGISTRATIONTYPE>{g("*GST REG. TYPE")}</GSTREGISTRATIONTYPE>')
            xml.append(f'      <VATDEALERTYPE>{g("*GST REG. TYPE")}</VATDEALERTYPE>')
            xml.append(f'      <PARENT>{g("TYPE / GROUP (Names As Per Tally)")}</PARENT>')
            xml.append(f'      <BILLCREDITPERIOD>{g("BILL CREDIT PERIOD")}</BILLCREDITPERIOD>')
            xml.append(f'      <COUNTRYOFRESIDENCE>{g("ADDRESS (Country)")}</COUNTRYOFRESIDENCE>')
            xml.append(f'      <EMAILCC>{g("ADDRESS (Country)")}</EMAILCC>')
            xml.append('      <LEDGERPHONE></LEDGERPHONE>')
            xml.append(f'      <LEDGERFAX>{g("FAX NUMBER")}</LEDGERFAX>')
            xml.append('      <LEDGERCONTACT>Authorise Person</LEDGERCONTACT>')
            xml.append(f'      <LEDGERMOBILE>{g("MOBILE NUMBER")}</LEDGERMOBILE>')
            xml.append(f'      <PARTYGSTIN>{g("GST REG. GSTIN / UIN")}</PARTYGSTIN>')
            xml.append('      <REGISTRATIONNUMBER></REGISTRATIONNUMBER>')
            xml.append(f'      <LEDSTATENAME>{g("*ADDRESS (State)")}</LEDSTATENAME>')
            xml.append(f'      <PARTYBUSINESSSTYLE>{g("*LEDGER NAME")}</PARTYBUSINESSSTYLE>')
            xml.append(f'      <ISBILLWISEON>{g("BILL WISE")}</ISBILLWISEON>')
            xml.append(f'      <ISCOSTCENTRESON>{g("COST CENTRE")}</ISCOSTCENTRESON>')
            xml.append(f'      <AFFECTSSTOCK>{g("INVENTORY EFFECT")}</AFFECTSSTOCK>')
            xml.append('      <ISINTERESTON>No</ISINTERESTON>')
            xml.append('      <ASORIGINAL>Yes</ASORIGINAL>')
            xml.append('      <ISAGAINSTFORMC>Yes</ISAGAINSTFORMC>')
            xml.append('      <ISCHEQUEPRINTINGENABLED>Yes</ISCHEQUEPRINTINGENABLED>')

            # ---------------- OPENING ----------------
            xml.append(f'      <OPENINGBALANCE>{g("*OPENING BALANCE")}</OPENINGBALANCE>')

            xml.append('      <LANGUAGENAME.LIST>')
            xml.append('       <NAME.LIST TYPE="String">')
            xml.append(f'        <NAME>{g("*LEDGER NAME")}</NAME>')
            xml.append(f'        <NAME>{g("*ALIAS")}</NAME>')
            xml.append('       </NAME.LIST>')
            xml.append('      </LANGUAGENAME.LIST>')

            xml.append('      <BILLALLOCATIONS.LIST>')
            xml.append('       <ISADVANCE>No</ISADVANCE>')
            xml.append(f'       <OPENINGBALANCE>{g("*OPENING BALANCE")}</OPENINGBALANCE>')
            xml.append('      </BILLALLOCATIONS.LIST>')

            # ---------------- GST DETAILS ----------------
            xml.append('      <LEDGSTREGDETAILS.LIST>')
            xml.append('       <APPLICABLEFROM>20220601</APPLICABLEFROM>')
            xml.append(f'       <GSTREGISTRATIONTYPE>{g("*GST REG. TYPE")}</GSTREGISTRATIONTYPE>')
            xml.append(f'       <PLACEOFSUPPLY>{g("*ADDRESS (State)")}</PLACEOFSUPPLY>')
            xml.append(f'       <GSTIN>{g("GST REG. GSTIN / UIN")}</GSTIN>')
            xml.append('       <ISOTHTERRITORYASSESSEE>No</ISOTHTERRITORYASSESSEE>')
            xml.append('       <CONSIDERPURCHASEFOREXPORT>No</CONSIDERPURCHASEFOREXPORT>')
            xml.append('       <ISTRANSPORTER>No</ISTRANSPORTER>')
            xml.append('       <ISCOMMONPARTY>No</ISCOMMONPARTY>')
            xml.append('      </LEDGSTREGDETAILS.LIST>')

            # ---------------- MAILING DETAILS (MAIN ADDRESS USED BY TALLY) ----------------
            xml.append('      <LEDMAILINGDETAILS.LIST>')
            xml.append('       <APPLICABLEFROM>20220601</APPLICABLEFROM>')
            xml.append(f'       <MAILINGNAME>{g("*LEDGER NAME")}</MAILINGNAME>')
            xml.append('       <ADDRESS.LIST TYPE="String">')
            xml.append(f'        <ADDRESS>{g("ADDRESS (Bldg / No)")}</ADDRESS>')
            xml.append(f'        <ADDRESS>{g("ADDRESS (Road / Area)")}</ADDRESS>')
            xml.append(f'        <ADDRESS>{g("ADDRESS (City)")}</ADDRESS>')
            xml.append('       </ADDRESS.LIST>')
            xml.append(f'       <STATE>{g("*ADDRESS (State)")}</STATE>')
            xml.append(f'       <PINCODE>{g("ADDRESS (Pin)")}</PINCODE>')
            xml.append(f'       <COUNTRY>{g("ADDRESS (Country)")}</COUNTRY>')
            xml.append('      </LEDMAILINGDETAILS.LIST>')

            xml.append('     </LEDGER>')
            xml.append('    </TALLYMESSAGE>')

        xml.append("   </REQUESTDATA>")
        xml.append("  </IMPORTDATA>")
        xml.append(" </BODY>")
        xml.append("</ENVELOPE>")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(xml))

        messagebox.showinfo(
            "XML Created",
            f"Ledger XML created successfully:\n{file_path}"
        )






    # --------------------------
    # MAIN VALIDATION FUNCTION
    # --------------------------
    def validate_ledgers(self):
        """
        Runs ALL validations in one click:
        1. Duplicate Ledger (Tally + Internal Treeview)
        2. GST validation + State auto fill
        3. YES / NO normalize
        4. Debit / Credit validation
        5. Opening Balance auto sync
        + Extra XML / Group / GST-Type rules
        """
        import re
        from tkinter import messagebox

        # --------------------------
        # Check Tally Connection
        # --------------------------
        if not self._tally_connected or not self.tally_ledgers:
            messagebox.showwarning(
                "Validation",
                "Tally is not connected.\nPlease click 'Connect to Tally' first."
            )
            return

        # --------------------------
        # Ensure Parent Groups Loaded
        # --------------------------
        if not hasattr(self, "parent_groups"):
            try:
                self._fetch_parent_groups()
            except Exception:
                self.parent_groups = []

        # --------------------------
        # GST STATE MAP
        # --------------------------
        gst_state_map = {
            "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
            "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
            "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
            "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
            "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
            "16": "Tripura", "17": "Meghalaya", "18": "Assam",
            "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
            "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
            "25": "Daman & Diu", "26": "Dadra & Nagar Haveli",
            "27": "Maharashtra", "28": "Andhra Pradesh (Old)",
            "29": "Karnataka", "30": "Goa", "31": "Lakshadweep",
            "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
            "35": "Andaman & Nicobar Islands", "36": "Telangana",
            "37": "Andhra Pradesh (New)", "38": "Ladakh",
            "97": "Other Territory", "99": "Centre Jurisdiction"
        }

        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}$'
        ledger_set = set(n.strip().lower() for n in self.tally_ledgers)

        duplicates = []
        gst_errors = []
        balance_errors = []
        ampersand_errors = []
        group_errors = []
        gst_type_errors = []

        # 🔹 NEW: Track internal Treeview ledger names
        entered_ledgers = {}

        def is_number(v):
            try:
                float(v)
                return True
            except:
                return False

        # --------------------------
        # ROW LOOP
        # --------------------------
        for item in self.tree.get_children():

            current_tags = list(self.tree.item(item, "tags"))

            ledger_name = (self.tree.set(item, "*LEDGER NAME") or "").strip()
            gst_reg_type = (self.tree.set(item, "*GST REG. TYPE") or "").strip()
            gst_number = (self.tree.set(item, "GST REG. GSTIN / UIN") or "").strip()
            group_val = (self.tree.set(item, "TYPE / GROUP (Names As Per Tally)") or "").strip()

            lname = ledger_name.lower()

            # ----- XML (&) CHECK -----
            if "&" in ledger_name:
                if "xml_error" not in current_tags:
                    current_tags.append("xml_error")
                ampersand_errors.append(item)

            # ----- GROUP VALIDATION -----
            if group_val and hasattr(self, "parent_groups") and group_val not in self.parent_groups:
                if "group_error" not in current_tags:
                    current_tags.append("group_error")
                group_errors.append(item)

            # ----- DUPLICATE (TALLY + TREEVIEW) -----
            if lname:
                entered_ledgers.setdefault(lname, []).append(item)

            if "duplicate" in current_tags:
                current_tags.remove("duplicate")

            if lname and lname in ledger_set:
                current_tags.append("duplicate")
                duplicates.append(item)

            # ----- GST VALIDATION -----
            clean_gst = (
                gst_number.replace("🔴 ", "")
                .replace("[REQUIRED]", "")
                .replace("[Invalid Format]", "")
                .strip()
            )

            gst_reg_type_clean = gst_reg_type.lower().strip()

            if (clean_gst or len(clean_gst) >= 10) and gst_reg_type_clean in ("", "unregistered"):
                if "gst_type_error" not in current_tags:
                    current_tags.append("gst_type_error")
                gst_type_errors.append(item)

            if gst_reg_type_clean in ("regular", "composition"):
                if not clean_gst:
                    self.tree.set(item, "GST REG. GSTIN / UIN", "🔴 [REQUIRED]")
                    if "gst_error" not in current_tags:
                        current_tags.append("gst_error")
                    gst_errors.append(item)

                elif not re.match(gst_pattern, clean_gst.upper()):
                    self.tree.set(
                        item,
                        "GST REG. GSTIN / UIN",
                        f"🔴 {clean_gst} [Invalid Format]"
                    )
                    if "gst_error" not in current_tags:
                        current_tags.append("gst_error")
                    gst_errors.append(item)

                else:
                    self.tree.set(item, "GST REG. GSTIN / UIN", clean_gst.upper())
                    current_tags = [t for t in current_tags if t != "gst_error"]

                    state = gst_state_map.get(clean_gst[:2])
                    if state:
                        self.tree.set(item, "*ADDRESS (State)", state)
            else:
                current_tags = [t for t in current_tags if t != "gst_error"]

            # ----- YES / NO -----
            for col in ("BILL WISE", "INVENTORY EFFECT", "COST CENTRE"):
                val = (self.tree.set(item, col) or "").strip().lower()
                self.tree.set(item, col, "Yes" if val == "yes" else "No")

            # ----- DEBIT / CREDIT -----
            debit = (self.tree.set(item, "DEBIT BALANCE") or "").strip()
            credit = (self.tree.set(item, "CREDIT BALANCE") or "").strip()

            if "balance_error" in current_tags:
                current_tags.remove("balance_error")

            error_found = False
            if debit and credit:
                error_found = True
            elif (debit and not is_number(debit)) or (credit and not is_number(credit)):
                error_found = True

            if error_found:
                current_tags.append("balance_error")
                balance_errors.append(item)
            else:
                self._sync_opening_balance_from_dr_cr(item)

            self.tree.item(item, tags=tuple(current_tags))

        # --------------------------
        # INTERNAL TREEVIEW DUPLICATES
        # --------------------------
        for lname, items in entered_ledgers.items():
            if len(items) > 1:
                for it in items:
                    tags = list(self.tree.item(it, "tags"))
                    if "duplicate" not in tags:
                        tags.append("duplicate")
                    self.tree.item(it, tags=tuple(tags))
                    duplicates.append(it)

        # --------------------------
        # UI UPDATE
        # --------------------------
        self._apply_striped_colors()
        self._reposition_all_comboboxes()

        # --------------------------
        # MESSAGE
        # --------------------------
        msgs = []

        if ampersand_errors:
            msgs.append("🔴 '&' not allowed in Ledger Name. Use 'AND'.")

        if group_errors:
            msgs.append("🔴 Invalid TYPE / GROUP found (not from choice list).")

        if gst_type_errors:
            msgs.append("🔴 GST Number entered but GST REG. TYPE is Unregistered / Empty.")

        # --------------------------
        # DUPLICATE MESSAGES (SEPARATE)
        # --------------------------
        tally_dup = []
        tree_dup = []

        for item in duplicates:
            ledger_name = (self.tree.set(item, "*LEDGER NAME") or "").strip().lower()
            if ledger_name in ledger_set:
                tally_dup.append(item)
            else:
                tree_dup.append(item)

        if tally_dup:
            msgs.append(
                "🔴 Ledger already created in Tally.\n"
                "Please change Ledger Name.\n"
                "Highlighted cells."
            )

        if tree_dup:
            msgs.append(
                "🔴 Duplicate Ledger Name found in list.\n"
                "Please change duplicate Ledger Name.\n"
                "Highlighted cells."
            )


        if gst_errors:
            msgs.append(f"🔴 {len(gst_errors)} GST error(s) found")

        if balance_errors:
            msgs.append("🔴 Debit / Credit issues found")

        if msgs:
            self._validation_passed = False
            self.btn_create_xml.pack_forget()
            messagebox.showwarning("Validation", "\n".join(msgs))
        else:
            self._validation_passed = True
            self.btn_create_xml.pack(side="left", padx=8)
            messagebox.showinfo("Validation", "✅ All validations passed")

            
            
            
            






class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D-SHIFT Bank PDF to Excel Converter")
        self.root.geometry("1200x700")
        # CTK handles the background for a cleaner look
        self.root.configure(bg=self.root.cget("background"))

        self.bank_var = tk.StringVar()
        self.pdf_path = ""
        self.data = pd.DataFrame()  # Changed to DataFrame to match show_table logic
        self.export_btn = None
        self.tally_btn = None
        self.pdf_password = None

        self.style = ttk.Style()
        self.setup_styles()
        self.create_widgets()

        # New Frame for Side-by-Side Bottom Action Buttons (Rounded)
        self.bottom_action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.bottom_action_frame.pack(side=tk.BOTTOM, pady=20)


    def setup_styles(self):
        """Define modern styles, mainly for TTK widgets (Treeview/Combobox)"""
        # We keep TTK styling only for non-CTK replaceable widgets (Treeview, Listbox)
        self.style.theme_use("clam")

        # --- Treeview Styles ---
        self.style.configure("Treeview.Heading",
                             font=("Arial", 12, "bold"),
                             background="#3498db",  # Blue header
                             foreground="white")
        self.style.configure("Treeview",
                             font=("Arial", 10),
                             rowheight=30,
                             background="white",
                             fieldbackground="white")
        self.style.map('Treeview',
                       background=[('selected', '#3498db')],
                       foreground=[('selected', 'white')])


    def create_widgets(self):
        """Create CTK widgets with rounded corners."""
        # Top Frame (Rounded, Transparent background)
        top_frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=12)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=15, padx=20)

        ctk.CTkLabel(top_frame, text="Select Bank:", font=ctk.CTkFont("Arial", 14)).pack(side=tk.LEFT, padx=(5, 10))

        # Autocomplete Combobox for bank selection (using TTK for logic)
        self.bank_menu = AutocompleteCombobox(top_frame, textvariable=self.bank_var, state="normal", width=40)
        self.bank_menu.set_completion_list([
            "HDFC Bank Limited", "Union Bank of India", "Bank of Maharashtra", "Central Bank of India",
            "NASIK MERCHANT CO-OP BANK LTD", "State Bank of India", "SVC Co-Op Bank","TJSB SAHAKARI BANK LTD",
            "Central Bank of India TEXT", "Axis Bank", "ICICI BANK LTD", "Kotak Mahindra Bank","Rajlaxmi Urban CO-OP Bank LTD",
            "Bandhan Bank", "Bank of Baroda", "Bank of India", "J K Excel format","HDFC Bank Limited Text","Abhyudaya Co-Operative Bank Limited",
            "CANARA BANK","COSMOS CO-OP BANK LTD","DCB BANK","IDBI BANK LTD","INDUSIND BANK LTD","Shree Mahesh Co-Op Bank Ltd","Punjab National Bank",
            "Saraswat Co-Operative Bank Ltd","test"
        ])


        self.bank_menu.current(0)
        self.bank_menu.pack(side=tk.LEFT, padx=10)

        # Buttons for Select PDF and Convert - CTK Buttons, highly rounded
        ctk.CTkButton(top_frame, text="Select PDF", command=self.load_pdf,
                      corner_radius=25, height=40, fg_color="#3498db", hover_color="#2980b9"
                      ).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(top_frame, text="Convert", command=self.convert_pdf,
                      corner_radius=25, height=40, fg_color="#27ae60", hover_color="#2ecc71"
                      ).pack(side=tk.LEFT, padx=10)

        # Middle section with PDF preview and Extracted table (Rounded Frames)
        middle_frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=12)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # --- PDF Preview Area ---
        # Using CTkFrame to replace LabelFrame, placing title above
        pdf_container = ctk.CTkFrame(middle_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#bdc3c7")
        pdf_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        ctk.CTkLabel(pdf_container, text="PDF Preview", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#2c3e50").pack(pady=(5,0))

        pdf_frame = ctk.CTkFrame(pdf_container, fg_color="transparent", corner_radius=0)
        pdf_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_pdf = tk.Canvas(pdf_frame, bg="white", highlightthickness=0)
        # Using CTK Scrollbar
        self.scroll_pdf_y = ctk.CTkScrollbar(pdf_frame, orientation="vertical", command=self.canvas_pdf.yview)
        self.scroll_pdf_x = ctk.CTkScrollbar(pdf_frame, orientation="horizontal", command=self.canvas_pdf.xview)

        self.scroll_pdf_y.pack(side="right", fill="y")
        self.scroll_pdf_x.pack(side="bottom", fill="x")
        self.canvas_pdf.pack(side="left", fill="both", expand=True)

        self.canvas_pdf.configure(
            yscrollcommand=self.scroll_pdf_y.set,
            xscrollcommand=self.scroll_pdf_x.set
        )
        self.pdf_images = []

        # --- Table for extracted data ---
        # Using CTkFrame to replace LabelFrame, placing title above
        table_container = ctk.CTkFrame(middle_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#bdc3c7")
        table_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        ctk.CTkLabel(table_container, text="Extracted Table", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#2c3e50").pack(pady=(5,0))

        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent", corner_radius=0)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ----------------- Treeview (TTK is best for tables) -----------------
        self.columns = ["Date", "Particulars", "Chq No", "Debit", "Credit", "Balance"]
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.columns,
            show="headings",
            height=10,
            selectmode="extended"
        )

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Bind Ctrl+A for select all
        self.tree.bind("<Control-a>", self.select_all_rows)
        self.tree.bind("<Control-A>", self.select_all_rows)

        # Scrollbars for table (Using TTK scrollbars next to TTK Treeview for compatibility)
        self.scroll_tree_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.scroll_tree_y.grid(row=0, column=1, sticky="ns")

        self.scroll_tree_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.scroll_tree_x.grid(row=1, column=0, sticky="ew")

        self.tree.configure(
            yscrollcommand=self.scroll_tree_y.set,
            xscrollcommand=self.scroll_tree_x.set
        )

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)


    def select_all_rows(self, event=None):
        """Select all rows in Treeview (Logic unchanged)"""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def load_pdf(self):
        """Select a PDF file (Logic unchanged)"""
        self.pdf_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not self.pdf_path:
            return

        try:
            doc = fitz.open(self.pdf_path)
        except fitz.fitz.FileDataError:
            # PDF is password protected
            self.ask_password()
            return

        if doc.needs_pass:
            self.ask_password()
        else:
            self.pdf_password = None
            self.show_pdf_preview()

    def ask_password(self):
        """Ask password if PDF is protected (Logic unchanged)"""
        while True:
            password = simpledialog.askstring("Password Required", "Enter PDF password:", show="*")
            if password is None:
                return
            try:
                doc = fitz.open(self.pdf_path)
                if doc.authenticate(password):
                    self.pdf_password = password
                    self.show_pdf_preview()
                    return
                else:
                    messagebox.showerror("Error", "Incorrect password. Try again.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {e}")
                return

    def show_pdf_preview(self):
        """Render PDF pages as images and show in canvas (Logic unchanged)"""
        self.canvas_pdf.delete("all")
        self.pdf_images.clear()

        if self.pdf_password:
            doc = fitz.open(self.pdf_path)
            if not doc.authenticate(self.pdf_password):
                messagebox.showerror("Error", "Invalid password for preview.")
                return
        else:
            doc = fitz.open(self.pdf_path)

        y = 0
        for page in doc:
            # Assuming Image, ImageTk, and fitz are properly imported/available
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)
            self.pdf_images.append(img_tk)
            self.canvas_pdf.create_image(10, y, anchor="nw", image=img_tk)
            y += pix.height + 10
        self.canvas_pdf.configure(scrollregion=self.canvas_pdf.bbox("all"))




    def convert_pdf(self):
        """Convert PDF to DataFrame based on bank selection (Logic unchanged)"""
        if not self.pdf_path:
            messagebox.showerror("Error", "PDF not selected.")
            return

        bank = self.bank_var.get().strip()
        try:
            # --- (PDF Parsing Logic - Unchanged method calls) ---
            if bank == "HDFC Bank Limited":
                self.data = self.parse_hdfc_pdf(self.pdf_path)
            elif bank == "Union Bank of India":
                self.data = self.parse_union_bank_pdf(self.pdf_path)
            elif bank == "Bank of Maharashtra":
                self.data = self.parse_bom_format(self.pdf_path)
            elif bank == "Central Bank of India":
                self.data = self.parse_central_bank_format(self.pdf_path)
            elif bank == "NASIK MERCHANT CO-OP BANK LTD":
                self.data = self.parse_namco_bank_text(self.pdf_path)
            elif bank == "State Bank of India":
                self.data = self.parse_sbi_bank_format(self.pdf_path)
            elif bank == "SVC Co-Op Bank":
                self.data = self.parse_svc_bank_format(self.pdf_path)
            elif bank == "Central Bank of India TEXT":
                self.data = self.parse_central_bank_formatTEXT(self.pdf_path)
            elif bank == "Axis Bank":
                self.data = self.parse_axis_bank_format(self.pdf_path)
            elif bank == "ICICI BANK LTD":
                self.data = self.parse_icici_pdf(self.pdf_path)
            elif bank == "Kotak Mahindra Bank":
                self.data = self.parse_kotak_bank_format(self.pdf_path)
            elif bank == "Bandhan Bank":
                self.data = self.parse_bandhan_bank_format(self.pdf_path)
            elif bank == "Bank of Baroda":
                self.data = self.parse_bob_format(self.pdf_path)
            elif bank == "Bank of India":
                self.data = self.parse_bank_of_india(self.pdf_path)
            elif bank == "J K Excel format":
                self.data = self.parse_bank_excel(self.pdf_path) 
            elif bank == "HDFC Bank Limited Text":
                self.data = self.parse_hdfc_format12(self.pdf_path)  
            
            elif bank == "Abhyudaya Co-Operative Bank Limited":
                self.data = self.parse_abhyudaya_bank_format(self.pdf_path)
                
            elif bank == "CANARA BANK":
                self.data = self.parse_canara_bank_format(self.pdf_path)  

            elif bank == "COSMOS CO-OP BANK LTD":
                self.data = self.parse_cosmos_bank_format(self.pdf_path)                
                            
            elif bank == "DCB BANK":
                self.data = self.parse_dcb_bank_format(self.pdf_path)

            elif bank == "IDBI BANK LTD":
                self.data = self.parse_idbi_bank_format(self.pdf_path)

            elif bank == "INDUSIND BANK LTD":
                self.data = self.parse_indusind_bank_format(self.pdf_path)
            
            elif bank == "Shree Mahesh Co-Op Bank Ltd":
                self.data = self.parse_mahesh_bank_format(self.pdf_path)
                
            elif bank == "Punjab National Bank":
                self.data = self.parse_pnb_bank_format(self.pdf_path)                

            elif bank == "Saraswat Co-Operative Bank Ltd":
                self.data = self.parse_SARASWAT_pdf(self.pdf_path)

            elif bank == "Rajlaxmi Urban CO-OP Bank LTD":
                self.data = self.parse_rajlaxmi_bank_format(self.pdf_path)
                
            elif bank == "TJSB SAHAKARI BANK LTD":
                self.data = self.parse_tjsb_bank_format(self.pdf_path)

                
            elif bank == "test":
                self.data = self.parse_hdfc_format1(self.pdf_path)



            else:
                messagebox.showerror("Error", "Unsupported bank.")
                return
            # --- End of PDF Parsing Logic ---


            self.show_table()

            # **GUI Change: Place buttons in the bottom_action_frame side-by-side (using CTK)**

            # Clean up existing buttons
            if self.export_btn:
                self.export_btn.destroy()
            if self.tally_btn:
                self.tally_btn.destroy()

            # 1. Transfer to Tally Button (Highly Rounded, Red accent)
            self.tally_btn = ctk.CTkButton(
                self.bottom_action_frame,
                text="🚀 Transfer to Tally",
                font=ctk.CTkFont("Arial", 14, "bold"),
                fg_color="#e74c3c", hover_color="#c0392b",
                corner_radius=25, height=50,
                command=self.open_tally_transfer_window
            )
            self.tally_btn.pack(side=tk.LEFT, padx=20)

            # 2. Export to Excel Button (Highly Rounded, Green accent)
            self.export_btn = ctk.CTkButton(
                self.bottom_action_frame,
                text="✅ Export to Excel",
                font=ctk.CTkFont("Arial", 14, "bold"),
                fg_color="#2ecc71", hover_color="#27ae60",
                corner_radius=25, height=50,
                command=self.export_to_excel
            )
            self.export_btn.pack(side=tk.LEFT, padx=20)


        except Exception as e:
            messagebox.showerror("Error", str(e))
            

        

    def open_tally_transfer_window(self):
        # LOGIC: Check for data, map data (अपरिवर्तित)
        global cols, win, apply_filter, _update_master_from_tree
        if not isinstance(self.data, (pd.DataFrame, list)) or (isinstance(self.data, pd.DataFrame) and self.data.empty):
            messagebox.showerror("No Data", "Please convert a PDF first so preview data is available.")
            return

        # ---------- Map preview df -> tally columns (लॉजिक अपरिवर्तित) ----------
        df_src = self.data if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)
        df_src = df_src.drop_duplicates().reset_index(drop=True)
        df_tally = self._map_preview_to_tally(df_src)         
        
        self.root.withdraw()
        
        # ---------- Toplevel UI (GUI मध्ये CTK चा वापर) ----------
        win = ctk.CTkToplevel(self.root) # 1. CTkToplevel वापरले
        #win = tk.Toplevel(self.root)
        win.title("Transfer to Tally")
        win.after(10, lambda: win.wm_state('zoomed'))
        win.overrideredirect(False)
        win.attributes("-toolwindow", False)
        win.resizable(True, True)
        win.geometry("1250x700")
        win.configure(fg_color="#f4f6f9") # हलका बॅकग्राउंड
        
        win.grab_set()  
        
        
        def on_close():
            win.destroy()
            self.root.deiconify()
            self.root.after(10, lambda: self.root.wm_state('zoomed'))

        win.protocol("WM_DELETE_WINDOW", on_close)

        # ======================================================
        # --- Narration Search (above table) -------------------
        # ======================================================
        topbar = ctk.CTkFrame(win, fg_color="transparent") # पारदर्शक फ्रेम
        topbar.pack(fill=tk.X, padx=15, pady=10)

        # Grid configuration (लॉजिक अपरिवर्तित)
        topbar.grid_columnconfigure(7, weight=1) 

        # Connect Button (आकर्षक निळा रंग, गोलाकार)
        btn_connect = ctk.CTkButton(
            topbar, text="Connect to Tally", 
            command=lambda: self._fetch_ledgers_to_list(lb_ledgers),
            fg_color="#3498db", hover_color="#2980b9", corner_radius=10, height=35
        )
        btn_connect.grid(row=0, column=0, padx=6, pady=6, sticky="w")
        
        # Export XML Button (आकर्षक हिरवा रंग, गोलाकार)
        btn_export_xml = ctk.CTkButton(
            topbar, text="Export XML", 
            command=lambda: self._export_to_xml(),
            fg_color="#2ecc71", hover_color="#27ae60", corner_radius=10, height=35
        )
        btn_export_xml.grid(row=1, column=0, padx=6, pady=6, sticky="w")
        btn_export_xml.grid_remove()  

        # Edit Column Combobox
        ctk.CTkLabel(topbar, text="Edit Column:", text_color="#34495e").grid(row=0, column=1, padx=6, pady=6, sticky="w")
        cmb_editcol = ctk.CTkComboBox( # CTK ComboBox वापरले
            topbar,
            values=["LEDGER NAME", "BANK NAME", "DEBITE BALANCE", "CREDITE BALANCE"],
            state="readonly",
            width=180,
            fg_color="white", 
            border_color="#bdc3c7", 
            button_color="#3498db", 
            dropdown_fg_color="#f4f6f9",
            corner_radius=8
        )
        cmb_editcol.set("LEDGER NAME") 
        cmb_editcol.grid(row=0, column=2, padx=6, pady=6, sticky="w")

        # Value Entry
        ctk.CTkLabel(topbar, text="Value:", text_color="#34495e").grid(row=0, column=3, padx=6, pady=6, sticky="w")
        ent_value = ctk.CTkEntry(topbar, width=250, corner_radius=8, fg_color="white") # CTK Entry
        ent_value.grid(row=0, column=4, padx=6, pady=6, sticky="w")

        # Change Data button (आकर्षक नारंगी रंग, गोलाकार)
        btn_change = ctk.CTkButton(
            topbar, text="Change Data", 
            command=lambda: _apply_change_data(),
            fg_color="#f39c12", hover_color="#e67e22", corner_radius=10, height=35
        )
        btn_change.grid(row=0, column=5, padx=6, pady=(0,10), sticky="w")
       
        # Search Narration Entry
        ctk.CTkLabel(topbar, text="Search Narration:", text_color="#34495e").grid(row=1, column=1, padx=6, pady=6, sticky="w")
        self.narration_var = tk.StringVar()
        ent_narr = ctk.CTkEntry(topbar, textvariable=self.narration_var, width=250, corner_radius=8, fg_color="white") # CTK Entry
        ent_narr.grid(row=1, column=2, padx=6, pady=6, sticky="w")       
       
        
        # ==================== FILTER OPTIONS ====================
        filterbar = ctk.CTkFrame(win, fg_color="transparent")
        filterbar.pack(fill=tk.X, padx=15, pady=5)

        self.filter_var = tk.StringVar(value="all")  # लॉजिक अपरिवर्तित

        # --- Labels for counts (CTK Labels) ---
        self.total_all_lbl = ctk.CTkLabel(filterbar, text="", text_color="#34495e")
        self.total_complete_lbl = ctk.CTkLabel(filterbar, text="", text_color="#2ecc71")
        self.total_pending_lbl = ctk.CTkLabel(filterbar, text="", text_color="#e74c3c")

        # CTK Radio Buttons (निळा accent, गोलाकार)
        r_all = ctk.CTkRadioButton(filterbar, text="ALL DATA", value="all", variable=self.filter_var,
                                command=lambda: apply_filter(), 
                                fg_color="#3498db", hover_color="#2980b9", 
                                radiobutton_width=15, radiobutton_height=15)
        r_all.pack(side=tk.LEFT, padx=(10,2))
        self.total_all_lbl.pack(side=tk.LEFT, padx=(0,20))

        r_complete = ctk.CTkRadioButton(filterbar, text="COMPLETE ENTRIES", value="complete", variable=self.filter_var,
                                     command=lambda: apply_filter(),
                                     fg_color="#3498db", hover_color="#2980b9", 
                                     radiobutton_width=15, radiobutton_height=15)
        r_complete.pack(side=tk.LEFT, padx=(10,2))
        self.total_complete_lbl.pack(side=tk.LEFT, padx=(0,20))

        r_pending = ctk.CTkRadioButton(filterbar, text="PENDING ENTRIES", value="pending", variable=self.filter_var,
                                    command=lambda: apply_filter(),
                                    fg_color="#3498db", hover_color="#2980b9", 
                                    radiobutton_width=15, radiobutton_height=15)
        r_pending.pack(side=tk.LEFT, padx=(10,2))
        self.total_pending_lbl.pack(side=tk.LEFT, padx=(0,20))

     
        # -----------------------------------------------------------
        # ADD ACTION DROPDOWN FOR EACH ROW (NEW FUNCTION)
        # -----------------------------------------------------------
        def add_action_dropdowns():
            """
            Add a dropdown (Delete / Add Above / Add Below / Edit)
            into the Action column for every row.
            Rebuild after every edit.
            """

            # Remove old dropdowns
            for widget in self.frm_table.winfo_children():
                if isinstance(widget, ttk.Combobox):
                    widget.destroy()

            action_col_index = cols.index("Action")

            for iid in tv.get_children():
                bbox = tv.bbox(iid, column=action_col_index)
                if not bbox:
                    continue

                x, y, w, h = bbox

                combo = ttk.Combobox(
                    self.frm_table,
                    values=["Delete", "Add Above", "Add Below", "Edit"],
                    state="readonly",
                    width=12,
                )
                combo.place(x=x, y=y, width=w, height=h)

                combo.bind(
                    "<<ComboboxSelected>>",
                    lambda e, item=iid, cb=combo: handle_action(item, cb)
                )

        # -----------------------------------------------------------
        # ACTION HANDLER FOR DROP-DOWN
        # -----------------------------------------------------------
        def handle_action(iid, cb):
            """Perform row actions from dropdown."""
            act = cb.get()

            if act == "Delete":
                tv.delete(iid)
                _update_master_from_tree()

            elif act == "Add Above":
                blank = [""] * (len(cols) - 1)
                index = tv.index(iid)
                tv.insert("", index, values=blank + [""])
                _update_master_from_tree()

            elif act == "Add Below":
                blank = [""] * (len(cols) - 1)
                index = tv.index(iid)
                tv.insert("", index + 1, values=blank + [""])
                _update_master_from_tree()

            elif act == "Edit":
                self._edit_row_dialog(iid)

            cb.set("")
            apply_filter()
            add_action_dropdowns()


     
        # ======================================================
        # --- Helper : Count updater ---
        # ======================================================






        def update_counts():
            total_all = len(self.master_data)
            total_complete = 0
            total_pending = 0
            for row in self.master_data:
                # LOGIC UNCHANGED
                ledger = str(row[cols.index("LEDGER NAME")]).strip()
                bank   = str(row[cols.index("BANK NAME")]).strip()
                if ledger and bank:
                    total_complete += 1
                else:
                    total_pending += 1
            # GUI: update CTK Labels
            self.total_all_lbl.configure(text=f"TOTAL {total_all}")
            self.total_complete_lbl.configure(text=f"TOTAL {total_complete}")
            self.total_pending_lbl.configure(text=f"TOTAL {total_pending}")
            
            # ---------- Show/hide Export XML (लॉजिक अपरिवर्तित) ----------
            if total_pending == 0 and total_all > 0:
                btn_export_xml.grid()
            else:
                btn_export_xml.grid_remove()

        # ... (Definition of apply_filter function remains unchanged) ...




        # ======================================================
        # --- Filter Function ---
        # ======================================================
        def apply_filter():
            update_counts()  # refresh counts first
            choice = self.filter_var.get()
            if choice == "all":
                _reload_treeview(self.master_data)
                add_action_dropdowns()
            elif choice == "complete":
                complete = []
                for row in self.master_data:
                    ledger = str(row[cols.index("LEDGER NAME")]).strip()
                    bank   = str(row[cols.index("BANK NAME")]).strip()
                    if ledger and bank:
                        complete.append(row)
                _reload_treeview(complete)
            elif choice == "pending":
                pending = []
                for row in self.master_data:
                    ledger = str(row[cols.index("LEDGER NAME")]).strip()
                    bank   = str(row[cols.index("BANK NAME")]).strip()
                    if not ledger or not bank:
                        pending.append(row)
                _reload_treeview(pending)


        # ======================================================
        # --- Body with Table (Left) + Ledgers (Right) ---------
        # ======================================================
        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        body.grid_columnconfigure(0, weight=4)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # --- Table (Left Side - CTK Frame with Border) ---
        self.frm_table = ctk.CTkFrame(body, fg_color="white", corner_radius=12, border_width=1, border_color="#bdc3c7")
        self.frm_table.grid(row=0, column=0, sticky="nsew", padx=(0,4), pady=5)

        cols = ["DATE", "NARRATION", "CHQ / REF NO", "VALUE DATE", "LEDGER NAME", "BANK NAME",
                "DEBITE BALANCE", "CREDITE BALANCE", "DR / CR AMOUNT", "CLOSING BALANCE", "Row", "Action"]
        tv = ttk.Treeview(self.frm_table, columns=cols, show="headings")
        # ADD THIS RIGHT AFTER TV CREATION:
        self.tv = tv
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=140 if c != "NARRATION" else 350, stretch=True)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10) # Added padding

        # Scrollbars (TTK for Treeview)
        scy = ttk.Scrollbar(self.frm_table, orient="vertical", command=tv.yview)
        scx = ttk.Scrollbar(self.frm_table, orient="horizontal", command=tv.xview)
        tv.configure(yscroll=scy.set, xscroll=scx.set)
        scy.pack(side=tk.RIGHT, fill=tk.Y)
        scx.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Ledger Listbox (Right Side - CTK Frame with Border) ---
        right = ctk.CTkFrame(body, fg_color="white", corner_radius=12, border_width=1, border_color="#bdc3c7")
        right.grid(row=0, column=1, sticky="nsew", pady=5)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        lbl_title = ctk.CTkLabel(right, text="Tally Ledgers", font=ctk.CTkFont("Arial", 12, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))

        frame_lb = ctk.CTkFrame(right, fg_color="transparent")
        frame_lb.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Keeping tk.Listbox
        lb_ledgers = tk.Listbox(
            frame_lb, activestyle="dotbox", font=("Arial", 9), width=50, borderwidth=0, highlightthickness=0
        )
        lb_ledgers.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(frame_lb, orient="vertical", command=lb_ledgers.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x = ttk.Scrollbar(frame_lb, orient="horizontal", command=lb_ledgers.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        lb_ledgers.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        frame_lb.grid_rowconfigure(0, weight=1)
        frame_lb.grid_columnconfigure(0, weight=1)

        # ======================================================
        # --- Narration Filter Logic (with preserved edits)
        # ======================================================


        # Master data (always stores full table with edits)
        self.master_data = df_tally.values.tolist()

        def _reload_treeview(data):
            """Clear & reload treeview with given data"""
            tv.delete(*tv.get_children())
            for row in data:
                tv.insert("", "end", values=row)

        def _update_master_from_tree():
            """Update master_data with current visible Treeview values"""
            self.master_data = []
            for item in tv.get_children():
                self.master_data.append(tv.item(item, "values"))

        def _filter_narration(event=None):
            """Filter rows based on narration text + current filter option"""
            search_text = self.narration_var.get().strip().lower()

            # --- Step A: get base subset according to radio selection ---
            choice = self.filter_var.get()
            base_data = []
            if choice == "all":
                base_data = self.master_data
            elif choice == "complete":
                for row in self.master_data:
                    ledger = str(row[cols.index("LEDGER NAME")]).strip()
                    bank   = str(row[cols.index("BANK NAME")]).strip()
                    if ledger and bank:
                        base_data.append(row)
            elif choice == "pending":
                for row in self.master_data:
                    ledger = str(row[cols.index("LEDGER NAME")]).strip()
                    bank   = str(row[cols.index("BANK NAME")]).strip()
                    if not ledger or not bank:
                        base_data.append(row)

            # --- Step B: narration filter apply करा ---
            if not search_text:
                # जर search रिकामा असेल → फक्त filter option चं data दाखव
                _reload_treeview(base_data)
                return

            filtered = []
            for row in base_data:
                if len(row) > 1 and search_text in str(row[1]).lower():
                    filtered.append(row)

            _reload_treeview(filtered)
            add_action_dropdowns()

        # Bind typing event
        ent_narr.bind("<KeyRelease>", _filter_narration)

        # Bind Down Arrow → Treeview focus
        ent_narr.bind("<Down>", lambda e: tv.focus_set())
        


        # ======================================================
        # --- Insert initial data into Treeview ----------------
        # ======================================================
        _reload_treeview(self.master_data)

        
        
        

        # ----------------- Multi-select & Key Bindings -----------------
        def select_all_rows(event=None):
            """Ctrl+A = Select all rows"""
            tv.selection_set(tv.get_children())
            return "break"

        def clear_selection(event=None):
            """Esc = Clear all selections"""
            tv.selection_remove(tv.selection())
            return "break"

        def arrow_move(event):
            """Up/Down = Move focus only (keep all selections), highlight new row"""
            focus = tv.focus()
            children = list(tv.get_children())
            if not children:
                return "break"

            if not focus:
                focus = children[0]
                tv.focus(focus)
                tv.see(focus)
                highlight_focus_row()
                return "break"

            idx = children.index(focus)
            new_item = None

            if event.keysym == "Down" and idx < len(children) - 1:
                new_item = children[idx + 1]
            elif event.keysym == "Up" and idx > 0:
                new_item = children[idx - 1]
            else:
                return "break"

            if new_item:
                tv.focus(new_item)
                tv.see(new_item)
                highlight_focus_row()

            return "break"

           
        def space_toggle(event=None):
            """Space = Toggle selection of focused row"""
            focus = tv.focus()
            if not focus:
                children = tv.get_children()
                if children:
                    focus = children[0]
                    tv.focus(focus)
                    tv.see(focus)
                else:
                    return "break"

            # Toggle selection for focused row
            if focus in tv.selection():
                tv.selection_remove(focus)
            else:
                tv.selection_add(focus)

            # Keep focus visible
            tv.focus(focus)
            tv.see(focus)
            highlight_focus_row()

            return "break"
            
            
        def highlight_focus_row():
            """Highlight the currently focused row with a temporary tag"""
            for item in tv.get_children():
                tv.item(item, tags=())  # remove previous highlight

            focus = tv.focus()
            if focus:
                tv.item(focus, tags=("focus_highlight",))
                tv.tag_configure("focus_highlight", background="#d0ebff")  # 🔵 light blue 

        # Bind keys
        tv.bind("<Control-a>", select_all_rows)
        tv.bind("<Control-A>", select_all_rows)
        tv.bind("<Escape>", clear_selection)
        tv.bind("<space>", space_toggle)      # 🟢 Space  toggle
        tv.bind("<Down>", arrow_move)         # ⬇️ Focus 
        tv.bind("<Up>", arrow_move)           # ⬆️ Focus 

        # --- Ledger Listbox (Right Side) ---
        right = tk.Frame(body, bg="#f4f6f9")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        lbl_title = ttk.Label(right, text="Tally Ledgers", font=("Arial", 9, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w", padx=4, pady=(0,6))

        frame_lb = tk.Frame(right, bg="#f4f6f9")
        frame_lb.grid(row=1, column=0, sticky="nsew")

        lb_ledgers = tk.Listbox(
            frame_lb,
            activestyle="dotbox",
            font=("Arial", 9),
            width=50
        )
        lb_ledgers.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(frame_lb, orient="vertical", command=lb_ledgers.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x = ttk.Scrollbar(frame_lb, orient="horizontal", command=lb_ledgers.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        lb_ledgers.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        frame_lb.grid_rowconfigure(0, weight=1)
        frame_lb.grid_columnconfigure(0, weight=1)




        # ======================================================
        # Context menu for deleting rows
        context_menu = tk.Menu(tv, tearoff=0)
        context_menu.add_command(label="Delete Row", command=lambda: delete_row())
        tv.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

        # --- Bind Delete key
        tv.bind("<Delete>", lambda event: delete_row())
        
        def delete_row():
            selected_items = tv.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "No row selected")
                return

            to_delete_rows = []
            for item in selected_items:
                vals = tv.item(item, "values")
                row_no = vals[cols.index("Row")]
                to_delete_rows.append(row_no)

            # Delete from master_data using Row number
            self.master_data = [r for r in self.master_data if str(r[cols.index("Row")]) not in to_delete_rows]

            # Delete from Treeview
            for item in selected_items:
                tv.delete(item)

            # ✅ Reset Row numbers in master_data and Treeview
            for i, iid in enumerate(tv.get_children(), start=1):
                vals = list(tv.item(iid, "values"))
                vals[cols.index("Row")] = str(i)
                tv.item(iid, values=vals)
                if i-1 < len(self.master_data):
                    self.master_data[i-1][cols.index("Row")] = str(i)

            apply_filter()






        def show_context_menu(event):
            row_id = tv.identify_row(event.y)
            if row_id:
                tv.selection_set(row_id)
                context_menu.post(event.x_root, event.y_root)

        # Bind right-click
        tv.bind("<Button-3>", show_context_menu)

 

        # --- Helpers ---
        def _filter_lb(*_):
            needle = ent_value.get().lower()
            items = getattr(lb_ledgers, "_all_items", [])
            lb_ledgers.delete(0, tk.END)
            for it in items:
                if needle in it.lower():
                    lb_ledgers.insert(tk.END, it)

        ent_value.bind("<KeyRelease>", lambda e: _filter_lb())

        def _focus_listbox(event):
            if lb_ledgers.size() > 0:
                lb_ledgers.focus_set()
                lb_ledgers.selection_set(0)
                lb_ledgers.activate(0)

        ent_value.bind("<Down>", _focus_listbox)

        def _take_from_lb(event=None):
            sel = lb_ledgers.curselection()
            if sel:
                name = lb_ledgers.get(sel[0])
                ent_value.delete(0, tk.END)
                ent_value.insert(0, name)
                ent_value.focus_set()

        lb_ledgers.bind("<Return>", _take_from_lb)


        def _apply_change_data():
            col_choice = cmb_editcol.get()
            if not col_choice:
                messagebox.showwarning("Missing", "Please select column (Ledger, Bank, Debit OR Credit).")
                return
            new_val = ent_value.get().strip()

            # --- Check for '&' (not allowed in XML) ---
            if "&" in new_val:
                messagebox.showerror(
                    "Invalid Character",
                    "Please change your Tally Ledger name, remove '&' since XML format does not support it.\nSELECTED SUSPENSE LEDGER"
                )
                return  # Stop applying change

            if not new_val:
                new_val = ""

            for iid in tv.selection():
                vals = list(tv.item(iid, "values"))

                # --- Update value in Treeview row ---
                col_index = cols.index(col_choice)
                vals[col_index] = new_val

                # If Debit is entered → clear Credit
                if col_choice.upper() == "DEBITE BALANCE" and new_val != "":
                    credit_index = cols.index("CREDITE BALANCE")
                    vals[credit_index] = ""
                # If Credit is entered → clear Debit
                if col_choice.upper() == "CREDITE BALANCE" and new_val != "":
                    debit_index = cols.index("DEBITE BALANCE")
                    vals[debit_index] = ""

                # --- Recalculate DR/CR Amount ---
                try:
                    debit = float(str(vals[cols.index("DEBITE BALANCE")]).replace(",", "")) if vals[cols.index("DEBITE BALANCE")] else 0.0
                except:
                    debit = 0.0
                try:
                    credit = float(str(vals[cols.index("CREDITE BALANCE")]).replace(",", "")) if vals[cols.index("CREDITE BALANCE")] else 0.0
                except:
                    credit = 0.0

                if debit != 0:
                    drcr = -debit   # If debit exists → DR/CR = negative credit
                elif credit != 0:
                    drcr = credit # If credit exists → DR/CR = positive debit
                else:
                    drcr = 0.0

                # --- Format all numeric columns (no commas, 2 decimals) ---
                vals[cols.index("DEBITE BALANCE")] = f"{debit:.2f}"
                vals[cols.index("CREDITE BALANCE")] = f"{credit:.2f}"
                vals[cols.index("DR / CR AMOUNT")] = f"{drcr:.2f}"

                # --- Update row in Treeview ---
                tv.item(iid, values=vals)

                # --- Update in master_data also ---
                row_index = int(vals[cols.index("Row")]) - 1   # "Row" col stores row number
                if 0 <= row_index < len(self.master_data):
                    self.master_data[row_index] = vals

            # Reapply any filters after change
            apply_filter()



        # ======================================================
        # --- Action Combobox (for Action column) ---------------
        # ======================================================
        action_var = tk.StringVar()
        action_box = ttk.Combobox(
            tv,
            textvariable=action_var,
            values=["Delete", "Add Above", "Add Below", "Edit"],
            state="readonly"
        )


    def _export_to_xml(self, tree=None):
        import pathlib, datetime

        try:
            tv = tree or getattr(self, "tv", None)
            if tv is None:
                messagebox.showerror("No Table", "No table available for export. Convert PDF first.")
                return
            
            rows = self.master_data  # Final updated data
            # -------- Fix DR/CR Amount in self.master_data --------
            fixed_rows = []
            for r in self.master_data:
                r = list(r)
                debit  = float(str(r[6]).replace(",", "")) if r[6] else 0   # Debit Balance
                credit = float(str(r[7]).replace(",", "")) if r[7] else 0   # Credit Balance

                if debit != 0:
                    r[8] = -debit
                elif credit != 0:
                    r[8] = credit
                else:
                    r[8] = 0

                fixed_rows.append(r)

            # Update back to master_data
            self.master_data = fixed_rows
            rows = self.master_data
            
            
            
            if not rows:
                messagebox.showwarning("No Data", "No data available to export.")
                return

            # ================== Step 1: Check Ledger/Bank for '&' ==================
            bad_rows = []
            for idx, r in enumerate(rows):
                ledger = str(r[4]).strip()
                bank   = str(r[5]).strip()
                if "&" in ledger or "&" in bank:
                    # Store row index and short ledger/bank for display
                    bad_rows.append((idx+1, ledger[:15]+"..." if len(ledger)>15 else ledger, 
                                           bank[:15]+"..." if len(bank)>15 else bank))

            if bad_rows:
                # Create message showing rows with & sign
                msg = "Please change your Tally Ledger name, remove '&' since XML format does not support it.\n"
                msg += "Or please change Ledger/Bank name in these rows:\n\n"
                for row_num, ledger_short, bank_short in bad_rows[:10]:
                    msg += f" Row {row_num}: Ledger: {ledger_short} | Bank: {bank_short}\n"
                if len(bad_rows) > 10:
                    msg += f"...and {len(bad_rows)-10} more rows"
                messagebox.showerror("Invalid Ledger/Bank Names", msg)
                return

            # ================== Step 2: Replace '&' in Narration / CQRefNo ==================
            clean_rows = []
            for r in rows:
                r = list(r)
                r[1] = str(r[1]).replace("&", "And")   # Narration
                r[2] = str(r[2]).replace("&", "And")   # CQRefNo
                clean_rows.append(r)

            # Confirm balance verification
            confirm = messagebox.askyesno(
                "Balance Verification",
                "Does the Opening Balance in Tally match the Bank Statement Balance?\n\nYes → XML will be created\nNo → Cancel"
            )
            if not confirm:
                messagebox.showinfo("Cancelled", "Operation Cancelled, XML not created")
                return

            # ---------------- Create XML ----------------
            xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml_lines.append("<ENVELOPE>")
            xml_lines.append("  <HEADER>")
            xml_lines.append("    <TALLYREQUEST>Import Data</TALLYREQUEST>")
            xml_lines.append("  </HEADER>")
            xml_lines.append("  <BODY>")
            xml_lines.append("    <IMPORTDATA>")
            xml_lines.append("      <REQUESTDESC>")
            xml_lines.append("        <REPORTNAME>All Masters</REPORTNAME>")
            xml_lines.append("        <STATICVARIABLES>")
            xml_lines.append("          <SVCURRENTCOMPANY>SMAART</SVCURRENTCOMPANY>")
            xml_lines.append("        </STATICVARIABLES>")
            xml_lines.append("      </REQUESTDESC>")
            xml_lines.append("      <REQUESTDATA>")

            # Loop through all rows
            for row in clean_rows:
                voucherDate   = str(row[0])  # DATE
                narration     = str(row[1])  # NARRATION (cleaned)
                cqRefNo       = str(row[2])  # CHQ / REF NO (cleaned)
                valueDate     = str(row[3])  # VALUE DATE
                ledgerName    = str(row[4])  # LEDGER NAME
                bankName      = str(row[5])  # BANK NAME
                amount        = float(row[8]) if row[8] else 0  # DR/CR Amount

                if not ledgerName or not bankName or amount == 0:
                    continue

                if amount < 0:
                    voucherType = "Payment"
                    amountPositive = -amount
                else:
                    voucherType = "Receipt"
                    amountPositive = amount

                xml_lines.append('        <TALLYMESSAGE xmlns:UDF="TallyUDF">')
                xml_lines.append(f'          <VOUCHER ACTION="Create" VCHTYPE="{voucherType}">')
                xml_lines.append(f'            <VOUCHERTYPENAME>{voucherType}</VOUCHERTYPENAME>')
                xml_lines.append(f'            <DATE>{voucherDate}</DATE>')
                xml_lines.append(f'            <VOUCHERNUMBER></VOUCHERNUMBER>')
                xml_lines.append(f'            <PARTYLEDGERNAME>{ledgerName}</PARTYLEDGERNAME>')
                xml_lines.append(f'            <NARRATION>{narration}</NARRATION>')
                xml_lines.append(f'            <EFFECTIVEDATE>{valueDate}</EFFECTIVEDATE>')

                # Ledger Entry 1
                xml_lines.append("            <ALLLEDGERENTRIES.LIST>")
                xml_lines.append(f'              <LEDGERNAME>{ledgerName}</LEDGERNAME>')
                xml_lines.append("              <REMOVEZEROENTRIES>NO</REMOVEZEROENTRIES>")
                xml_lines.append("              <LEDGERFROMITEM>NO</LEDGERFROMITEM>")
                xml_lines.append(f'              <ISDEEMEDPOSITIVE>{"YES" if amount < 0 else "NO"}</ISDEEMEDPOSITIVE>')
                xml_lines.append(f'              <AMOUNT>{amount}</AMOUNT>')
                xml_lines.append("            </ALLLEDGERENTRIES.LIST>")

                # Ledger Entry 2
                xml_lines.append("            <ALLLEDGERENTRIES.LIST>")
                xml_lines.append(f'              <LEDGERNAME>{bankName}</LEDGERNAME>')
                xml_lines.append("              <REMOVEZEROENTRIES>NO</REMOVEZEROENTRIES>")
                xml_lines.append("              <LEDGERFROMITEM>NO</LEDGERFROMITEM>")
                xml_lines.append(f'              <ISDEEMEDPOSITIVE>{"NO" if amount < 0 else "YES"}</ISDEEMEDPOSITIVE>')
                xml_lines.append(f'              <AMOUNT>{-amountPositive if voucherType=="Receipt" else amountPositive}</AMOUNT>')
                xml_lines.append("              <BANKALLOCATIONS.LIST>")
                xml_lines.append(f'                <DATE>{voucherDate}</DATE>')
                xml_lines.append(f'                <NAME>{cqRefNo}</NAME>')
                xml_lines.append(f'                <AMOUNT>{-amountPositive if voucherType=="Receipt" else amountPositive}</AMOUNT>')
                xml_lines.append("                <PAYMENTMODE>Transacted</PAYMENTMODE>")
                xml_lines.append("                <TRANSACTIONTYPE>Cheque</TRANSACTIONTYPE>")
                xml_lines.append(f'                <INSTRUMENTDATE>{valueDate}</INSTRUMENTDATE>')
                xml_lines.append(f'                <INSTRUMENTNUMBER>{cqRefNo}</INSTRUMENTNUMBER>')
                xml_lines.append("              </BANKALLOCATIONS.LIST>")
                xml_lines.append("            </ALLLEDGERENTRIES.LIST>")

                xml_lines.append("          </VOUCHER>")
                xml_lines.append("        </TALLYMESSAGE>")

            xml_lines.append("      </REQUESTDATA>")
            xml_lines.append("    </IMPORTDATA>")
            xml_lines.append("  </BODY>")
            xml_lines.append("</ENVELOPE>")

            # ---------------- Save File ----------------
            desktop = pathlib.Path.home() / "Desktop" / "Tally_XML"
            desktop.mkdir(exist_ok=True)
            ts = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
            out = desktop / f"TallyVoucher_{ts}.xml"

            with open(out, "w", encoding="utf-8") as f:
                f.write("\n".join(xml_lines))

            messagebox.showinfo("Success", f"XML file created successfully:\n{out}")

        except Exception as e:
            messagebox.showerror("Export Failed", str(e))



        # ======================================================
        # --- 🟢 ACTION BOX LOGIC (ERROR FIX APPLIED) 🟢 ---
        # ======================================================
        
        # 1. CREATE ACTION BOX LOCALLY (Removed 'self.' to fix AttributeError)
        action_var = tk.StringVar()
        action_box = ttk.Combobox(
            self.frm_table, 
            textvariable=action_var, 
            values=["Delete", "Add Above", "Add Below", "Edit"],
            state="readonly",
            justify="center",
            font=("Arial", 9)
        )
        action_box.place_forget() 

        def _show_action_box(event=None):
            sel = tv.focus()
            if not sel:
                action_box.place_forget()
                return
            
            # Find the bounding box for the "Action" column in the selected row
            col_index = cols.index("Action")
            bbox = tv.bbox(sel, column=col_index)
            
            if not bbox:
                action_box.place_forget()
                return
            
            x, y, w, h = bbox
            # Place action_box relative to the Treeview position inside its parent frame (self.frm_table)
            # tv.winfo_x() and tv.winfo_y() give the Treeview's offset.
            action_box.place(x=x + tv.winfo_x(), y=y + tv.winfo_y(), width=w, height=h)
            action_box.lift()

        def _do_action(*_):
            act = action_var.get()
            sel = tv.focus()
            if not sel:
                action_var.set("")
                action_box.place_forget()
                return

            if act == "Delete":
                # NOTE: For proper master_data sync, call your delete_row() function here
                tv.delete(sel)
                _update_master_from_tree() 
                # This ensures Row numbers are consistent after deletion (although delete_row is better)
                # For simplicity, we keep the original tv.delete(sel) but ensure master data is synced.
            elif act in ("Add Above", "Add Below"):
                blank = [""] * len(cols)
                idx = tv.index(sel)
                tv.insert("", idx if act == "Add Above" else idx+1, values=blank)
                _update_master_from_tree() # Sync master data
            elif act == "Edit":
                _edit_row_dialog(sel)
                
            action_var.set("")
            action_box.place_forget()
            # Reload counts/filters after action
            apply_filter() 


        # 2. BINDINGS (Using 'action_box' instead of 'self.action_box')
        action_box.bind("<<ComboboxSelected>>", _do_action)
        tv.bind("<<TreeviewSelect>>", _show_action_box)
        tv.bind("<Button-1>", _show_action_box)




        # --- Edit Row Dialog ---
        def _edit_row_dialog(iid):
            vals = list(tv.item(iid, "values"))
            dlg = tk.Toplevel(win)
            dlg.title("Edit Row")
            dlg.transient(win)
            fields = cols[:-1]  # exclude Action
            entries = {}
            for i, c in enumerate(fields):
                ttk.Label(dlg, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
                e = ttk.Entry(dlg, width=60)
                e.grid(row=i, column=1, padx=6, pady=4)
                e.insert(0, vals[i])
                entries[c] = e

            def _ok():
                new_vals = [entries[c].get() for c in fields] + [""]
                tv.item(iid, values=new_vals)
                dlg.destroy()

            ttk.Button(dlg, text="OK", command=_ok).grid(row=len(fields), column=0, padx=6, pady=8)
            ttk.Button(dlg, text="Cancel", command=dlg.destroy).grid(row=len(fields), column=1, padx=6, pady=8)

        # --- Export Excel ---
        def _export_current_tv(tree):
            import pathlib
            rows = [tree.item(iid, "values") for iid in tree.get_children("")]
            df_out = pd.DataFrame(rows, columns=cols)
            desktop = pathlib.Path.home() / "Desktop"
            out = desktop / "Tally_Transfer.xlsx"
            try:
                df_out.drop(columns=["Action"], errors="ignore").to_excel(out, index=False)
                messagebox.showinfo("Saved", f"File created:\n{out}")
            except Exception as e:
                messagebox.showerror("Save failed", str(e))



    def _map_preview_to_tally(self, df):
        """
        Normalize different bank statement columns into standard format for Tally transfer.
        """
        cols = [c.upper().strip() for c in df.columns]
        df = df.copy()
        df.columns = cols

        def pick(*names):
            for n in names:
                if n in df.columns:
                    return df[n]
            return [""]*len(df)

        date = pick("DATE","TRAN DATE","VALUE DATE","POST DATE","Date")
        vdate = pick("VALUE DATE","POST DATE","Value Dt")
        narr = pick("NARRATION","PARTICULARS","DESCRIPTION","DETAILS")
        chq  = pick("CHQ/REF NO","CHQ.NO.","CHEQUE NO","INST NO","CHEQUE/INSTRUMENT","Chq./Ref.No.")
        debit = pick("WITHDRAWALS","DEBIT","DEBITS","Withdrawal Amt.","DEBIT AMOUNT")
        credit= pick("DEPOSITS","DEPOSIT","CREDIT","CREDITS","Deposit Amt.", "CREDIT AMOUNT")
        bal   = pick("BALANCE","Closing Balance")
        


        def to_num(s):
            try:
                s = str(s).replace(",","").replace("Cr","").replace("DR","").replace("Dr","").replace("CR","").strip()
                return float(s) if s not in ("",None) else 0.0
            except:
                return 0.0
        drcr = [ (to_num(c) - to_num(d)) for d,c in zip(debit,credit) ]

        out = pd.DataFrame({
            "DATE": [str(x) for x in date],
            "NARRATION": [str(x) for x in narr],
            "CHQ / REF NO": [str(x) for x in chq],
            "VALUE DATE": [str(x) for x in vdate],
            "LEDGER NAME": ["" for _ in range(len(df))],
            "BANK NAME": [self.bank_var.get()] * len(df),
            "DEBITE BALANCE": [str(x) for x in debit],
            "CREDITE BALANCE": [str(x) for x in credit],
            "DR / CR AMOUNT": [f"{x:.2f}" if isinstance(x,(int,float)) else str(x) for x in drcr],
            "CLOSING BALANCE": [str(x) for x in bal],
            "Row": list(range(1, len(df)+1))
        })
        return out


    def _fetch_ledgers_to_list(self, listbox_widget):
        """
        Connect to Tally and fetch ONLY Ledgers (no stock items, no groups).
        Uses a custom Collection request.
        """
        try:
            envelope = """<ENVELOPE>
              <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>Ledger Coll</ID>
              </HEADER>
              <BODY>
                <DESC>
                  <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                  </STATICVARIABLES>
                  <TDL>
                    <TDLMESSAGE>
                      <COLLECTION NAME="Ledger Coll" ISMODIFY="No">
                        <TYPE>Ledger</TYPE>
                        <NATIVEMETHOD>NAME</NATIVEMETHOD>
                      </COLLECTION>
                    </TDLMESSAGE>
                  </TDL>
                </DESC>
              </BODY>
            </ENVELOPE>""".encode("utf-8")

            r = requests.post(
                "http://127.0.0.1:9000",
                data=envelope,
                headers={"Content-Type": "text/xml"},
                timeout=5
            )
            r.raise_for_status()

            from lxml import etree
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(r.text.encode("utf-8", "ignore"), parser=parser)

            # --- Extract ONLY ledger <NAME> tags ---
            names = []
            for tag in root.iter():
                if tag.tag.upper() == "NAME" and tag.text:
                    names.append(tag.text.strip())

            names = sorted(set(names))

            # --- Update Listbox ---
            listbox_widget.delete(0, tk.END)
            for n in names:
                listbox_widget.insert(tk.END, n)
            listbox_widget._all_items = names

            if not names:
                messagebox.showwarning(
                    "No Ledgers",
                    "Connected to Tally but no ledgers were returned.\n"
                    "👉 Make sure a company is open in Tally and has ledgers."
                )

        except Exception as e:
            listbox_widget.delete(0, tk.END)
            listbox_widget._all_items = []
            messagebox.showwarning("Tally connection",
                                   f"Could not fetch ledgers from Tally.\n{e}")
















    # ----------------- Bank of Maharashtra -----------------
    def clean_extracted_data(self, df):


        # --- (1) Remove all rows below the last Sr No ---
        # Find the last valid Sr No (numeric)
        last_valid_srno = None
        for i in range(len(df)):
            val = str(df.loc[i, "Sr No"]).strip()
            if val.isdigit():
                last_valid_srno = int(val)

        # Keep only rows up to the last Sr No
        if last_valid_srno:
            df = df[df["Sr No"].astype(str).str.isdigit()]
            df = df[df["Sr No"].astype(int) <= last_valid_srno]

        # --- (2) Remove any rows after “Total Transaction Count” or similar footer text ---
        total_index = df[df.apply(lambda r: r.astype(str).str.contains("Total Transaction Count", case=False).any(), axis=1)].index
        if len(total_index) > 0:
            last_row_index = total_index[0]
            df = df.loc[:last_row_index - 1]

        # --- (3) Replace <NA> or nan in “Cheque/Reference No” column with blank ---
        if "CHQ/REF NO" in df.columns:
            df["CHQ/REF NO"] = df["CHQ/REF NO"].replace(["<NA>", "nan", "NaN", None], "")

        # --- (4) Replace "-" in Debit and Credit columns with blank ---
        for col in ["Debit", "Credit"]:
            if col in df.columns:
                df[col] = df[col].replace("-", "")
                df[col] = df[col].replace(["nan", "<NA>", None], "")

        return df

    def parse_bom_format(self, path):


        all_data = []
        base_columns = None

        with pdfplumber.open(path, password=self.pdf_password) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for tbl in tables:
                    df = pd.DataFrame(tbl)
                    df = df.dropna(how="all").dropna(axis=1, how="all")
                    if df.empty:
                        continue

                    col_count = len(df.columns)
                    if base_columns is None and col_count >= 6:
                        # Set base column names using the first non-empty table
                        base_columns = [str(c).strip() if c else f"COL_{i+1}" for i, c in enumerate(df.iloc[0])]
                        df = df.iloc[1:]
                        df.columns = base_columns
                    else:
                        # Adjust number of columns to match base_columns
                        if col_count < len(base_columns):
                            # Add extra empty columns if the table has fewer columns
                            for i in range(len(base_columns) - col_count):
                                df[f"Extra_{i+1}"] = ""
                            df.columns = base_columns
                        elif col_count > len(base_columns):
                            # Add extra column names if the table has more columns
                            extra_cols = [f"Extra_{i+1}" for i in range(col_count - len(base_columns))]
                            df.columns = base_columns + extra_cols
                        else:
                            df.columns = base_columns
                    all_data.append(df)

        if not all_data:
            raise Exception("No valid Bank of Maharashtra tables found.")

        # Combine all pages
        final_df = pd.concat(all_data, ignore_index=True)
        # Remove 'Extra_' columns
        final_df = final_df.loc[:, ~final_df.columns.str.startswith("Extra_")]
        # Replace empty strings with NaN and remove fully empty rows
        final_df = final_df.replace("", pd.NA).dropna(how="all")

        # -------------------------------------------------------
        # 🔹 Keep only transaction part of the table
        # -------------------------------------------------------

        # 1️⃣ Find the row that contains 'Sr No'
        srno_row_index = None
        for i, row in final_df.iterrows():
            if any(str(cell).strip().lower() == "sr no" for cell in row):
                srno_row_index = i
                break

        if srno_row_index is not None:
            # 2️⃣ Keep only rows below the 'Sr No' header row
            final_df = final_df.iloc[srno_row_index + 1:].reset_index(drop=True)
        else:
            raise Exception("'Sr No' header not found in extracted table.")

        # 3️⃣ Keep only the first 7 columns (Sr No to Balance)
        final_df = final_df.iloc[:, :7]

        # 4️⃣ Assign new proper column names
        final_df.columns = [
            "Sr No",
            "Date",
            "Particulars",
            "CHQ/REF NO",
            "Debit",
            "Credit",
            "Balance"
        ]

        # 5️⃣ Remove empty rows if any
        final_df = final_df.dropna(how="all")

        # 6️⃣ Clean and filter the data using custom logic
        final_df = self.clean_extracted_data(final_df)

        return final_df




    def parse_central_bank_format(self, path):
        text_data = ""
        with fitz.open(path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text")

        final_data = []
        buffer_line = ""
        last_balance = None

        for line in text_data.split("\n"):
            line = line.strip()
            if not line:
                continue

            # If header/footer line comes  flush buffer before skipping
            if any(skip in line for skip in [
                "Page", 
                "Date Particulars Withdrawals Deposits Balance",
                "Opening Balance", 
                "Closing Balance",
                "Statement for A/c"
            ]):
                if buffer_line:
                    entry = self._process_entry(buffer_line, last_balance)
                    if entry:
                        final_data.append(entry)
                        if entry["BALANCE"]:
                            last_balance = float(entry["BALANCE"])
                    buffer_line = ""
                continue

            # If line starts with a date  process previous buffer
            if re.match(r"^\d{2}-\d{2}-\d{4}", line):
                if buffer_line:
                    entry = self._process_entry(buffer_line, last_balance)
                    if entry:
                        final_data.append(entry)
                        if entry["BALANCE"]:
                            last_balance = float(entry["BALANCE"])
                buffer_line = line
            else:
                # Otherwise continue appending to particulars
                buffer_line += " " + line

        # Process the last entry
        if buffer_line:
            entry = self._process_entry(buffer_line, last_balance)
            if entry:
                final_data.append(entry)

        return pd.DataFrame(final_data)

    def _process_entry(self, buffer_line, last_balance):
        match = re.match(
            r"^(\d{2}-\d{2}-\d{4})(?:\s+(.*?))?\s+([\d,]*\.?\d+)?\s+([\d,]*\.?\d+)?$",
            buffer_line.strip()
        )
        if match:
            date, particulars, amt, balance = match.groups()
            particulars = particulars or ""   # if None, keep empty
            amt = amt.replace(",", "") if amt else ""
            balance = balance.replace(",", "") if balance else ""
            withdrawal = deposit = ""

            # Calculate withdrawal/deposit from balance difference
            if last_balance is not None and balance:
                try:
                    diff = round(float(balance) - float(last_balance), 2)
                    if diff > 0:
                        deposit = f"{diff:.2f}"
                    elif diff < 0:
                        withdrawal = f"{abs(diff):.2f}"
                except:
                    pass

            # If withdrawal/deposit still empty but amt exists ? assign amt
            if amt and (not deposit and not withdrawal):
                if last_balance and balance:
                    try:
                        diff = round(float(balance) - float(last_balance), 2)
                        if diff == 0:   # Balance unchanged
                            deposit = amt
                        elif diff > 0:
                            deposit = amt
                        elif diff < 0:
                            withdrawal = amt
                    except:
                        deposit = amt
                else:
                    deposit = amt  # fallback if balance not available

            return {
                "DATE": date,
                "PARTICULARS": particulars.strip(),
                "WITHDRAWALS": withdrawal,
                "DEPOSITS": deposit,
                "BALANCE": balance
            }
        return None



    #---------state bank of india -------------


    def parse_sbi_bank_format(self, path):
        rows = []
        seen = set()
        with pdfplumber.open(path, password=self.pdf_password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Clean up row (strip spaces, handle None)
                        row = [cell.strip() if cell else "" for cell in row]

                        # Skip header / repeated header rows
                        if (
                            "Txn Date" in row[0]
                            or "Description" in row[2]
                            or row[0].startswith("----")
                            or row[0].startswith("Account")
                            or "Date" in row[0]
                            or "Details" in row[1]
                            or "Ref No." in row[2]
                            or "Debit" in row[3]
                            or "Credit" in row[4]
                            or "Balance" in row[5]
                        ):
                            continue

                        if len(row) >= 7:
                            key = tuple(row)   # tuple बनवून duplicate check
                            if key in seen:
                                continue
                            seen.add(key)
                            
                            rows.append({
                                "DATE": row[0],
                                "VALUE DATE": row[1],
                                "PARTICULARS": row[2],
                                "Ref No.": row[3],
                                "WITHDRAWALS": row[4],
                                "DEPOSITS": row[5],
                                "BALANCE": row[6],
                            })

        df = pd.DataFrame(rows)
        
        # ✅ Remove duplicate rows
        df = df.drop_duplicates().reset_index(drop=True)
        self.data = df 
        
        # ✅ Filter empty rows from DATE to BALANCE
        self.filter_empty_rows()
        
        return self.data


    def filter_empty_rows(self):
        """
        Remove rows where all columns from DATE to BALANCE are empty or blank ("").
        """
        if self.data is None or self.data.empty:
            return
        
        # Columns to check
        cols_to_check = ["DATE", "VALUE DATE", "PARTICULARS", "Ref No.", "WITHDRAWALS", "DEPOSITS", "BALANCE"]
        
        # Keep only rows where at least one of these columns has a non-empty value
        self.data = self.data[self.data[cols_to_check].apply(lambda x: any(str(v).strip() != "" for v in x), axis=1)]
        
        # Reset index after dropping
        self.data = self.data.reset_index(drop=True)
 

 # ------------------ MASTER UNION BANK PARSER ------------------
    def parse_union_bank_pdf(self, path):



        # -----------------------------------------------------
        # Validate if dataframe contains meaningful complete data
        # -----------------------------------------------------
        def is_valid(df):
            """Validate if dataframe contains required columns and non-empty data."""
            if df is None or df.empty:
                return False

            required = ["VALUE DATE", "POST DATE", "DETAILS", "DEBIT", "CREDIT", "BALANCE"]

            # Check if required columns exist
            for c in required:
                if c not in df.columns:
                    return False

            # At least 4 columns must contain non-empty values
            filled_cols = 0
            for c in required:
                if df[c].astype(str).str.strip().replace("", pd.NA).notna().sum() > 0:
                    filled_cols += 1

            return filled_cols >= 4

        # -----------------------------------------------------
        # Normalize dataframe columns for all formats
        # -----------------------------------------------------
        def normalize(df, fmt):
            """Convert all formats into standard output columns."""

            if df is None or df.empty:
                return df

            # Format-0 and Format-2 already match the final structure
            if fmt in ("f0", "f2"):
                return df

            # Format-1 → Convert to standard structure
            if fmt == "f1":
                df["VALUE DATE"] = df["DATE"]
                df["POST DATE"] = df["DATE"]
                df["DETAILS"] = df["DESCRIPTION"]
                df["DEBIT"] = df["WITHDRAWALS"]
                df["CREDIT"] = df["DEPOSITS"]
                # BALANCE already exists

                return df[
                    ["VALUE DATE", "POST DATE", "DETAILS",
                     "DEBIT", "CREDIT", "BALANCE"]
                ]

            return df

        # -----------------------------------------------------
        # TRY FORMAT 0
        # -----------------------------------------------------
        try:
            df0 = self.parse_union_format_0(path)
            df0 = normalize(df0, "f0")
            if is_valid(df0):
                return df0
        except:
            pass

        # -----------------------------------------------------
        # TRY FORMAT 1
        # -----------------------------------------------------
        try:
            df1 = self.parse_union_bank_format_1(path)
            df1 = normalize(df1, "f1")
            if is_valid(df1):
                return df1
        except:
            pass

        # -----------------------------------------------------
        # TRY FORMAT 2
        # -----------------------------------------------------
        try:
            df2 = self.parse_union_format_2(path)
            df2 = normalize(df2, "f2")
            if is_valid(df2):
                return df2
        except:
            pass

        # If all formats fail
        return pd.DataFrame()




    #----------------union bank ------------------------ 
    def parse_union_bank_format_1(self, path):


        text_data = ""
        with fitz.open(path) as doc:
            # password  authenticate 
            if self.pdf_password:
                if not doc.authenticate(self.pdf_password):
                    raise ValueError("Invalid PDF password")
            for page in doc:
                text_data += page.get_text("text")

        rows = []
        columns = ["DATE", "DESCRIPTION", "CHEQUE NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]

        # --- Raw extraction ---
        for line in text_data.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Skip headers / footers
            if line.startswith("Page ") or "Transaction Details" in line:
                continue

            # If URL line found -> delete last row
            if "https://" in line or "http://" in line:
                if rows:   # safe check
                    rows.pop()
                continue

            # Date column (dd-mm-yyyy)
            if re.match(r"\d{2}-\d{2}-\d{4}", line):
                parts = re.split(r"\s{2,}", line)   # split by 2+ spaces (columns)

                # Pad / Trim to exactly 6 columns
                while len(parts) < 6:
                    parts.append("")
                if len(parts) > 6:
                    # Merge middle parts into description
                    desc = " ".join(parts[1:-4])
                    parts = [parts[0], desc] + parts[-4:]

                row = dict(zip(columns, parts))
                rows.append(row)
            else:
                # narration line continuation
                if rows:
                    rows[-1]["DESCRIPTION"] += " " + line

        df = pd.DataFrame(rows, columns=columns)

        # --- Post Processing (Withdrawals / Deposits / Balance fix) ---
        refined_rows = []
        prev_balance = None

        # Extract Opening Balance if available
        opening_balance_match = re.search(r"Opening Balance[: ]+([\d,]+\.\d{2})", text_data)
        if opening_balance_match:
            prev_balance = float(opening_balance_match.group(1).replace(",", ""))

        for _, row in df.iterrows():
            desc = str(row["DESCRIPTION"]).strip()

            # Remove unwanted footer text after balance
            desc = re.sub(
                r"(Closing Balance:.*|Unless constituent.*|To strengthen.*|FASTEST MODE.*|GOOD PEOPLE.*)$",
                "",
                desc,
                flags=re.IGNORECASE,
            ).strip()

            # Balance at end of description (e.g. 8034.72Cr / Dr)
            bal_match = re.search(r"([\d,]+\.\d{2}\s*[CD]r?)$", desc, re.IGNORECASE)
            balance = row["BALANCE"]
            if bal_match:
                balance = bal_match.group()
                desc = desc[:desc.rfind(balance)].strip()

            # Amount before balance (e.g. 3985.00)
            amt_match = re.search(r"([\d,]+\.\d{2})$", desc)
            amt = ""
            if amt_match:
                amt = amt_match.group()
                desc = desc[:desc.rfind(amt)].strip()

            withdrawals, deposits = "", ""
            if amt and balance:
                bal_val = float(balance.replace("Cr", "").replace("Dr", "").replace(",", ""))
                amt_val = float(amt.replace(",", ""))

                if prev_balance is not None:
                    if bal_val > prev_balance:
                        deposits = amt
                    elif bal_val < prev_balance:
                        withdrawals = amt

                prev_balance = bal_val

            new_row = {
                "DATE": row["DATE"],
                "DESCRIPTION": desc,
                "CHEQUE NO": row["CHEQUE NO"],
                "WITHDRAWALS": withdrawals,
                "DEPOSITS": deposits,
                "BALANCE": balance
            }
            refined_rows.append(new_row)

        return pd.DataFrame(refined_rows, columns=columns)


    #-----------------------saraswat bank ------------------------
    def parse_saraswat_bank_format(self, path):


        text_data = ""
        with fitz.open(path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text")

        rows = []
        columns = ["DATE", "DESCRIPTION", "CHEQUE NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]

        # -------------------
        # 1) HEADER/FOOTER PATTERNS
        # -------------------
        header_footer_patterns = [
            r"SBTWO/",
            r"Sanction Limit",
            r"Opening Balance As On",
            r"Date\s+Dr Amount\s+Cr Amount\s+Total Amount\s+Particulars\s+Instruments",
            r"STATEMENT OF ACCOUNTS",
            r"Statement of Account",
            r"PAGE\s*:\s*\d+\s*Of\s*\d+",
            r"Page\s+\d+",
            r"Saraswat",
            r"Closing Balance",
            r"\*+ END OF STATEMENT \*+",
            r"Totals\s*/\s*Balance",
        ]

        lines = text_data.split("\n")
        cleaned_lines = []

        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # skip first 2 lines force
            if idx < 2:
                continue

            if any(re.search(p, line, re.IGNORECASE) for p in header_footer_patterns):
                continue

            cleaned_lines.append(line)

        # -------------------
        # 2) BUILD RAW ROWS
        # -------------------
        for line in cleaned_lines:
            if re.match(r"^\d{2}[-/]\d{2}[-/]\d{2,4}", line):
                parts = re.split(r"\s{2,}", line)
                while len(parts) < 6:
                    parts.append("")
                if len(parts) > 6:
                    desc = " ".join(parts[1:-4])
                    parts = [parts[0], desc] + parts[-4:]
                row = dict(zip(columns, parts))
                rows.append(row)
            else:
                if rows:
                    rows[-1]["DESCRIPTION"] += " " + line

        df = pd.DataFrame(rows, columns=columns)

        # -------------------
        # 3) DELETE UNWANTED ROWS (Account No / Customer ID)
        # -------------------
        delete_patterns = [
            r"SBTWO/",
            r"Sanction Limit",
            r"Opening Balance As On",
            r"STATEMENT OF ACCOUNTS",
            r"Statement of Account",
            r"PAGE\s*:\s*\d+\s*Of\s*\d+",
            r"Closing Balance",
            r"\*+ END OF STATEMENT \*+",
            r"Totals\s*/\s*Balance",
            r"Date\s+Dr Amount\s+Cr Amount\s+Total Amount\s+Particulars\s+Instruments",
            r"Account No\.",       # FULL ROW DELETE
            r"Customer ID",        # FULL ROW DELETE
        ]

        drop_index = []
        for idx, row in df.iterrows():
            row_text = " ".join([str(x) for x in row.values])

            #  If line starts with date, keep it (never delete)
            if re.match(r"^\d{2}[-/]\d{2}[-/]\d{2,4}", str(row["DATE"])):
                continue  

            #  Otherwise apply delete rules
            for pat in delete_patterns:
                if re.search(pat, row_text, re.IGNORECASE):
                    drop_index.append(idx)
                    break

        df = df.drop(drop_index).reset_index(drop=True)

        # -------------------
        # 4) INSERT OPENING BALANCE BEFORE PREVIEW
        # -------------------
        refined_rows = []
        prev_balance = None

        opening_match = re.search(r"Opening Balance.*?([\d,]+\.\d{2})\s*CR", text_data, re.IGNORECASE)
        if opening_match:
            prev_balance = float(opening_match.group(1).replace(",", ""))
            refined_rows.append({
                "DATE": "",
                "DESCRIPTION": "",
                "CHEQUE NO": "",
                "WITHDRAWALS": "",
                "DEPOSITS": "",
                "BALANCE": ""
            })
        elif not df.empty and df.iloc[0]["BALANCE"]:
            try:
                prev_balance = float(str(df.iloc[0]["BALANCE"]).replace(",", "").replace("CR", "").replace("DR", ""))
                refined_rows.append({
                    "DATE": "",
                    "DESCRIPTION": "",
                    "CHEQUE NO": "",
                    "WITHDRAWALS": "",
                    "DEPOSITS": "",
                    "BALANCE": ""
                })
            except:
                prev_balance = None

        # -------------------
        # 5) PROCESS ROWS WITH LOGIC (Withdrawals / Deposits)
        # -------------------
        for _, row in df.iterrows():
            desc = str(row["DESCRIPTION"]).strip()
            balance = str(row["BALANCE"]).strip()

            # Balance fix (sometimes inside description)
            bal_match = re.search(r"([\d,]+\.\d{2})\s*CR|DR", desc, re.IGNORECASE)
            if bal_match and not balance:
                balance = bal_match.group()

            # Amount detection
            amt_match = re.search(r"([\d,]+\.\d{2})", desc)
            amt = ""
            if amt_match:
                amt = amt_match.group()
                # remove from description
                desc = desc.replace(amt, "", 1).strip()
                
            withdrawals, deposits = "", ""
            if amt and balance:
                try:
                    bal_val = float(balance.replace(",", "").replace("CR", "").replace("DR", ""))
                except:
                    bal_val = None
                amt_val = float(amt.replace(",", ""))

                if prev_balance is not None and bal_val is not None:
                    if bal_val > prev_balance:
                        deposits = amt
                    elif bal_val < prev_balance:
                        withdrawals = amt

                prev_balance = bal_val

            new_row = {
                "DATE": row["DATE"],
                "DESCRIPTION": desc,
                "CHEQUE NO": row["CHEQUE NO"],
                "WITHDRAWALS": withdrawals,
                "DEPOSITS": deposits,
                "BALANCE": balance,
            }
            refined_rows.append(new_row)


        # 6) CLEAN DESCRIPTION (Remove any leading balance/amount text)
        # -------------------
        final_rows = []
        for r in refined_rows:
            desc = r["DESCRIPTION"]

            # Remove leading "xxxxx.xx CR/DR"
            desc = re.sub(r"^\s*[\d,]+\.\d{2}\s*(CR|DR)?\s*", "", desc)

            # Remove leading "xxxxx.xx" (amount)
            desc = re.sub(r"^\s*[\d,]+\.\d{2}\s*", "", desc)

            r["DESCRIPTION"] = desc.strip()
            final_rows.append(r)


        # -------------------
        # 7) EXTRA DESCRIPTION CLEANING (AFTER ALL PROCESSING)
        # -------------------
        cleaned_final_rows = []
        for r in final_rows:
            desc = r["DESCRIPTION"]

            # 1) Remove "Account No ... PIN"
            desc = re.sub(r"Account No.*?\b\d{6}\b", "", desc, flags=re.IGNORECASE)

            # 2) Remove block starting from "From Date" till "Instruments xxxx.xx CR"
            desc = re.sub(r"From Date.*?Instruments\s*\d+,\d+\.\d{2}\s*CR", "", desc, flags=re.IGNORECASE)

            # 3) If "fr" followed by Date/Dr...  remove till "Instruments"
            desc = re.sub(r"fr.*?Date\s+Dr\s+Amount.*?Instruments", "fr", desc, flags=re.IGNORECASE)

            # 4) If after 'fr' there are numbers  remove numbers part
            desc = re.sub(r"fr\s+\d[\d,\. ]+CR?", "fr", desc, flags=re.IGNORECASE)

            # 5) Remove the repeated "Date Dr Amount Cr Amount Total Amount Particulars Instruments"
            desc = re.sub(r"Date\s+Dr\s+Amount\s+Cr\s+Amount\s+Total\s+Amount\s+Particulars\s+Instruments", "", desc, flags=re.IGNORECASE)

            # 6) Remove trailing multiple spaces
            desc = re.sub(r"\s+", " ", desc).strip()

            r["DESCRIPTION"] = desc
            cleaned_final_rows.append(r)

        # -------------------
        # 8) DELETE unwanted rows based on conditions
        # -------------------
        df_final = pd.DataFrame(cleaned_final_rows, columns=columns)

        def should_delete(row):
            desc = str(row["DESCRIPTION"]).strip().lower()
            balance_text = str(row["BALANCE"]).strip().upper()

            # Condition 1: Balance only CR/DR and rest empty
            balance_is_only_crdr = balance_text in ("CR", "DR")
            all_blank = not any([
                str(row["DESCRIPTION"]).strip(),
                str(row["CHEQUE NO"]).strip(),
                str(row["WITHDRAWALS"]).strip(),
                str(row["DEPOSITS"]).strip()
            ])
            cond1 = balance_is_only_crdr and all_blank

            # Condition 2: Description = "fr" and both debit/credit empty
            cond2 = (desc == "fr") and not str(row["WITHDRAWALS"]).strip() and not str(row["DEPOSITS"]).strip()

            return cond1 or cond2

        # Apply filter
        df_final = df_final[~df_final.apply(should_delete, axis=1)].reset_index(drop=True)

        return df_final



    #-------------------SVC Co-Op Bank ----------------------
    def parse_svc_bank_format(self, path):


        # -------------------
        # 0) Handle Password Protected PDF
        # -------------------
        decrypted_pdf = None
        if self.pdf_password:  #  password 
            doc = fitz.open(path)
            if doc.needs_pass:
                if not doc.authenticate(self.pdf_password):
                    raise ValueError("Invalid PDF password for SVC Bank file.")
            #  Temporary decrypted copy 
            tmp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
            os.close(tmp_fd)
            doc.save(decrypted_pdf)
            doc.close()
            path = decrypted_pdf  #  Camelot  decrypted path 

        # -------------------
        # 1) Extract tables from PDF
        # -------------------
        tables = camelot.read_pdf(path, pages="all", flavor="stream")
        if not tables:
            return pd.DataFrame()

        df = tables[0].df  

        # -------------------
        # 2) Fix headers (expected 7 columns)
        # -------------------
        df.columns = ["TRAN DATE", "VALUE DATE", "PARTICULARS", "CHEQUE NO", "DEBIT", "CREDIT", "BALANCE"]

        if df.iloc[0]["TRAN DATE"].lower().startswith("tran"):
            df = df.drop(0).reset_index(drop=True)

        # -------------------
        # 3) Detect Opening Balance from PDF text
        # -------------------
        opening_balance = None
        text_data = ""
        with fitz.open(path) as doc:
            for page in doc:
                text_data += page.get_text("text")

        opening_match = re.search(
            r"Opening Balance as on\s*:\s*\d{2}-[A-Za-z]{3}-\d{4}\s*Rs\.\s*([\d,]+\.\d{2})\s*Cr",
            text_data,
            re.IGNORECASE
        )
        refined_rows = []
        if opening_match:
            opening_balance = float(opening_match.group(1).replace(",", ""))
            refined_rows.append({
                "TRAN DATE": "",
                "VALUE DATE": "",
                "PARTICULARS": "",
                "CHEQUE NO": "",
                "DEBIT": "",
                "CREDIT": "",
                "BALANCE": ""
            })

        # -------------------
        # 4) Merge extracted table rows
        # -------------------
        for _, row in df.iterrows():
            refined_rows.append({
                "TRAN DATE": str(row["TRAN DATE"]).strip(),
                "VALUE DATE": str(row["VALUE DATE"]).strip(),
                "PARTICULARS": str(row["PARTICULARS"]).strip(),
                "CHEQUE NO": str(row["CHEQUE NO"]).strip(),
                "DEBIT": str(row["DEBIT"]).strip(),
                "CREDIT": str(row["CREDIT"]).strip(),
                "BALANCE": str(row["BALANCE"]).strip()
            })

        final_df = pd.DataFrame(
            refined_rows,
            columns=["TRAN DATE", "VALUE DATE", "PARTICULARS", "CHEQUE NO", "DEBIT", "CREDIT", "BALANCE"]
        )

        # -------------------
        # 5) CLEAN ONLY FOR PREVIEW
        # -------------------
        drop_patterns = [
            r"^From:\s*\d{2}-[A-Za-z]{3}-\d{4}\s*To:\s*\d{2}-[A-Za-z]{3}-\d{4}",
            r"Opening Balance as on",
            r"^Total",
            r"^Tran\s*Date",
            r"^Value\s*Date"
        ]

        mask = []
        for _, row in final_df.iterrows():
            row_text = " ".join([str(x).strip() for x in row.values])

            if any(re.search(p, row_text, re.IGNORECASE) for p in drop_patterns):
                mask.append(False)
                continue

            if all(str(x).strip() == "" for x in row.values):
                mask.append(False)
                continue

            mask.append(True)

        preview_df = final_df[mask].reset_index(drop=True)

        # -------------------
        # 6) Delete temporary decrypted file
        # -------------------
        if decrypted_pdf and os.path.exists(decrypted_pdf):
            os.remove(decrypted_pdf)
            
        # -------------------
        # 7) Delete rows containing "Total" in any column
        # -------------------
        def has_total(row):
            for col in ["TRAN DATE", "VALUE DATE", "PARTICULARS", "CHEQUE NO", "DEBIT", "CREDIT"]:
                val = str(row[col]).strip().lower()
                if "total" in val:
                    return True
            return False

        preview_df = preview_df[~preview_df.apply(has_total, axis=1)].reset_index(drop=True)
        return preview_df




    def parse_central_bank_formatTEXT(self, path):

        # -------------------
        # 1) Extract raw text
        # -------------------
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text_data = f.read()

        lines = text_data.split("\n")
        rows = []
        current_row = None
        opening_balance = None
        opening_row_added = False

        # -------------------
        # 2) Regex pattern
        # -------------------
        row_pattern = re.compile(
            r"^(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})\s+(.*?)\s{2,}([\d,]+\.\d{2})?\s*([\d,]+\.\d{2})?\s*([\d,]+\.\d{2}(Cr|Dr))?$"
        )

        skip_patterns = [
            r"Value\s+Date",
            r"Post\s+Date",
            r"Details",
            r"CARRIED FORWARD",
            r"CLOSING BALANCE",
            r"Statement Summary",
            r"Page No",
            r"END OF STATEMENT"
        ]

        garbage_patterns = [
            r"^_{5,}",
            r"Toll Free",
            r"Letter Of Authority",
            r"Account Is Operated",
            r"Check The Transaction",
            r"Date\s+Date"
        ]

        # -------------------
        # 3) Parse each line
        # -------------------
        for line in lines:

            line = line.strip()
            if not line:
                continue

            # Remove garbage
            if any(re.search(p, line, re.IGNORECASE) for p in garbage_patterns):
                continue

            # -------------------
            # Opening Balance
            # -------------------
            if "BROUGHT FORWARD" in line and not opening_row_added:

                ob_match = re.search(r"([\d,]+\.\d{2})(Cr|Dr)", line)

                if ob_match:
                    amount = float(ob_match.group(1).replace(",", ""))
                    typ = ob_match.group(2)

                    if typ == "Dr":
                        amount = -amount

                    rows.append({
                        "VALUE DATE": "",
                        "POST DATE": "",
                        "DETAILS": "OPENING BALANCE",
                        "CHQ NO": "",
                        "DEBIT": "",
                        "CREDIT": "",
                        "BALANCE": amount
                    })

                    opening_balance = amount
                    opening_row_added = True

                continue

            # Skip headers
            if any(re.search(p, line, re.IGNORECASE) for p in skip_patterns):
                continue

            # -------------------
            # Match regular transaction row
            # -------------------
            match = row_pattern.match(line)

            if match:

                if current_row:
                    rows.append(current_row)

                value_date, post_date, details, debit, credit, bal, dc_typ = match.groups()

                clean_balance = None
                if bal:
                    clean_balance = float(bal.replace("Cr", "").replace("Dr", "").replace(",", ""))
                    if dc_typ == "Dr":
                        clean_balance = -clean_balance

                current_row = {
                    "VALUE DATE": value_date,
                    "POST DATE": post_date,
                    "DETAILS": details.strip(),
                    "CHQ NO": "",
                    "DEBIT": debit if debit else "",
                    "CREDIT": credit if credit else "",
                    "BALANCE": clean_balance if clean_balance is not None else ""
                }

            else:
                # -------------------
                # Continuation line
                # -------------------
                if current_row:

                    if "____" in line:
                        continue
                    if "Toll Free" in line:
                        continue

                    clean_line = line.strip().replace("\t", " ")

                    if clean_line:
                        current_row["DETAILS"] += " " + clean_line

        if current_row:
            rows.append(current_row)

        # -------------------
        # 4) Fix Debit/Credit using balance difference
        # -------------------
        prev_balance = None

        for row in rows:
            try:
                bal = float(row["BALANCE"])
            except:
                continue

            if prev_balance is not None:
                diff = bal - prev_balance

                if diff > 0:
                    row["CREDIT"] = f"{diff:,.2f}"
                    row["DEBIT"] = ""
                elif diff < 0:
                    row["DEBIT"] = f"{abs(diff):,.2f}"
                    row["CREDIT"] = ""

            prev_balance = bal

        # -------------------
        # 5) Final cleaning for DETAILS
        # -------------------
        for r in rows:

            d = r["DETAILS"]

            # Remove BROUGHT FORWARD : + amount (Cr/Dr optional)
            d = re.sub(
                r"BROUGHT FORWARD\s*:\s*[\d,]+\.?\d*(Cr|Dr)?",
                "",
                d,
                flags=re.IGNORECASE
            )

            # Remove multiple spaces
            d = " ".join(d.split())

            # Remove control/hide chars
            d = "".join(ch for ch in d if ord(ch) >= 32)

            r["DETAILS"] = d.strip()

        # -------------------
        # 6) Return DataFrame
        # -------------------
        df = pd.DataFrame(
            rows,
            columns=["VALUE DATE", "POST DATE", "DETAILS", "CHQ NO", "DEBIT", "CREDIT", "BALANCE"]
        )

        return df

    # --------- Axis Bank ------------- #
    def parse_axis_bank_format(self, path):
        import camelot
        rows = []
        page_no = 0

        # Read all tables from the PDF using Camelot (with password if provided)
        if self.pdf_password:
            tables = camelot.read_pdf(path, pages="all", strip_text="\n", password=self.pdf_password)
        else:
            tables = camelot.read_pdf(path, pages="all", strip_text="\n")

        for table in tables:
            page_no += 1
            df = table.df  # Convert Camelot table to DataFrame
            for i, row in df.iterrows():
                # Skip header only on the very first page
                if page_no == 1 and i == 0:
                    continue

                # Clean up each cell (remove leading/trailing spaces)
                row = [cell.strip() for cell in row]

                # Skip empty rows or rows containing header-like text
                if not row[0] or row[0].lower().startswith("tran date"):
                    continue

                # Axis Bank format has 7 columns
                if len(row) >= 7:
                    rows.append({
                        "TRAN DATE": row[0],
                        "CHQ/REF NO": row[1],
                        "PARTICULARS": row[2],
                        "DEBIT": row[3],
                        "CREDIT": row[4],
                        "BALANCE": row[5],
                        "INIT BR": row[6],
                    })

        # Combine all extracted rows into a final DataFrame
        df_final = pd.DataFrame(rows)
        return df_final


    # --------- ICICI Bank ------------- #
    def parse_icici_bank_format(self, path):

        rows = []
        page_no = 0

        # Use lattice mode for bordered tables (with password if provided)
        if self.pdf_password:
            tables = camelot.read_pdf(path, pages="all", flavor="lattice", strip_text="\n", password=self.pdf_password)
        else:
            tables = camelot.read_pdf(path, pages="all", flavor="lattice", strip_text="\n")

        for table in tables:
            page_no += 1
            df = table.df  # Convert Camelot table to DataFrame

            for i, row in df.iterrows():
                # Skip header only on the very first page
                if page_no == 1 and i == 0:
                    continue

                # Clean up each cell
                row = [cell.strip() for cell in row]

                # Skip empty or header-like rows
                if not row[0] or row[0].lower().startswith("date"):
                    continue

                # ICICI format has 4 columns
                if len(row) >= 4:
                    # If description is blank but row seems valid, try merging with previous line
                    if not row[1] and rows:
                        rows[-1]["DESCRIPTION"] += " " + row[0]  # merge into last description
                        continue

                    rows.append({
                        "DATE": row[0],
                        "DESCRIPTION": row[1],
                        "AMOUNT": row[2],
                        "TYPE": row[3],   # DR or CR
                    })

        # Convert rows to DataFrame
        df_final = pd.DataFrame(rows)

        # Add DEBIT and CREDIT columns based on TYPE
        df_final["DEBIT"] = df_final.apply(
            lambda x: x["AMOUNT"] if x["TYPE"] == "DR" else "", axis=1
        )
        df_final["CREDIT"] = df_final.apply(
            lambda x: x["AMOUNT"] if x["TYPE"] == "CR" else "", axis=1
        )

        return df_final


    #-------------------Kotak Mahindra Bank--------------------------------


    def parse_kotak_bank_format(self, path):
        rows = []
        current = {}

        with fitz.open(path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            text_data = ""
            for page in doc:
                text_data += page.get_text("text")

        lines = [l.strip() for l in text_data.split("\n") if l.strip()]

        for line in lines:
            # ---- IGNORE unwanted lines (page headers/footers) ----
            if re.match(r"^Page \d+ of \d+", line):
                continue
            if line.strip() == "Date Narration Chq/Ref No Withdrawal(Dr)/ Deposit(Cr) Balance":
                continue

            # ---- Detect new DATE ----
            if re.match(r"\d{2}-\d{2}-\d{4}", line):
                if current.get("DATE") and current.get("BALANCE"):
                    rows.append(current)
                current = {"DATE": line, "NARRATION": "", "CHQ/REF NO": ""}
                continue

            # ---- Detect CHQ/REF NO (UPI-xxxxx etc.) ----
            if re.match(r"UPI-\d+", line):
                current["CHQ/REF NO"] = line
                continue

            # ---- Detect Withdrawal/Deposit ----
            if re.search(r"\d+\.\d{2}\(Dr\)|\d+\.\d{2}\(Cr\)", line) and "WITHDRAWAL/DEPOSIT" not in current:
                current["WITHDRAWAL/DEPOSIT"] = line
                continue

            # ---- Detect Balance ----
            if re.match(r"^\d{1,3}(,\d{3})*\.\d{2}\(Cr\)$", line):
                current["BALANCE"] = line
                continue

            # ---- Narration ----
            if "NARRATION" in current:
                # Extract CHQ/REF NO hidden inside narration
                ref_match = re.search(r"(UPI-\d+)", line)
                if ref_match:
                    current["CHQ/REF NO"] = ref_match.group(1)
                    line = line.replace(ref_match.group(1), "").strip()

                if current["NARRATION"]:
                    current["NARRATION"] += " " + line
                else:
                    current["NARRATION"] = line

        if current.get("DATE") and current.get("BALANCE"):
            rows.append(current)

        # ---- FINAL CLEANUP FOR NARRATION ----
        cleaned_rows = []
        for row in rows:
            narration = row.get("NARRATION", "")

            # remove anything after unwanted markers
            unwanted_markers = [
                "Date Narration Chq/Ref No Withdrawal",
                "Statement Summary",
                "Opening Balance",
                "Total Withdrawal",
                "This is system generated"
            ]
            for marker in unwanted_markers:
                if marker in narration:
                    narration = narration.split(marker)[0].strip()

            # ---- NEW LOGIC: extract last token as CHQ/REF NO if empty ----
            if not row.get("CHQ/REF NO") and narration:
                parts = narration.split()
                if len(parts) > 1:
                    last_token = parts[-1]

                    # check if last_token looks like date (dd-mm-yyyy or dd-mmm-yyyy)
                    is_date_like = bool(
                        re.match(r"^\d{2}-\d{2}-\d{4}$", last_token) or
                        re.match(r"^\d{2}-[A-Za-z]{3}-\d{4}$", last_token)
                    )

                    if not is_date_like and re.match(r"^[A-Za-z0-9\-]+$", last_token):
                        row["CHQ/REF NO"] = last_token
                        narration = " ".join(parts[:-1])

            row["NARRATION"] = narration.strip()
            cleaned_rows.append(row)

        df = pd.DataFrame(
            cleaned_rows,
            columns=["DATE", "NARRATION", "CHQ/REF NO", "WITHDRAWAL/DEPOSIT", "BALANCE"]
        )

        # ---- SPLIT Withdrawal/Deposit into Debit / Credit ----
        df["DEBIT"] = ""
        df["CREDIT"] = ""

        for idx, val in df["WITHDRAWAL/DEPOSIT"].items():
            if pd.isna(val) or not isinstance(val, str):
                continue
            amt = re.sub(r"[^\d.]", "", val)  # ???? ???? ?????
            if amt:
                if val.endswith("(Dr)"):
                    df.at[idx, "DEBIT"] = amt
                elif val.endswith("(Cr)"):
                    df.at[idx, "CREDIT"] = amt

        # ---- REORDER COLUMNS: Debit & Credit in middle ----
        df = df[["DATE", "NARRATION", "CHQ/REF NO", "WITHDRAWAL/DEPOSIT", "DEBIT", "CREDIT", "BALANCE"]]

        return df

    #------------------Bandhan Bank-----------------------

    def parse_bandhan_bank_format(self, path):


        # If the PDF is password protected, unlock it first
        if self.pdf_password:
            reader = PdfReader(path)
            if reader.is_encrypted:
                try:
                    reader.decrypt(self.pdf_password)
                except Exception as e:
                    raise ValueError(f"Wrong PDF password or cannot decrypt: {e}")

                # Create a temporary unlocked PDF file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    writer.write(tmp_file)
                    unlocked_path = tmp_file.name
            else:
                unlocked_path = path
        else:
            unlocked_path = path

        rows = []

        # Extract bordered tables using Camelot in lattice mode
        tables = camelot.read_pdf(
            unlocked_path,
            pages="all",
            flavor="lattice",
            strip_text="\n"
        )

        for table in tables:
            df = table.df  # Convert Camelot table to DataFrame

            for i, row in df.iterrows():
                if i == 0:  # Skip header row
                    continue

                # Clean row (remove spaces, ensure strings)
                row = [str(cell).strip() for cell in row]

                # Skip empty or repeated header rows
                if not row[0] or row[0].lower().startswith("trans"):
                    continue

                # Ensure row has at least 7 columns
                if len(row) >= 7:
                    rows.append({
                        "TRANS DATE": row[0],
                        "VALUE DATE": row[1],
                        "CHQ/REF NO": row[2],
                        "DESCRIPTION": row[3],
                        "DEBITS": row[4],
                        "CREDITS": row[5],
                        "BALANCE": row[6],
                    })

        df_final = pd.DataFrame(rows)

        # Delete temporary unlocked file if created
        if unlocked_path != path:
            os.remove(unlocked_path)

        return df_final

    # ----------------- BANK OF BARODA -----------------

    def parse_bob_format(self, path):


        text_data = ""
        with fitz.open(path) as doc:
            if getattr(self, "pdf_password", None):  # if password is set
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text")

        # Regex for date dd-mm-yy
        date_pattern = re.compile(r"^\d{2}-\d{2}-\d{2}$")

        rows = []
        current_row = None

        for line in text_data.split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if not parts:
                continue

            # --- Case 1: Line starts with a DATE -> New transaction
            if date_pattern.match(parts[0]):
                # Save previous row
                if current_row:
                    rows.append(current_row)

                # Extract date
                date_val = parts[0]

                # Try to extract amounts (withdraw, deposit, balance)
                withdraw, deposit, balance = "", "", ""
                numbers = re.findall(r"[\d,]+\.\d{2}Cr|[\d,]+\.\d{2}Dr|[\d,]+\.\d{2}", line)

                if numbers:
                    if len(numbers) == 1:  # Only balance
                        balance = numbers[0]
                    elif len(numbers) == 2:  # Deposit/Withdrawal + Balance
                        withdraw_or_deposit = numbers[0]
                        balance = numbers[1]
                        # Heuristic: if narration contains 'CR' treat as deposit else withdrawal
                        if "CR" in withdraw_or_deposit.upper():
                            deposit = withdraw_or_deposit
                        else:
                            withdraw = withdraw_or_deposit
                    elif len(numbers) >= 3:  # Withdraw, Deposit, Balance
                        withdraw, deposit, balance = numbers[-3:]

                # Narration cleanup (remove extracted numbers)
                narration = re.sub(r"[\d,]+\.\d{2}(Cr|Dr)?", "", line)
                narration = narration.replace(date_val, "").strip()

                current_row = {
                    "DATE": date_val,
                    "PARTICULARS": narration,
                    "CHQ.NO.": "",
                    "WITHDRAWALS": withdraw,
                    "DEPOSITS": deposit,
                    "BALANCE": balance,
                }

            else:
                # --- Case 2: Continuation line (append to narration)
                if current_row:
                    current_row["PARTICULARS"] += " " + line

        # Add last row
        if current_row:
            rows.append(current_row)

        df = pd.DataFrame(rows)

        # --- Step 2: Fix Withdrawals/Deposits using balance difference ---
        prev_balance = None
        for i in range(len(df)):
            try:
                bal_str = str(df.at[i, "BALANCE"]).replace(",", "").replace("Cr", "").replace("Dr", "")
                bal = float(bal_str)
            except:
                continue

            if prev_balance is not None:
                diff = round(bal - prev_balance, 2)
                if diff > 0:  # Deposit
                    df.at[i, "DEPOSITS"] = f"{diff:,.2f}"
                    df.at[i, "WITHDRAWALS"] = ""  # clear withdrawals
                elif diff < 0:  # Withdrawal
                    df.at[i, "WITHDRAWALS"] = f"{abs(diff):,.2f}"
                    df.at[i, "DEPOSITS"] = ""  # clear deposits

            prev_balance = bal
        # --- Step 3: Cleanup hyphen blocks in PARTICULARS ---
        for i in range(len(df)):
            partic = df.at[i, "PARTICULARS"]
            if "---" in partic:  # check if 3 or more hyphens exist
                # keep only text before first occurrence of ---
                df.at[i, "PARTICULARS"] = partic.split("---", 1)[0].strip()

        # Clean up spaces
       # df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else x)
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else x)
        return df



    # ---------------------BANK OF INDIA ----------------------

    def parse_bank_of_india(self, path):
        text_data = ""
        with fitz.open(path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text") + "\n"

        rows = []
        current_txn = None

        for line in text_data.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Opening Balance
            if line.startswith("|B/F"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                opening_balance = parts[-1] if parts else ""
                rows.append({
                    "DATE": "B/F",
                    "PARTICULARS": "Opening Balance",
                    "INST NO": "",
                    "WITHDRAWALS": "",
                    "DEPOSITS": "",
                    "BALANCE": opening_balance
                })
                continue

            # New Transaction
            if re.match(r"^\|\d{2}-\d{2}-\d{4}\|", line):
                if current_txn:
                    rows.append(current_txn)

                parts = [p.strip() for p in line.split("|") if p.strip()]
                date = parts[0]
                particulars = parts[1] if len(parts) > 1 else ""
                balance = parts[-1] if len(parts) > 2 else ""

                current_txn = {
                    "DATE": date,
                    "PARTICULARS": particulars,
                    "INST NO": "",
                    "WITHDRAWALS": "",
                    "DEPOSITS": "",
                    "BALANCE": balance
                }
            else:
                # continuation line
                if current_txn:
                    current_txn["PARTICULARS"] += " " + line

        if current_txn:
            rows.append(current_txn)

        # --- Balance Difference Logic ---
        final_rows = []
        last_balance = None
        for row in rows:
            bal_str = row["BALANCE"].replace("Cr", "").replace(",", "").strip()
            try:
                balance = float(bal_str)
            except:
                balance = None

            if row["DATE"] == "B/F":
                last_balance = balance
                final_rows.append(row)
                continue

            if last_balance is not None and balance is not None:
                diff = balance - last_balance
                if diff < 0:
                    row["WITHDRAWALS"] = f"{abs(diff):.2f}"
                    row["DEPOSITS"] = ""
                elif diff > 0:
                    row["DEPOSITS"] = f"{diff:.2f}"
                    row["WITHDRAWALS"] = ""
            last_balance = balance
            final_rows.append(row)

        df = pd.DataFrame(final_rows)

        # --- Clean up PARTICULARS (remove footers, TDS etc.) ---
        for row in final_rows:
            if "----" in row["PARTICULARS"]:
                cut_index = row["PARTICULARS"].find("----")
                row["PARTICULARS"] = row["PARTICULARS"][:cut_index].strip()

        df = pd.DataFrame(final_rows)


        return df

    def parse_bank_excel(self, path, sheet_name="Bank Format"):
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(path, sheet_name=sheet_name)

        # Clean up columns: rename columns for internal consistency
        df = df.rename(columns={
            "Date": "VALUE DATE",
            "Narration": "DETAILS",
            "Chq./Ref.No.": "CHQ NO",
            "Value Dt": "POST DATE",
            "Withdrawal Amt.": "DEBIT",
            "Deposit Amt.": "CREDIT",
            "Closing Balance": "BALANCE"
        })

        # Missing values: Replace NaN/missing values with an empty string ("")
        # This crucial step ensures initial blank cells are handled as empty strings globally.
        df = df.fillna("") 

        # Debit/Credit numeric: Convert financial columns to numeric, handling non-numeric data
        for col in ["DEBIT", "CREDIT", "BALANCE"]:
            # If the value is not empty, try to convert it to a number (coercing errors to NaN if conversion fails)
            df[col] = df[col].apply(lambda x: pd.to_numeric(x, errors='coerce') if x != "" else "")

        # --- LOGIC TO FORMAT VALUE DATE and POST DATE TO DD/MM/YYYY ---
        # This section updates ONLY the specified date columns, leaving the rest of the DataFrame intact.
        date_columns = ["VALUE DATE", "POST DATE"] 
        
        for col in date_columns:
            # 1. Convert the column to datetime objects. Existing empty strings ("") are treated as NaT.
            #    Non-date/invalid values are also converted to NaT (Not a Time).
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 2. Format the valid datetime objects to the required DD/MM/YYYY string format (automatically removes the time component).
            #    NaT values are converted into the string 'NaT'.
            df[col] = df[col].dt.strftime('%d/%m/%Y')
            
            # 3. CRITICAL STEP: Replace the resulting 'NaT' strings (from initial blank/invalid dates) with an empty string ("").
            #    This ensures your blank cells remain BLANK and not 'NaT'.
            df[col] = df[col].replace('NaT', '') 
        # --- END OF DATE FORMATTING LOGIC ---
        df = df.fillna("") 
        # Return the entire DataFrame with the formatted date columns
        return df  

    # ------------------- ICICI BANK -------------------
    def parse_icici_bank_format1(self, path):

        # Step 1: Handle password-protected PDF
        decrypted_pdf = None
        if getattr(self, "pdf_password", None):
            doc = fitz.open(path)
            if doc.needs_pass:
                ok = doc.authenticate(self.pdf_password)
                if not ok:
                    raise ValueError("Incorrect PDF password")

            temp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
            os.close(temp_fd)
            doc.save(decrypted_pdf)
            doc.close()
            path = decrypted_pdf

        # Step 2: Extract raw text
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n"
        doc.close()

        if decrypted_pdf and os.path.exists(decrypted_pdf):
            os.remove(decrypted_pdf)

        # Step 3: Split & clean lines
        lines = [l.strip() for l in full_text.split("\n") if l.strip()]
        date_regex = r"\b\d{2}-\d{2}-\d{4}\b"

        rows = []
        current_date = ""
        particulars_accum = []
        deposit_val = ""
        withdrawal_val = ""
        balance_val = ""
        first_amount_seen = False

        def push_record():
            """Push one completed row into the rows list"""
            nonlocal rows, current_date, particulars_accum, deposit_val, withdrawal_val, balance_val, first_amount_seen
            if current_date:
                rows.append({
                    "DATE": current_date,
                    "PARTICULARS": " ".join(particulars_accum).strip(),
                    "DEPOSITS": deposit_val,
                    "WITHDRAWALS": withdrawal_val,
                    "BALANCE": balance_val
                })
            particulars_accum = []
            deposit_val = ""
            withdrawal_val = ""
            balance_val = ""
            first_amount_seen = False

        # Step 4: Parsing logic - Modified for blank row fix
        for line in lines:

            date_match = re.search(date_regex, line)

            if date_match:
                before = line.split(date_match.group())[0].strip()
                after = line.split(date_match.group())[1].strip()

                # FIX 1: If the line contains date inside description (like Int.Pd:30-06-2024),
                # it should NOT start a new transaction. Treat as particulars.
                if any(desc_part in line for desc_part in ["Int.Pd:", "EMI", "BILL", "NEFT", "RTGS", "UPI"]):
                    if current_date:
                        particulars_accum.append(line)
                        continue

                # Case: DATE + TEXT → same transaction (append to particulars)
                if before == "" and after != "":
                    if not current_date:
                        current_date = date_match.group()
                    particulars_accum.append(after)
                    continue

                # Case: DATE only → new transaction row
                push_record()
                current_date = date_match.group()

                # If there is text after date, add it into particulars
                if after:
                    particulars_accum.append(after)

                continue

            # Opening balance case
            if line.upper() == "B/F":
                particulars_accum.append("B/F")
                continue

            # Numeric values detection
            amounts = re.findall(r"[0-9,]+\.\d{2}", line)

            if amounts:

                # B/F → only balance
                if "B/F" in particulars_accum:
                    balance_val = amounts[0]
                    continue

                # First amount = deposit/withdrawal
                if not first_amount_seen:
                    deposit_val = amounts[0]
                    first_amount_seen = True

                    # If only one amount, treat it as withdrawal
                    if len(amounts) == 1:
                        withdrawal_val = amounts[0]
                        deposit_val = ""
                    continue

                # Second amount = balance
                if len(amounts) >= 1 and not balance_val:
                    balance_val = amounts[0]
                    continue

            # Normal particulars text
            particulars_accum.append(line)

        push_record()

        df = pd.DataFrame(rows)

        # ---------------------------------------------------
        # POST-STEP 1: Clear deposits & withdrawals and recalc using BALANCE difference
        # ---------------------------------------------------
        df["DEPOSITS"] = ""
        df["WITHDRAWALS"] = ""

        prev_bal = None
        for i in range(len(df)):
            try:
                # Convert balance safely, handling NaN and commas
                bal_str = str(df.loc[i, "BALANCE"]).replace(",", "") if pd.notna(df.loc[i, "BALANCE"]) else ""
                bal = float(bal_str) if bal_str else None
            except ValueError:
                bal = None

            if prev_bal is None:
                prev_bal = bal
                continue

            # Compute difference
            if bal is not None and prev_bal is not None:
                diff = bal - prev_bal
                if diff > 0:
                    df.loc[i, "DEPOSITS"] = f"{diff:.2f}"
                elif diff < 0:
                    df.loc[i, "WITHDRAWALS"] = f"{abs(diff):.2f}"

            prev_bal = bal

        # ---------------------------------------------------
        # POST-STEP 2: Remove "Page X of Y" and everything after it from particulars
        # ---------------------------------------------------
        df["PARTICULARS"] = df["PARTICULARS"].apply(
            lambda x: re.split(r"Page\s+\d+\s+of\s+\d+", x)[0].strip()
        )

        # ---------------------------------------------------
        # POST-STEP 3: Remove TOTAL number blocks from particulars
        # ---------------------------------------------------
        def clean_total_block(text):
            text = re.sub(r"TOTAL\s+[0-9,]+\.\d{2}\s+[0-9,]+\.\d{2}.*", "", text)
            return text.strip()

        df["PARTICULARS"] = df["PARTICULARS"].apply(clean_total_block)

        return df

    # ------------------- Abhyudaya Co-Operative Bank Limited -------------------
    def parse_abhyudaya_bank_format(self, path):


        # --- ✅ Step 0: Handle password-protected PDF ---
        decrypted_pdf = None
        if getattr(self, "pdf_password", None):  # if password is provided
            doc = fitz.open(path)
            if doc.needs_pass:
                if not doc.authenticate(self.pdf_password):
                    raise ValueError("Invalid PDF password for Abhyudaya Bank file.")
                # Create temporary decrypted copy
                tmp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
                os.close(tmp_fd)
                doc.save(decrypted_pdf)
                doc.close()
                path = decrypted_pdf  # Use decrypted file for Camelot
            else:
                doc.close()

        # --- Step 1: Extract tables from PDF ---
        tables = camelot.read_pdf(path, pages="all", flavor="stream")

        if not tables:
            return pd.DataFrame(columns=[
                "DATE", "PARTICULARS", "CHQ/REF NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"
            ])

        all_rows = []

        # --- Step 2: Loop through tables and collect rows ---
        for t in tables:
            df = t.df.copy()
            df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")

            # Drop header or unwanted first lines (like "Transaction Date" etc.)
            header_idx = -1
            for i, row in df.iterrows():
                row_text = " ".join(row).lower()
                if "transaction" in row_text and "date" in row_text:
                    header_idx = i
                    break

            if header_idx >= 0:
                df = df.iloc[header_idx + 1:].reset_index(drop=True)

            # --- Merge narration lines (handle multi-line particulars) ---
            merged_rows = []
            temp = []
            for _, row in df.iterrows():
                line_text = " ".join(row).strip()

                # If first column is a date → new transaction starts
                if re.match(r"^\d{2}/\d{2}/\d{4}", row[0]):
                    if temp:
                        merged_rows.append(temp)
                        temp = []
                    temp = list(row)
                else:
                    # continuation line (append to particulars)
                    if temp:
                        temp[1] += " " + line_text
                    else:
                        temp = list(row)

            # add last transaction (important)
            if temp:
                merged_rows.append(temp)

            # Convert merged rows to proper structure
            for r in merged_rows:
                while len(r) < 6:
                    r.append("")

                all_rows.append({
                    "DATE": r[0],
                    "PARTICULARS": r[1],
                    "CHQ/REF NO": r[2],
                    "WITHDRAWALS": r[3],
                    "DEPOSITS": r[4],
                    "BALANCE": r[5]
                })

        df_final = pd.DataFrame(all_rows)

        # --- Step 3: Cleanup ---
        df_final = df_final.map(lambda x: str(x).strip() if pd.notnull(x) else "")

        # --- Step 4: Remove unwanted header/footer rows ---
        drop_patterns = [
            r"account summary", r"transaction summary",
            r"bank statement", r"abhyudaya", r"transaction details",
            r"statement of account"
        ]

        cleaned_rows = []
        for _, row in df_final.iterrows():
            text = " ".join(row.values).lower()

            # Skip empty rows
            if all(str(v).strip() == "" for v in row.values):
                continue

            # Skip unwanted header/footer lines
            if any(re.search(p, text) for p in drop_patterns):
                continue

            # Skip rows that start with opening/closing/total
            if re.match(r"^(opening|closing|total)", text.strip()):
                continue

            cleaned_rows.append(row)

        df_final = pd.DataFrame(cleaned_rows).reset_index(drop=True)

        # --- Step 5: Final column order ---
        df_final = df_final[["DATE", "PARTICULARS", "CHQ/REF NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]]

        # --- ✅ Step 6: Replace '-' with blank in Withdrawals/Deposits ---
        df_final["WITHDRAWALS"] = df_final["WITHDRAWALS"].apply(lambda x: "" if x.strip() in ["-", "–"] else x)
        df_final["DEPOSITS"] = df_final["DEPOSITS"].apply(lambda x: "" if x.strip() in ["-", "–"] else x)

        # --- ✅ Step 7: Clean Narration (remove trailing totals or balance text) ---
        def clean_narration(text):
            if not isinstance(text, str):
                return text
            # Remove text starting from "Total Amount" or "Closing Balance"
            text = re.split(r"(Total\s*Amount|Closing\s*Balance)", text, flags=re.IGNORECASE)[0]
            # Remove extra spaces
            return text.strip()

        df_final["PARTICULARS"] = df_final["PARTICULARS"].apply(clean_narration)

        # --- ✅ Step 8: Delete temp decrypted file if created ---
        if decrypted_pdf and os.path.exists(decrypted_pdf):
            os.remove(decrypted_pdf)

        return df_final

    # ------------------- CANARA BANK -------------------
    def parse_canara_bank_format(self, path):

        warnings.filterwarnings("ignore")

        # --- Step 1: Handle password protected PDF ---
        temp_path = path
        try:
            with fitz.open(path) as doc:
                if getattr(self, "pdf_password", None):
                    doc.authenticate(self.pdf_password)
                temp_path = "temp_canara.pdf"
                doc.save(temp_path)
        except Exception as e:
            print("PDF open error:", e)

        # --- Step 2: Extract tables using Camelot ---
        tables = camelot.read_pdf(temp_path, pages="all", flavor="stream")
        if not tables:
            return pd.DataFrame(columns=[
                "TRANS DATE", "VALUE DATE", "BRANCH", "CHQ/REF NO",
                "DESCRIPTION", "WITHDRAWALS", "DEPOSIT", "BALANCE"
            ])

        all_rows = []

        # --- Step 3: Parse tables ---
        for t in tables:
            df = t.df.copy()
            df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")

            # Find header
            header_idx = -1
            for i, row in df.iterrows():
                row_text = " ".join(row).lower()
                if "trans" in row_text and "value" in row_text:
                    header_idx = i
                    break
            if header_idx >= 0:
                df = df.iloc[header_idx + 1:].reset_index(drop=True)

            merged_rows = []
            temp = None

            # --- Step 4: Merge rows and balance logic (BALANCE FIX ONLY) ---
            for idx, row in df.iterrows():
                r = list(row) + [""] * (8 - len(row))

                is_new_txn = re.match(r"^\d{2}-[A-Z]{3}-\d{2,4}", r[0]) or re.match(r"^\d{2}-\d{2}-\d{2,4}", r[0])
                is_bf_row = "B/F" in r[3] # FIX 1: B/F row olakha
                current_balance = r[7] # Current row madhla balance

                # ✅ Case 1: New transaction (Modified to include B/F logic)
                if is_new_txn or is_bf_row: # FIX 1: is_bf_row add kela
                    if temp:
                        # FIX 2: Previous transaction append karnyapurvi final balance check
                        if current_balance and not temp[7]:
                            temp[7] = current_balance
                            
                        # Last balance check in entire row if balance still missing
                        last_balance = next((x for x in reversed(temp) if re.match(r"^-?[\d,]+\.\d{2}$", str(x).strip()) and x.strip()), None)
                        if last_balance and not temp[7]:
                            temp[7] = last_balance
                            
                        merged_rows.append(temp)
                    temp = r

                # ✅ Case 2: Row contains only balance pattern (no date, short row)
                elif temp and re.match(r"^-?[\d,]+\.\d{2}$", r[0]):
                    temp[7] = r[0]  # balance column fill
                elif temp and re.match(r"^-?[\d,]+\.\d{2}$", r[-1]):
                    temp[7] = r[-1]

                # ✅ Case 3: Continuation of narration
                elif temp:
                    # FIX 3: Continuation row madhe jar r[7] madhe balance asel tar to set kara
                    if current_balance:
                        temp[7] = current_balance 
                        
                    line_text = " ".join(r).strip()
                    temp[4] += " " + line_text
                    
                    # search for last amount pattern that could be balance
                    bal_match = re.findall(r"-?[\d,]+\.\d{2}", line_text)
                    if bal_match:
                        possible_bal = bal_match[-1]
                        # if last column empty and amount seems large, assign to balance
                        # FIX: Check if temp[7] is empty BEFORE assigning
                        if not temp[7] and (len(possible_bal) >= 4 or "-" in possible_bal):
                            temp[7] = possible_bal

                # ✅ Always push last row (Modified for final balance check)
                if idx == len(df) - 1 and temp:
                    # FIX 4: Ensure final balance is captured for the very last transaction
                    if current_balance and not temp[7]:
                        temp[7] = current_balance
                        
                    last_balance = next((x for x in reversed(temp) if re.match(r"^-?[\d,]+\.\d{2}$", str(x).strip()) and x.strip()), None)
                    if last_balance and not temp[7]:
                        temp[7] = last_balance
                        
                    merged_rows.append(temp)

            for r in merged_rows:
                all_rows.append({
                    "TRANS DATE": r[0],
                    "VALUE DATE": r[1],
                    "BRANCH": r[2],
                    "CHQ/REF NO": r[3],
                    "DESCRIPTION": r[4],
                    "WITHDRAWALS": r[5],
                    "DEPOSIT": r[6],
                    "BALANCE": r[7],
                })

        df_final = pd.DataFrame(all_rows)

        # --- Step 5: Remove unwanted headers/footers ---
        drop_patterns = [
            r"internal", r"page\s*\d+", r"ombudsman", r"clear balance",
            r"central vista", r"fort glacis", r"details of ombudsman"
        ]
        cleaned_rows = []
        for _, row in df_final.iterrows():
            text = " ".join(row.values).lower()
            has_date = re.search(r"\d{2}-[A-Z]{3}-\d{2,4}", text) or re.search(r"\d{2}-\d{2}-\d{2,4}", text)
            has_amount = re.search(r"[\d,]+\.\d{2}", text)
            if any(re.search(p, text) for p in drop_patterns):
                if not (has_date or has_amount):
                    continue
            if all(str(v).strip() == "" for v in row.values):
                continue
            cleaned_rows.append(row)

        df_final = pd.DataFrame(cleaned_rows).reset_index(drop=True)

        # --- Step 6: Delete “DATE” rows and headers ---
        df_final = df_final[
            ~df_final["TRANS DATE"].str.contains("date", case=False, na=False) &
            ~df_final["VALUE DATE"].str.contains("date", case=False, na=False)
        ]

        # --- Step 7: Remove extra rows ---
        df_final = df_final[~df_final["BRANCH"].str.contains("statement of account", case=False, na=False)]

        if any(df_final["TRANS DATE"].str.contains("Statement Summary", case=False, na=False)):
            idx = df_final[df_final["TRANS DATE"].str.contains("Statement Summary", case=False, na=False)].index[0]
            df_final = df_final.iloc[:idx].reset_index(drop=True)

        # --- Step 8: Replace “–” or “0.00” ---
        for col in ["WITHDRAWALS", "DEPOSIT"]:
            df_final[col] = df_final[col].apply(lambda x: "" if str(x).strip() in ["-", "–", "0.00"] else x)

        # --- Step 9: Clean narration ---
        df_final["DESCRIPTION"] = df_final["DESCRIPTION"].apply(lambda x: re.sub(r"\s+", " ", x).strip())

        # --- Step 10: Balance cleanup ---
        # df_final["BALANCE"] = df_final["BALANCE"].apply(lambda x: re.sub(r"[^\d\-,\.]", "", x).strip() if x else "")

        # df_final = df_final.map(lambda x: str(x).strip() if pd.notnull(x) else "")

        if os.path.exists("temp_canara.pdf"):
            os.remove("temp_canara.pdf")          

        return df_final

    # ------------------- COSMOS CO-OP BANK LTD -------------------
    def parse_cosmos_bank_format(self, path):

        warnings.filterwarnings("ignore") # NEW WARNINGS FILTER

        # --- Step 0: Handle password protected PDF (NEW BLOCK) ---
        temp_path = path
        final_path = path 
        try:
            with fitz.open(path) as doc:
                if getattr(self, "pdf_password", None):
                    # Check if authentication is needed and try to authenticate
                    if doc.needs_pass:
                        # doc.authenticate returns non-zero if successful
                        if doc.authenticate(self.pdf_password) > 0: 
                            temp_path = "temp_cosmos.pdf"
                            # Save the decrypted file temporarily
                            doc.save(temp_path)
                            final_path = temp_path
                        # else: PDF is password-protected and authentication failed.
                # else: No password provided, use original path

        except Exception as e:
            # Handle cases where the PDF file might not exist or other issues
            print("PDF pre-processing error:", e)
            final_path = path # Default back to path if an error occurs
        
        # --- Step 1: Read PDF text (Modified to use final_path) ---
        text = ""
        # Use final_path, which is either the original file or the decrypted temp file
        try:
            with fitz.open(final_path) as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
             # Handle read error (e.g., failed authentication)
             print(f"Error reading PDF content: {e}")
             # Return empty DataFrame if critical read fails
             return pd.DataFrame() 

        # --- Step 2: Split and clean lines ---
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        all_rows = []
        temp_row = None
        date_pattern = re.compile(r"^\d{2}[-−]\d{2}[-−]\d{4}")  # e.g. 16−09−2025
        opening_balance = None  # 🟢 For Step 9

        # --- Step 3: Parse each line ---
        for line in lines:
            # ✅ Case 1: New Transaction
            if date_pattern.match(line):
                if temp_row and temp_row.get("TRANS DATE") and not temp_row.get("VALUE DATE"):
                    # If Value Date is missing, append the previous row.
                    all_rows.append(temp_row)

                parts = re.split(r"\s{2,}", line)
                parts = [p.strip() for p in parts if p.strip()]

                trans_date = parts[0]
                particulars = ""
                chq_no = ""
                withdrawals = ""
                deposits = ""
                balance = ""

                # Extract Dr/Cr balance (keep original format)
                bal_match = re.search(r"([\d,]+\.\d{2}\s*(Dr|Cr))", line, re.IGNORECASE)
                if bal_match:
                    balance = bal_match.group(1).replace(" ", "")

                # Find numeric amounts
                nums = re.findall(r"[\d,]+\.\d{2}", line)
                if len(nums) == 1:
                    withdrawals = nums[0]
                elif len(nums) == 2:
                    withdrawals = nums[0]
                    deposits = nums[1]
                elif len(nums) == 3:
                    withdrawals, deposits, _ = nums[:3]

                # Clean narration
                desc = re.sub(r"[\d,]+\.\d{2}\s*(Dr|Cr)?", "", line)
                desc = re.sub(r"^\d{2}[-−]\d{2}[-−]\d{4}", "", desc).strip()

                temp_row = {
                    "TRANS DATE": trans_date,
                    "VALUE DATE": "",
                    "PARTICULARS": desc,
                    "CHQ/NO": chq_no,
                    "WITHDRAWALS": withdrawals,
                    "DEPOSITS": deposits,
                    "BALANCE": balance,
                }

            # ✅ Case 2: Second line (Value Date only)
            elif temp_row and temp_row["VALUE DATE"] == "" and date_pattern.match(line):
                # This line only contains the date as Value Date, so populate Value Date.
                temp_row["VALUE DATE"] = line.split()[0]
                all_rows.append(temp_row) # Append the complete row
                temp_row = None # Reset temp_row

            # ✅ Case 3: Opening Balance line (Line containing only balance)
            elif not date_pattern.match(line):
                bal_only = re.findall(r"([\d,]+\.\d{2}\s*(Dr|Cr))", line, re.IGNORECASE)
                if bal_only and not opening_balance:
                    opening_balance = bal_only[0][0].replace(" ", "")

        # Add last pending
        if temp_row:
            all_rows.append(temp_row)

        # --- Step 4: Create DataFrame ---
        df = pd.DataFrame(all_rows)

        # --- Step 5: Clean up ---
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        df = df[df["TRANS DATE"].str.match(r"\d{2}[-−]\d{2}[-−]\d{4}", na=False)]

        # --- Step 6: Replace empty with blanks ---
        for col in ["WITHDRAWALS", "DEPOSITS", "BALANCE"]:
            df[col] = df[col].replace("nan", "").replace("None", "")

        # --- Step 7: Remove headers and junk lines ---
        df = df[~df["PARTICULARS"].str.contains("Statement of Account", case=False, na=False)]
        df = df[~df["TRANS DATE"].str.contains("Tran Date", case=False, na=False)]

        # --- ✅ Step 8: Merge value-date rows intelligently ---
        merged_rows = []
        skip_next = False
        for i in range(len(df)):
            if skip_next:
                skip_next = False
                continue

            current = df.iloc[i]
            if i + 1 < len(df):
                nxt = df.iloc[i + 1]
                if (
                    current["BALANCE"] != "" and  # This row has a balance
                    nxt["BALANCE"] == "" and  # Next row has no balance
                    nxt["PARTICULARS"] == "" and  # Next narration is empty
                    re.match(r"^\d{2}[-−]\d{2}[-−]\d{4}", nxt["TRANS DATE"]) # Next line is a date pattern
                ):
                    current["VALUE DATE"] = nxt["TRANS DATE"]
                    skip_next = True # Skip the next row

            merged_rows.append(current)

        df = pd.DataFrame(merged_rows).reset_index(drop=True)

        # --- ✅ Step 9: Add Opening Balance Row ---
        if opening_balance:
            opening_row = {
                "TRANS DATE": "OPENING",
                "VALUE DATE": "",
                "PARTICULARS": "Opening Balance",
                "CHQ/NO": "",
                "WITHDRAWALS": "",
                "DEPOSITS": "",
                "BALANCE": opening_balance,
            }
            df = pd.concat([pd.DataFrame([opening_row]), df], ignore_index=True)


        # -----------------------------------------------------
        # --- ✅ Step 10: Recalculate WDL/DEP based on Balance Difference (NEW LOGIC) ---
        # -----------------------------------------------------

        # 1. Helper function to clean and standardize the balance
        def clean_balance(balance_str):
            """Converts balance string (e.g., '14,32,977.77Dr') to float and returns type (Dr/Cr)."""
            if not isinstance(balance_str, str) or not balance_str.strip():
                return 0.0, None
            
            balance_str = balance_str.replace(',', '').strip()
            
            balance_type = None
            if balance_str.endswith('Dr'):
                balance_type = 'Dr'
                value = balance_str[:-2]
            elif balance_str.endswith('Cr'):
                balance_type = 'Cr'
                value = balance_str[:-2]
            else:
                value = balance_str
                
            try:
                # Use a negative value for Dr balances for calculation simplicity if needed, 
                # but here we rely on type and absolute value as per Step 10 logic.
                return float(value), balance_type
            except ValueError:
                return 0.0, None

        # 2. Clear existing WDL/DEP data
        df["WITHDRAWALS"] = ""
        df["DEPOSITS"] = ""
        
        # 3. Iterate and recalculate WDL/DEP from the second row (i=1)
        for i in range(1, len(df)):
            
            # Get Previous and Current Balance values and types
            prev_value, prev_type = clean_balance(df.loc[i-1, 'BALANCE'])
            curr_value, curr_type = clean_balance(df.loc[i, 'BALANCE'])

            # Only proceed if both balances are valid and of the same type 
            if prev_type is None or curr_type is None or prev_type != curr_type:
                # Type change (Cr to Dr or vice versa) or invalid data. 
                # Skipping recalculation when balance type changes or is invalid.
                continue 
            
            # Calculate the absolute difference
            diff_amount = abs(curr_value - prev_value)
            
            # Check if there was any actual difference
            if diff_amount == 0:
                continue
                
            # Format difference to two decimal places
            formatted_diff = "{:,.2f}".format(diff_amount)
            
            # --- APPLY USER'S LOGIC ---
            
            if prev_type == 'Dr':
                # Rule for Dr Account: WDL = Increase in debt, DEP = Decrease in debt
                
                if curr_value > prev_value:
                    # Balance increased (debt increased) -> WITHDRAWAL
                    df.loc[i, 'WITHDRAWALS'] = formatted_diff
                elif curr_value < prev_value:
                    # Balance decreased (debt decreased) -> DEPOSIT
                    df.loc[i, 'DEPOSITS'] = formatted_diff
                    
            elif prev_type == 'Cr':
                # Rule for Cr Account: DEP = Increase in asset, WDL = Decrease in asset
                
                if curr_value > prev_value:
                    # Balance increased (asset increased) -> DEPOSIT
                    df.loc[i, 'DEPOSITS'] = formatted_diff
                elif curr_value < prev_value:
                    # Balance decreased (asset decreased) -> WITHDRAWAL
                    df.loc[i, 'WITHDRAWALS'] = formatted_diff

        # --- Final Cleanup: Delete temp file (NEW) ---
        if os.path.exists("temp_cosmos.pdf"):
             os.remove("temp_cosmos.pdf")
             
        return df
    # -----------------------DCB BANK --------------------------

    def parse_dcb_bank_format(self, path):

        warnings.filterwarnings("ignore")

        temp_path = path
        try:
            with fitz.open(path) as doc:
                if getattr(self, "pdf_password", None):
                    doc.authenticate(self.pdf_password)
                temp_path = "temp_dcb.pdf"
                doc.save(temp_path)
        except Exception as e:
            print("PDF open error:", e)

        # --- Step 1: Extract using lattice (preserves merged cells) ---
        tables = camelot.read_pdf(
            temp_path, pages="all", flavor="lattice", strip_text='\n', line_scale=40
        )

        if not tables:
            return pd.DataFrame(columns=[
                "DATE", "PARTICULARS", "CHQ/REF NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"
            ])

        all_rows = []

        for t in tables:
            df = t.df.copy()
            df = df.map(lambda x: str(x).replace('\n', ' ').strip() if pd.notnull(x) else "")

            # Header detection
            header_idx = -1
            for i, row in df.iterrows():
                row_text = " ".join(row).lower()
                if "transaction" in row_text and "balance" in row_text:
                    header_idx = i
                    break
            if header_idx >= 0:
                df = df.iloc[header_idx + 1:].reset_index(drop=True)

            if df.shape[1] > 6:
                df = df.iloc[:, :6]
            elif df.shape[1] < 6:
                for _ in range(6 - df.shape[1]):
                    df[f"extra{_}"] = ""

            df.columns = ["DATE", "PARTICULARS", "CHQ/REF NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]

            merged_rows = []
            temp = None
            for _, row in df.iterrows():
                date_val = str(row["DATE"]).strip() if pd.notnull(row["DATE"]) else ""
                is_new_txn = (
                    re.match(r"^\d{2}-\d{2}-\d{4}$|^\d{2}-[A-Z]{3}-\d{2,4}$", date_val)
                    or "opening balance" in date_val.lower()
                    or "closing balance" in date_val.lower()
                )

                if bool(is_new_txn):
                    if temp is not None:
                        merged_rows.append(temp)
                    temp = row.copy()
                elif temp is not None:
                    temp["PARTICULARS"] += " " + row["PARTICULARS"].strip()
                    if not str(temp["WITHDRAWALS"]).strip():
                        temp["WITHDRAWALS"] = row["WITHDRAWALS"]
                    if not str(temp["DEPOSITS"]).strip():
                        temp["DEPOSITS"] = row["DEPOSITS"]
                    if not str(temp["BALANCE"]).strip():
                        temp["BALANCE"] = row["BALANCE"]
                else:
                    temp = row.copy()

            if temp is not None:
                merged_rows.append(temp)

            all_rows.extend(merged_rows)

        df_final = pd.DataFrame(all_rows)

        # --- Step 4: Remove unwanted header/footer rows ---
        drop_patterns = [
            r"page\s*\d+", r"statement of account", r"dcb bank", r"for clarification",
            r"registered office", r"customer care", r"gst invoice", r"nominee details", r"end of statement"
        ]
        cleaned_rows = []
        for _, row in df_final.iterrows():
            text = " ".join(row.values).lower()
            if any(re.search(p, text) for p in drop_patterns):
                continue
            if all(str(v).strip() == "" for v in row.values):
                continue
            cleaned_rows.append(row)
        df_final = pd.DataFrame(cleaned_rows).reset_index(drop=True)

        # --- Step 5: Clean columns but preserve exact text ---
        for col in ["WITHDRAWALS", "DEPOSITS", "BALANCE"]:
            df_final[col] = df_final[col].astype(str).str.replace(",", "").str.strip()

        df_final["PARTICULARS"] = df_final["PARTICULARS"].apply(
            lambda x: re.sub(r"\s+", " ", x).strip()
        )

        if os.path.exists("temp_dcb.pdf"):
            os.remove("temp_dcb.pdf")
            
        # --- Step 6: Remove rows before 'Opening Balance' & trim narration after 'Closing' ---
        if not df_final.empty:
            # 6A → Delete all rows before & including 'Opening Balance'
            idx_list = df_final.index[
                df_final["PARTICULARS"].str.contains("Opening Balance", case=False, na=False)
            ].tolist()
            if idx_list:
                first_idx = idx_list[0]
                # remove that row also (hence first_idx + 1)
                df_final = df_final.iloc[first_idx + 1:].reset_index(drop=True)

            # 6B → Trim narration after 'Closing'
            def clean_closing_text(text):
                txt = str(text)
                if "Closing" in txt:
                    # keep only text before 'Closing'
                    txt = txt.split("Closing")[0].strip()
                return txt
            df_final["PARTICULARS"] = df_final["PARTICULARS"].apply(clean_closing_text)

        # --- Step 7: Remove rows after 'GST Number' line in DATE column ---
        if not df_final.empty:
            gst_idx_list = df_final.index[
                df_final["DATE"].str.contains("GST Number", case=False, na=False)
            ].tolist()
            if gst_idx_list:
                gst_idx = gst_idx_list[0]
                df_final = df_final.iloc[:gst_idx].reset_index(drop=True)



        # --------------------- Step 8 -------------------------------
        # Auto-correct rows having both Withdrawal and Deposit values
        # by comparing current and previous balances:
        # - If balance increased → fill Deposit column with difference
        # - If balance decreased → fill Withdrawal column with difference
        # The opposite column is cleared in each case.
        # ============================================================

        if not df_final.empty and "BALANCE" in df_final.columns:
            try:
                df_final["BALANCE"] = pd.to_numeric(df_final["BALANCE"], errors="coerce")

                for i in range(1, len(df_final)):
                    w = str(df_final.at[i, "WITHDRAWALS"]).strip()
                    d = str(df_final.at[i, "DEPOSITS"]).strip()

                    # Only process rows where both columns contain numbers
                    if re.search(r"\d", w) and re.search(r"\d", d):
                        prev_bal = df_final.at[i - 1, "BALANCE"] if pd.notnull(df_final.at[i - 1, "BALANCE"]) else 0
                        curr_bal = df_final.at[i, "BALANCE"] if pd.notnull(df_final.at[i, "BALANCE"]) else 0
                        diff = round(curr_bal - prev_bal, 2)

                        # Balance increased → Deposit difference
                        if diff > 0:
                            df_final.at[i, "DEPOSITS"] = f"{abs(diff):.2f}"
                            df_final.at[i, "WITHDRAWALS"] = ""
                        # Balance decreased → Withdrawal difference
                        elif diff < 0:
                            df_final.at[i, "WITHDRAWALS"] = f"{abs(diff):.2f}"
                            df_final.at[i, "DEPOSITS"] = ""

#                print("✅ Step 8: Auto-corrected rows having both Withdrawal and Deposit values based on balance difference.")

            except Exception as e:
                print("⚠️ Step 8 Error:", e)
                
        return df_final


    # ------------------- IDBI BANK -------------------
    def parse_idbi_bank_format(self, path):

        """
        Extract IDBI Bank statement data (8 columns) using pdfplumber.
        Handles merged/multiline cells, removes duplicate & empty rows.
        """


        rows = []
        seen = set()

        with pdfplumber.open(path, password=getattr(self, "pdf_password", None)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        # Clean cells (remove None and extra spaces)
                        row = [cell.strip() if cell else "" for cell in row]

                        # --- Skip headers / repeated headers ---
                        if (
                            any(x.lower().startswith(("s.no", "txn", "value", "descr", "cheque", "withdraw", "deposit", "balance")) for x in row)
                            or "idbi" in " ".join(row).lower()
                            or "statement" in " ".join(row).lower()
                            or "page" in " ".join(row).lower()
                        ):
                            continue

                        # --- Only process rows with enough columns ---
                        if len(row) >= 8:
                            key = tuple(row)
                            if key in seen:
                                continue
                            seen.add(key)

                            rows.append({
                                "S.NO": row[0],
                                "TXN DATE": row[1],
                                "VALUE DATE": row[2],
                                "DESCRIPTION": row[3],
                                "CHQ/REF NO": row[4],
                                "WITHDRAWALS": row[5],
                                "DEPOSITS": row[6],
                                "BALANCE": row[7],
                            })

        # --- Step 2: Create DataFrame ---
        df = pd.DataFrame(rows)

        # --- Step 3: Remove duplicate rows ---
        df = df.drop_duplicates().reset_index(drop=True)

        # --- Step 4: Remove rows where all main columns are empty ---
        self.data = df
        self.filter_empty_rows()
        
        # --- Step 5A: Remove time part from TXN DATE column ---
        if "TXN DATE" in self.data.columns:
            self.data["TXN DATE"] = (
                self.data["TXN DATE"]
                .astype(str)
                .str.strip()
                .str.replace(r"(\d{2}[/-]\d{2}[/-]\d{4}).*", r"\1", regex=True)
            )
        
        return self.data


    def filter_empty_rows(self):
        """
        Remove rows where all important columns are blank or empty.
        """


        if self.data is None or self.data.empty:
            return

        cols_to_check = [
            "S.NO", "TXN DATE", "VALUE DATE", "DESCRIPTION",
            "CHQ/REF NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"
        ]

        self.data = self.data[
            self.data[cols_to_check].apply(lambda x: any(str(v).strip() != "" for v in x), axis=1)
        ]

        self.data = self.data.reset_index(drop=True)


# ----------------- INDUSIND BANK -----------------

    def parse_indusind_bank_format(self, path):

        # Ignore warnings
        warnings.filterwarnings("ignore")

        # --- Step 1: Read PDF text (with password authentication same as UNION BANK) ---
        text = ""
        with fitz.open(path) as doc:
            # ✅ Password authentication (same as UNION BANK)
            if self.pdf_password:
                if not doc.authenticate(self.pdf_password):
                    raise ValueError("Invalid PDF password")

            for page in doc:
                text += page.get_text("text") + "\n"

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # RegEx Patterns
        indusind_date_pat = re.compile(r"^\d{1,2} [A-Za-z]{3} \d{4}$")
        amt_check_pat = re.compile(r"^-?[\d,]+\.\d+$")  # e.g. 300000.0, 0.00, 145369.00
        
        # --- Core Logic: Segmented Transaction Processing ---
        records = []
        i = 0
        
        ignore_lines = {"Date", "Particulars", "Chq No/Ref No", "Withdrawal", "Deposit", "Balance"}

        while i < len(lines):
            line = lines[i]
            
            if indusind_date_pat.match(line):
                current = {
                    "Date": line,
                    "Narration": "",
                    "CHQ/REF NO": "",
                    "VALUE DATE": line,
                    "WITHDRAWALS": "",
                    "DEPOSITS": "",
                    "BALANCE": ""
                }
                i += 1
                intermediate_lines = []
                first_amount_index = -1
                
                for j in range(i, len(lines)):
                    current_line = lines[j]
                    if current_line in ignore_lines:
                        continue
                    if indusind_date_pat.match(current_line):
                        break
                    if amt_check_pat.match(current_line):
                        first_amount_index = j
                        break
                    intermediate_lines.append(current_line)
                    i = j + 1

                if intermediate_lines:
                    current["CHQ/REF NO"] = intermediate_lines[-1]
                    narration_parts = intermediate_lines[:-1]
                    current["Narration"] = " ".join(narration_parts).strip()
                
                if first_amount_index == -1:
                    records.append(current)
                    continue
                
                start_search = first_amount_index
                amounts_found = []
                
                for k in range(start_search, len(lines)):
                    amount_line = lines[k]
                    if amount_line in ignore_lines:
                        continue
                    if indusind_date_pat.match(amount_line):
                        break
                    if amt_check_pat.match(amount_line):
                        amounts_found.append(amount_line)
                        if len(amounts_found) == 3:
                            current["WITHDRAWALS"] = amounts_found[0]
                            current["DEPOSITS"] = amounts_found[1]
                            current["BALANCE"] = amounts_found[2]
                            i = k + 1
                            break
                    else:
                        if len(amounts_found) > 0:
                            break

                if len(amounts_found) == 3:
                    final_narration_parts = []
                    start_search_after_balance = i
                    
                    for l in range(start_search_after_balance, len(lines)):
                        final_narration_line = lines[l]
                        if final_narration_line in ignore_lines:
                            continue
                        if indusind_date_pat.match(final_narration_line):
                            i = l
                            break
                        final_narration_parts.append(final_narration_line)
                        i = l + 1
                        
                    if final_narration_parts:
                        current["Narration"] = (
                            current["Narration"] + " " + " ".join(final_narration_parts)
                        ).strip()

                records.append(current)
                continue
            
            i += 1

        # --- Create DataFrame and Final Steps ---
        df = pd.DataFrame(records, columns=[
            "Date", "Narration", "CHQ/REF NO", "VALUE DATE",
            "WITHDRAWALS", "DEPOSITS", "BALANCE"
        ])
        
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        def clean_text_parts(narr):
            if not isinstance(narr, str):
                return narr
            narr = re.split(r"\b(Page|STATEMENT SUMMARY|Account Statement)\b", narr, flags=re.IGNORECASE)[0].strip()
            return narr

        df["Narration"] = df["Narration"].apply(clean_text_parts)
        
        def clean_amount(amt_str):
            if not isinstance(amt_str, str) or not amt_str.strip():
                return ""
            amt_str = amt_str.replace(',', '')
            try:
                amt = float(amt_str)
                if abs(amt) < 0.01:
                    return ""
                return f"{amt:,.2f}"
            except ValueError:
                return amt_str 
        
        df['WITHDRAWALS'] = df['WITHDRAWALS'].apply(clean_amount)
        df['DEPOSITS'] = df['DEPOSITS'].apply(clean_amount)
        df['BALANCE'] = df['BALANCE'].apply(clean_amount)
        
        df['BALANCE_CALC'] = df['BALANCE'].str.replace(',', '', regex=False).replace('', np.nan)
        df['BALANCE_CALC'] = pd.to_numeric(df['BALANCE_CALC'], errors='coerce')
        df['WITHDRAWALS_CALC'] = df['WITHDRAWALS'].str.replace(',', '', regex=False).replace('', '0')
        df['DEPOSITS_CALC'] = df['DEPOSITS'].str.replace(',', '', regex=False).replace('', '0')
        df['WITHDRAWALS_CALC'] = pd.to_numeric(df['WITHDRAWALS_CALC'], errors='coerce')
        df['DEPOSITS_CALC'] = pd.to_numeric(df['DEPOSITS_CALC'], errors='coerce')
        
        if len(df) > 0:
            if df.loc[0, 'WITHDRAWALS'] == "" and df.loc[0, 'DEPOSITS'] == "":
                df.loc[0, 'WITHDRAWALS'] = "Opening Balance not found; kindly input the transaction amount manually."
                df.loc[0, 'DEPOSITS'] = "Opening Balance not found; kindly input the transaction amount manually."

        for i in range(1, len(df)):
            prev_balance = df.loc[i - 1, 'BALANCE_CALC']
            current_balance = df.loc[i, 'BALANCE_CALC']
            if pd.notna(prev_balance) and pd.notna(current_balance):
                difference = current_balance - prev_balance
                if df.loc[i, 'WITHDRAWALS'] == "" and df.loc[i, 'DEPOSITS'] == "":
                    if difference > 0:
                        df.loc[i, 'DEPOSITS'] = f"{difference:,.2f}"
                    elif difference < 0:
                        df.loc[i, 'WITHDRAWALS'] = f"{abs(difference):,.2f}"

        df = df.drop(columns=['BALANCE_CALC', 'WITHDRAWALS_CALC', 'DEPOSITS_CALC'])
        df["Date"], df["VALUE DATE"] = df["VALUE DATE"], df["Date"]
        
        def clean_computer_text(narr):
            if not isinstance(narr, str):
                return narr
            narr_parts = re.split(r"\bThis is a computer generated\b", narr, flags=re.IGNORECASE)
            return narr_parts[0].strip()

        df["Narration"] = df["Narration"].apply(clean_computer_text)        

        return df

        
    #-----------------------Shree Mahesh Co-Op Bank Ltd------------------------         
        
    def parse_mahesh_bank_format(self, path):


        # --- Step 0: PDF open with password authentication (same as union bank) ---
        temp_path = None
        with fitz.open(path) as doc:
            if self.pdf_password:
                if not doc.authenticate(self.pdf_password):
                    raise ValueError("Invalid PDF password")

                # ✅ Decrypt & save to temporary file for Camelot
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_path = temp_file.name
                temp_file.close()
                doc.save(temp_path)
            else:
                temp_path = path  # No password case

        # --- Step 1: Extract tables using Camelot ---
        tables = camelot.read_pdf(temp_path, pages='all', flavor='lattice', strip_text='\n')
        
        rows = []
        seen = set()

        for table in tables:
            df = table.df
            for _, row in df.iterrows():
                # Clean cells (remove extra spaces/newlines)
                row = [str(c).strip() for c in row.tolist()]

                # Skip empty or header rows
                if (
                    "Date" in row[0]
                    or "Particulars" in row[1]
                    or "Debit" in row[-3]
                    or "Credit" in row[-2]
                    or "Balance" in row[-1]
                    or "STATEMENT" in " ".join(row)
                    or "Bank Name" in " ".join(row)
                    or "Page" in " ".join(row)
                    or re.match(r"^\*+END OF STATEMENT", " ".join(row))
                ):
                    continue

                # Expecting 7 columns: Sr.No, Date, Particulars, CHQ/REF NO, Debit, Credit, Balance
                if len(row) >= 7:
                    key = tuple(row)
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    rows.append({
                        "SR NO": row[0],
                        "DATE": row[1],
                        "PARTICULARS": row[2],
                        "CHQ/REF NO": row[3],
                        "DEBIT": row[4],
                        "CREDIT": row[5],
                        "BALANCE": row[6],
                    })

        df = pd.DataFrame(rows)

        # --- Step 2: Remove duplicates & clean ---
        df = df.drop_duplicates().reset_index(drop=True)
        df = df[df['DATE'].str.strip() != ""]  # Remove blank rows

        # --- Step 3: Cleanup temp file ---
        if temp_path and temp_path != path:
            try:
                os.remove(temp_path)
            except Exception:
                pass

        self.data = df
        return df

    # ----------------- NASIK MERCHANT CO-OP BANK LTD -----------------

    def parse_namco_bank_text(self, pdf_path):

        import os
        import re
        import fitz
        import pandas as pd
        import tempfile

        decrypted_pdf = None
        txt_path = None

        try:
            # ----------------------------------------------------------
            # STEP 0: Handle Password Protected PDF (ADDED LOGIC)
            # ----------------------------------------------------------
            if self.pdf_password:
                doc = fitz.open(pdf_path)

                if doc.needs_pass:
                    if not doc.authenticate(self.pdf_password):
                        doc.close()
                        raise ValueError("Invalid PDF password for NAMCO Bank file.")

                # Create temp decrypted PDF file
                tmp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
                os.close(tmp_fd)
                doc.save(decrypted_pdf)
                doc.close()

                # Use decrypted PDF as input
                pdf_path = decrypted_pdf

            # ----------------------------------------------------------
            # STEP 1: Extract text from PDF (layout preserved)
            # ----------------------------------------------------------
            doc = fitz.open(pdf_path)
            all_text = ""
            for page in doc:
                all_text += page.get_text("text")
            doc.close()

            txt_path = pdf_path.replace(".pdf", "_extracted.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(all_text)

            # ----------------------------------------------------------
            # STEP 2: Convert Text → DataFrame (existing logic)
            # ----------------------------------------------------------
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            lines = text.split("\n")
            rows = []
            prev_balance = None
            opening_added = False

            skip_patterns = [
                r"DATE\s+PARTICULARS",
                r"STATEMENT OF ACCOUNT",
                r"Statement Printed",
                r"NASIK MERCHANT",
                r"Schme Type",
                r"Grand Total",
                r"Page Total",
                r"Page\s+1",
                r"^-{5,}",
                r"Transaction Details",
            ]

            opening_match = re.search(r"([\d,]+\.\d{2})Cr", text)
            if opening_match and not opening_added:
                ob = float(opening_match.group(1).replace(",", ""))
                rows.append({
                    "VALUE DATE": "",
                    "POST DATE": "",
                    "DETAILS": "OPENING BALANCE",
                    "CHQ NO": "",
                    "DEBIT": "",
                    "CREDIT": "",
                    "BALANCE": ob
                })
                prev_balance = ob
                opening_added = True

            ref_capture = re.compile(r"(\d{5,12})\s+[\d,]+\.\d{2}")

            line_pattern = re.compile(
                r"^(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([\d,]+\.\d{2})?\s*"
                r"([\d,]+\.\d{2})?\s+([\d,]+\.\d{2})Cr$"
            )

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if any(re.search(p, line, re.IGNORECASE) for p in skip_patterns):
                    continue

                match = line_pattern.match(line)
                if match:
                    date, details, wd, dep, bal = match.groups()
                    balance = float(bal.replace(",", "").replace("Cr", ""))

                    ref_match = ref_capture.search(line)
                    if ref_match:
                        ref_no = ref_match.group(1)
                        details = f"{details} {ref_no}"

                    rows.append({
                        "VALUE DATE": date,
                        "POST DATE": date,
                        "DETAILS": details.strip(),
                        "CHQ NO": "",
                        "DEBIT": wd if wd else "",
                        "CREDIT": dep if dep else "",
                        "BALANCE": balance
                    })

                    prev_balance = balance

            # ----------------------------------------------------------
            # STEP 3: Fix Debit/Credit via Balance differences
            # ----------------------------------------------------------
            prev = None
            for r in rows:
                try:
                    bal = float(r["BALANCE"])
                except:
                    continue

                if prev is not None:
                    diff = bal - prev
                    if diff > 0:
                        r["CREDIT"] = f"{diff:,.2f}"
                        r["DEBIT"] = ""
                    elif diff < 0:
                        r["DEBIT"] = f"{abs(diff):,.2f}"
                        r["CREDIT"] = ""
                prev = bal

            df = pd.DataFrame(rows, columns=[
                "VALUE DATE", "POST DATE", "DETAILS", "CHQ NO", "DEBIT", "CREDIT", "BALANCE"
            ])

            # ----------------------------------------------------------
            # STEP 4: Remove CHQ NO column
            # ----------------------------------------------------------
            df = df.drop(columns=["CHQ NO"])

            # ----------------------------------------------------------
            # STEP 5: Remove duplicate reference numbers inside DETAILS
            # ----------------------------------------------------------
            for i in df.index:
                details = df.at[i, "DETAILS"]
                details = re.sub(r"\b(\d{5,12})\b(?:\s+\1)+", r"\1", details)
                df.at[i, "DETAILS"] = details

        finally:
            # ----------------------------------------------------------
            # STEP 6: Delete temp text file
            # ----------------------------------------------------------
            try:
                if txt_path and os.path.exists(txt_path):
                    os.remove(txt_path)
            except:
                pass

            # ----------------------------------------------------------
            # STEP 7: Delete decrypted temp PDF
            # ----------------------------------------------------------
            try:
                if decrypted_pdf and os.path.exists(decrypted_pdf):
                    os.remove(decrypted_pdf)
            except:
                pass

        return df




    # ------------------ UNION BANK OF INDIA --------------------

    def parse_union_format_0(self, pdf_path):

        import os
        import re
        import fitz
        import pandas as pd
        import tempfile

        decrypted_pdf = None
        temp_doc = None

        try:
            # ----------------------------------------------------------
            # 0) Handle Password Protected PDF (Added Logic)
            # ----------------------------------------------------------
            if self.pdf_password:
                doc = fitz.open(pdf_path)

                if doc.needs_pass:
                    if not doc.authenticate(self.pdf_password):
                        doc.close()
                        raise ValueError("Invalid PDF password for Union Bank file.")

                tmp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
                os.close(tmp_fd)

                doc.save(decrypted_pdf)
                doc.close()

                pdf_path = decrypted_pdf

            # ----------------------------------------------------------
            # STEP 1: Extract raw text
            # ----------------------------------------------------------
            doc = fitz.open(pdf_path)
            all_text = ""

            for page in doc:
                all_text += page.get_text("text")

            doc.close()

            txt_path = pdf_path.replace(".pdf", "_extracted.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(all_text)

            # ----------------------------------------------------------
            # STEP 2: Read text
            # ----------------------------------------------------------
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            lines = text.split("\n")
            rows = []
            prev_balance = None

            skip_patterns = [
                r"UNION BANK OF INDIA",
                r"STATEMENT OF ACCOUNT",
                r"DATE\s+PARTICULARS",
                r"Cumulative Totals",
                r"PAGE:",
                r"Transaction Details",
                r"^-{5,}",
                r"Nasik",
                r"UMFB",
            ]

            # ----------------------------------------------------------
            # STEP 3: Opening Balance
            # ----------------------------------------------------------
            opening_match = re.search(r"([\d,]+\.\d{2})Cr", text)
            if opening_match:
                ob = float(opening_match.group(1).replace(",", ""))
                rows.append({
                    "VALUE DATE": "",
                    "POST DATE": "",
                    "DETAILS": "OPENING BALANCE",
                    "DEBIT": "",
                    "CREDIT": "",
                    "BALANCE": ob
                })
                prev_balance = ob

            ref_capture = re.compile(r"(\d{5,12})")

            # ----------------------------------------------------------
            # STEP 4: Main line regex
            # ----------------------------------------------------------
            line_pattern = re.compile(
                r"^(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([\d,]+\.\d{2})?\s*"
                r"([\d,]+\.\d{2})?\s+([\d,]+\.\d{2})Cr$"
            )

            # ----------------------------------------------------------
            # STEP 5: Parse each line
            # ----------------------------------------------------------
            for line in lines:

                line = line.strip()
                if not line:
                    continue

                if any(re.search(p, line, re.IGNORECASE) for p in skip_patterns):
                    continue

                match = line_pattern.match(line)
                if match:

                    date, details, wd, dep, bal = match.groups()
                    balance = float(bal.replace(",", ""))

                    refs = ref_capture.findall(details)
                    if refs:
                        details = details + " " + refs[-1]

                    rows.append({
                        "VALUE DATE": date,
                        "POST DATE": date,
                        "DETAILS": details.strip(),
                        "DEBIT": wd if wd else "",
                        "CREDIT": dep if dep else "",
                        "BALANCE": balance
                    })

                    prev_balance = balance

            # ----------------------------------------------------------
            # STEP 6: Debit/Credit fix by difference
            # ----------------------------------------------------------
            prev = None
            for r in rows:
                try:
                    bal = float(r["BALANCE"])
                except:
                    continue

                if prev is not None:
                    diff = bal - prev
                    if diff > 0:
                        r["CREDIT"] = f"{diff:,.2f}"
                        r["DEBIT"] = ""
                    elif diff < 0:
                        r["DEBIT"] = f"{abs(diff):,.2f}"
                        r["CREDIT"] = ""

                prev = bal

            df = pd.DataFrame(rows, columns=[
                "VALUE DATE", "POST DATE", "DETAILS", "DEBIT", "CREDIT", "BALANCE"
            ])

            # ----------------------------------------------------------
            # STEP 7: Remove duplicate ref numbers
            # ----------------------------------------------------------
            for i in df.index:
                details = df.at[i, "DETAILS"]
                details = re.sub(r"\b(\d{5,12})\b(?:\s+\1)+", r"\1", details)
                df.at[i, "DETAILS"] = details

        finally:
            # ----------------------------------------------------------
            # STEP 8: Safe delete txt file
            # ----------------------------------------------------------
            try:
                if os.path.exists(txt_path):
                    os.remove(txt_path)
            except:
                pass

            # ----------------------------------------------------------
            # STEP 9: Safe delete decrypted pdf
            # ----------------------------------------------------------
            try:
                if decrypted_pdf and os.path.exists(decrypted_pdf):
                    os.remove(decrypted_pdf)
            except:
                pass

        return df




    def parse_union_format_2(self, pdf_path: str) -> pd.DataFrame:
        """
        Parses Union Bank of India fixed-column-like format (loan-style statements).
        Supports password-protected PDFs.
        """

        import os
        import re
        import fitz
        import pandas as pd
        import tempfile
        from typing import List, Dict, Any, Optional

        decrypted_pdf = None
        txt_path = None

        try:
            # ----------------------------------------------------------
            # STEP 0: Password Protected PDF Handling
            # ----------------------------------------------------------
            if self.pdf_password:
                doc = fitz.open(pdf_path)

                if doc.needs_pass:
                    if not doc.authenticate(self.pdf_password):
                        doc.close()
                        raise ValueError("Invalid PDF password for Union Bank file.")

                tmp_fd, decrypted_pdf = tempfile.mkstemp(suffix=".pdf")
                os.close(tmp_fd)
                doc.save(decrypted_pdf)
                doc.close()

                pdf_path = decrypted_pdf

            # ----------------------------------------------------------
            # STEP 1: Extract raw text
            # ----------------------------------------------------------
            doc = fitz.open(pdf_path)
            all_text = ""
            for page in doc:
                all_text += page.get_text("text")
            doc.close()

            txt_path = pdf_path.replace(".pdf", "_extracted_format_2.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(all_text)

            # ----------------------------------------------------------
            # STEP 2: Load extracted text
            # ----------------------------------------------------------
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            lines = text.split("\n")
            rows: List[Dict[str, Any]] = []
            prev_balance: Optional[float] = None

            # ----------------------------------------------------------
            # STEP 3: Opening Balance = 0.0
            # ----------------------------------------------------------
            rows.append({
                "VALUE DATE": "",
                "POST DATE": "",
                "DETAILS": "OPENING BALANCE",
                "DEBIT": "",
                "CREDIT": "",
                "BALANCE": 0.0
            })
            prev_balance = 0.0

            # ----------------------------------------------------------
            # STEP 4: Regex Pattern
            # ----------------------------------------------------------
            skip_patterns = [
                r"UNION BANK OF INDIA",
                r"STATEMENT OF ACCOUNT",
                r"DATE\s+PARTICULARS",
                r"Cumulative Totals",
                r"PAGE:",
                r"Transaction Details",
                r"^-{5,}",
                r"Unless constituent notifies the bank",
            ]

            line_pattern = re.compile(
                r"^(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([\d,]+\.\d{2})?\s*"
                r"([\d,]+\.\d{2})?\s+([\d,]+\.\d{2})(Dr|Cr)?$"
            )

            # ----------------------------------------------------------
            # STEP 5: Parse each line
            # ----------------------------------------------------------
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if any(re.search(p, line, re.IGNORECASE) for p in skip_patterns):
                    continue

                if line == "0":
                    continue

                match = line_pattern.match(line)
                if match:
                    date, details, wd, dep, bal_str, sign = match.groups()

                    clean_bal = float(bal_str.replace(",", ""))

                    if sign and sign.upper() == "DR":
                        clean_bal *= -1

                    rows.append({
                        "VALUE DATE": date,
                        "POST DATE": date,
                        "DETAILS": details.strip(),
                        "DEBIT": wd if wd else "",
                        "CREDIT": dep if dep else "",
                        "BALANCE": clean_bal,
                        "ORIGINAL_SIGN": sign if sign else ""
                    })

            # ----------------------------------------------------------
            # STEP 6: Fix Debit/Credit by difference
            # ----------------------------------------------------------
            for i in range(1, len(rows)):
                curr = rows[i]
                prev = rows[i - 1]

                try:
                    bal = float(curr["BALANCE"])
                    prev_bal = float(prev["BALANCE"])
                except:
                    continue

                diff = bal - prev_bal

                if diff > 0.005:
                    curr["CREDIT"] = f"{diff:,.2f}"
                    curr["DEBIT"] = ""
                elif diff < -0.005:
                    curr["DEBIT"] = f"{abs(diff):,.2f}"
                    curr["CREDIT"] = ""

            # ----------------------------------------------------------
            # STEP 7: Format Balance Column
            # ----------------------------------------------------------
            for r in rows:
                if isinstance(r["BALANCE"], float):
                    v = abs(r["BALANCE"])
                    sign = "Dr" if r["BALANCE"] < 0 else "Cr" if r["BALANCE"] > 0 else ""
                    r["BALANCE"] = f"{v:,.2f}{sign}"
                r.pop("ORIGINAL_SIGN", None)

            df = pd.DataFrame(rows, columns=[
                "VALUE DATE", "POST DATE", "DETAILS",
                "DEBIT", "CREDIT", "BALANCE"
            ])

            return df

        finally:
            try:
                if txt_path and os.path.exists(txt_path):
                    os.remove(txt_path)
            except:
                pass

            try:
                if decrypted_pdf and os.path.exists(decrypted_pdf):
                    os.remove(decrypted_pdf)
            except:
                pass



#------------- Punjab National Bank ---------------------------

    def parse_pnb_bank_format(self, path):

        import camelot
        import pandas as pd

        rows = []
        page_no = 0

        # ------------------------------
        # 1) Read PDF (with password)
        # ------------------------------
        if self.pdf_password:
            tables = camelot.read_pdf(
                path,
                pages="all",
                flavor="lattice",
                strip_text="\n",
                password=self.pdf_password
            )
        else:
            tables = camelot.read_pdf(
                path,
                pages="all",
                flavor="lattice",
                strip_text="\n"
            )

        # ------------------------------
        # 2) Parse each page table
        # ------------------------------
        for table in tables:
            page_no += 1
            df = table.df

            for i, row in df.iterrows():

                # Skip first header on first page
                if page_no == 1 and i == 0:
                    continue

                row = [str(x).strip() for x in row]

                # Header rows skip
                if row[0].lower() in ["date", "NARRATION"]:
                    continue

                if not row[0].strip():
                    continue

                # Expected PNB columns = DATE | INST ID | AMOUNT | TYPE | BALANCE | NARRATION
                if len(row) < 5:
                    continue

                date = row[0]
                inst = row[1]
                amount = row[2]
                ttype = row[3]  # DR or CR
                balance = row[4]
                NARRATION = ""
                if len(row) > 5:
                    NARRATION = row[5]

                # Multi-line NARRATION merge (blank date means continuation line)
                if not date and rows:
                    rows[-1]["NARRATION"] += " " + inst
                    continue

                rows.append({
                    "DATE": date,
                    "CHQ/REF NO": inst,
                    "AMOUNT": amount,
                    "TYPE": ttype,   # DR / CR
                    "BALANCE": balance,
                    "NARRATION": NARRATION
                })

        # ------------------------------
        # 3) Add DEBIT / CREDIT columns
        # ------------------------------
        df_final = pd.DataFrame(rows)

        df_final["DEBIT"] = df_final.apply(
            lambda x: x["AMOUNT"] if x["TYPE"] == "DR" else "",
            axis=1
        )
        df_final["CREDIT"] = df_final.apply(
            lambda x: x["AMOUNT"] if x["TYPE"] == "CR" else "",
            axis=1
        )

        return df_final

    def parse_SARASWAT_pdf(self, path):
        """
        1) Try primary Saraswat parser (parse_saraswat_bank_format - Text based, as requested)
        2) If primary parser fails (error, empty DF, missing crucial columns) → run fallback format1
        """

        # -------------------------------
        # TRY PRIMARY PARSER (FORMAT 2 - Text-based logic)
        # -------------------------------
        try:
            # parse_saraswat_bank_format main coad
            df = self.parse_saraswat_bank_format(path)
        except Exception as e:
            print("Primary parser (format2) ERROR:", e)
            print("→ Using fallback format (format1) parser...")
            return self.parse_saraswat_bank_format1(path)

        # -------------------------------
        # CHECK-1 : DataFrame Empty / None
        # -------------------------------
        if df is None or df.empty:
            print("Primary parser (format2) returned EMPTY → fallback")
            return self.parse_saraswat_bank_format1(path)
        
        # -------------------------------
        # CHECK-2 : Required columns exist (Format 2 colume)
        # -------------------------------
        required_cols = ["DATE", "DESCRIPTION", "CHEQUE NO", "WITHDRAWALS", "DEPOSITS", "BALANCE"]

        for col in required_cols:
            if col not in df.columns:
                print(f"Missing column: {col} → fallback")
                return self.parse_saraswat_bank_format1(path)

        # -------------------------------
        # CHECK-3 : Full column blank (Critical columns)
        # -------------------------------
        # DATE, WITHDRAWALS and DEPOSITS is any colume empty then fallback.
        cols_to_check_blank = ["DATE", "WITHDRAWALS", "DEPOSITS"]

        for col in cols_to_check_blank:
            try:
                # if full colume empty then fallback.
                if (df[col].astype(str).str.strip() == "").all():
                    print(f"Critical column {col} is fully blank → fallback")
                    return self.parse_saraswat_bank_format1(path)
            except Exception as e:
                print(f"Column check failed for {col}: {e} → fallback")
                return self.parse_saraswat_bank_format1(path)
        
        # -------------------------------
        # NO fallback needed → RETURN PRIMARY RESULT
        # -------------------------------
        print("Primary parser (format2) SUCCESS ✔")
        return df



    # ----------------- SARASWAT CO-OPERATIVE BANK LTD ----------------------------
    def parse_saraswat_bank_format1(self, path):


        rows = []
        seen = set()

        with pdfplumber.open(path, password=self.pdf_password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        row = [cell.strip() if cell else "" for cell in row]

                        if (
                            "Date" in row[0]
                            or "Particulars" in row[1]
                            or "CHQ/REF NO" in row[2]
                            or "Dr Amount" in row[3]
                            or "Cr Amount" in row[4]
                            or "Balance" in row[-1]
                            or row[0].startswith("----")
                        ):
                            continue

                        if len(row) < 5:
                            continue

                        key = tuple(row)
                        if key in seen:
                            continue
                        seen.add(key)

                        if row[0] == "" and rows:
                            rows[-1]["PARTICULARS"] += " " + row[1]
                            continue

                        rows.append({
                            "DATE": row[0],
                            "PARTICULARS": row[1],
                            "CHQ/REF NO": row[2],
                            "WITHDRAWALS": row[3],
                            "DEPOSITS": row[4],
                            "BALANCE": row[5] if len(row) > 5 else "",
                        })

        df = pd.DataFrame(rows)

        # RULE 1: Remove rows where DATE contains "Account :"
        df = df[~df["DATE"].str.contains("Account :", case=False, na=False)]

        # RULE 2: Remove "Totals / Balance :-" AND everything after it
        stop_index = df.index[
            df.apply(
                lambda r: r.astype(str).str.contains("Totals / Balance", case=False, na=False).any(),
                axis=1
            )
        ]

        if len(stop_index) > 0:
            first_stop = stop_index[0]
            df = df.iloc[:first_stop]

        # FINAL CLEAN — Delete row where DATE contains "Totals / Balance :-"
        df = df[~df["DATE"].str.contains("Totals / Balance", case=False, na=False)]

        df = df.drop_duplicates().reset_index(drop=True)

        self.data = df
        self.filter_empty_rows()

        return self.data

    def filter_empty_rows(self):
        """
        Removes rows where all statement columns are blank.
        """
        if self.data is None or self.data.empty:
            return

        cols_to_check = ["DATE", "PARTICULARS", "CHQ/REF NO",
                         "WITHDRAWALS", "DEPOSITS", "BALANCE"]

        self.data = self.data[
            self.data[cols_to_check].apply(
                lambda x: any(str(v).strip() != "" for v in x),
                axis=1
            )
        ]

        self.data = self.data.reset_index(drop=True)



 # ----------------hdfc bank text ----------------

    def parse_hdfc_format12(self, path):
        rows = []
        table_active = False

        # ------------------------------
        # Utility functions
        # ------------------------------
        def is_date(s):
            return bool(re.match(r"^\d{2}/\d{2}/\d{2}$", s.strip()))

        def is_money(s):
            return bool(re.match(r"^[\d,]+\.\d{2}$", s.strip()))

        # ------------------------------
        # Read file
        # ------------------------------
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # ------------------------------
        # Process all lines (ALL pages)
        # ------------------------------
        for raw in lines:

            line = raw.rstrip("\n")

            if "Date      Narration" in line and "Closing Balance" in line:
                table_active = True
                continue

            if not table_active:
                continue

            if not line.strip():
                continue

            if "**Continue**" in line:
                continue

            parts = re.split(r"\s{2,}", line.strip())

            # --------------------------
            # MAIN ROW (Date present)
            # --------------------------
            if is_date(parts[0]):

                date = parts[0]
                narr = ""
                refno = ""
                valdt = ""
                debit = ""
                credit = ""
                bal = ""

                if len(parts) >= 2:
                    narr = parts[1]

                if len(parts) >= 3 and len(parts[2]) >= 6:
                    refno = parts[2]

                if len(parts) >= 4 and is_date(parts[3]):
                    valdt = parts[3]

                money = [p for p in parts if is_money(p)]

                if len(money) == 3:
                    debit, credit, bal = money
                elif len(money) == 2:
                    if "CR" in narr.upper() or "DEP" in narr.upper():
                        credit, bal = money
                    else:
                        debit, bal = money
                elif len(money) == 1:
                    bal = money[0]

                rows.append({
                    "DATE": date,
                    "NARRATION": narr,
                    "REF NO": refno,
                    "VALUE DATE": valdt,
                    "DEBIT": debit,
                    "CREDIT": credit,
                    "BALANCE": bal
                })

            # --------------------------
            # SUB ROW
            # --------------------------
            else:
                sub = line.strip()
                if sub:
                    rows.append({
                        "DATE": "",
                        "NARRATION": sub,
                        "REF NO": "",
                        "VALUE DATE": "",
                        "DEBIT": "",
                        "CREDIT": "",
                        "BALANCE": ""
                    })

        # ============================================================
        #  FINAL CLEANING
        # ============================================================

        clean_rows = []
        skip_block = False
        dash_count = 0
        star_block_found = False

        for r in rows:

            text = r["NARRATION"]

            # RULE 1 → remove page header (HDFC BANK ... until 2 dashed lines)
            if not skip_block and re.search(r"HDFC BANK.*Page No", text, re.IGNORECASE):
                skip_block = True
                dash_count = 0
                continue

            if skip_block:
                if re.search(r"-{6,}", text):
                    dash_count += 1
                if dash_count >= 2:
                    skip_block = False
                continue

            # RULE 2 → if "********" block appears → delete that line & everything after
            if re.search(r"\*{4,}", text):
                star_block_found = True
                break  # stop processing further rows

            # RULE 3 → delete dashed table header rows
            if re.match(r"-{6,}", text):
                continue

            clean_rows.append(r)

        # Convert to DataFrame
        df = pd.DataFrame(clean_rows)
        df = self.merge_narrations(df)
        return df

    def merge_narrations(self, df):

        import pandas as pd

        merged_rows = []
        current_main = None

        for idx, row in df.iterrows():

            if row["DATE"]:  
                # new main row
                if current_main is not None:
                    merged_rows.append(current_main)

                # new record start
                current_main = row.copy()
            
            else:
                # subline → narration merge 
                if current_main is not None:
                    sub = str(row["NARRATION"]).strip()
                    if sub:
                        current_main["NARRATION"] += " " + sub

                #  sub-row append

        #  pending row save
        if current_main is not None:
            merged_rows.append(current_main)

        return pd.DataFrame(merged_rows)
        




# ----------------- MASTER FUNCTION WITH FALLBACK -----------------
    def parse_hdfc_pdf(self, path):
        """
        Attempts to parse the HDFC PDF using two different formats.

        1) First runs parse_hdfc_format
        2) If DataFrame is empty OR
           If DATE / DEBIT / CREDIT / BALANCE columns have no values
           then fallback to parse_hdfc_format1
        """

        # 1. Run first format
        df = self.parse_hdfc_format(path)

        # 2. If DataFrame itself is empty → fallback
        if df is None or df.empty or len(df) == 0:
            
            return self.parse_hdfc_format1(path)

        # 3. Columns to validate
        required_columns = ["DATE", "DEBIT", "CREDIT", "BALANCE"]

        # 4. Check missing columns
        for col in required_columns:
            if col not in df.columns:
                
                return self.parse_hdfc_format1(path)

        # 5. Check if ALL values are empty in any required column
        for col in required_columns:
            if df[col].isna().all() or (df[col].astype(str).str.strip() == "").all():
                
                return self.parse_hdfc_format1(path)

        # 6. If everything is fine, return first parsed data
        return df

    def parse_icici_pdf(self, path):

        # Step 1: Run Camelot parser
        df = self.parse_icici_bank_format1(path)

        # If df is empty → direct fallback
        if df is None or df.empty:
            
            return self.parse_icici_bank_format(path)

        # Step 2: Check if any column is fully blank
        blank_column_found = False
        for col in df.columns:
            try:
                if (df[col].astype(str).str.strip() == "").all():
                    blank_column_found = True
                    break
            except:
                blank_column_found = True
                break

        # Step 3: If any column fully blank → run fallback parser
        if blank_column_found:
            
            return self.parse_icici_bank_format(path)

        # Otherwise return Camelot extracted DF
        return df




# ----------------- HDFC Format 1 (Original User Logic) -----------------
    def parse_hdfc_format(self, path):
        import warnings
        import fitz
        import pandas as pd
        import re

        warnings.filterwarnings("ignore")

        # --- Step 1: Read PDF text ---
        try:
            doc = fitz.open(path)
            if self.pdf_password:
                if not doc.authenticate(self.pdf_password):
                    print("ERROR: PDF password failed")
                    doc.close()
                    return pd.DataFrame()
        except RuntimeError as e:
            print(f"ERROR opening PDF: {e}")
            return pd.DataFrame()

        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # --- Regex ---
        date_pat = re.compile(r"^\d{2}/\d{2}/\d{2}$")
        date_with_text_pat = re.compile(r"^(\d{2}/\d{2}/\d{2})\s+(.*)$")
        amt_pat = re.compile(r"^-?[\d,]+\.\d{2}$")

        records = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # ---------- DATE detection (new + old) ----------
            date_match = date_with_text_pat.match(line)

            if date_match:
                txn_date = date_match.group(1)
                first_narration = date_match.group(2)
            elif date_pat.match(line):
                txn_date = line
                first_narration = ""
            else:
                i += 1
                continue

            current = {
                "Date": txn_date,
                "Narration": first_narration.strip(),
                "CHQ/REF NO": "",
                "VALUE DATE": "",
                "WITHDRAWALS": "",
                "DEPOSITS": "",
                "BALANCE": ""
            }

            i += 1

            # ---------- Find VALUE DATE ----------
            intermediate_lines = []
            value_date_index = -1

            for j in range(i, len(lines)):
                if date_pat.match(lines[j]):
                    current["VALUE DATE"] = lines[j]
                    value_date_index = j
                    break
                else:
                    intermediate_lines.append(lines[j])

            # ---------- Narration + CHQ REF ----------
            if intermediate_lines:
                current["CHQ/REF NO"] = intermediate_lines[-1]
                extra_narr = " ".join(intermediate_lines[:-1]).strip()
                if extra_narr:
                    current["Narration"] = (
                        current["Narration"] + " " + extra_narr
                    ).strip()

            # ---------- Find BALANCE ----------
            balance_found = False
            amount_index = -1

            if value_date_index != -1:
                amounts = []
                for k in range(value_date_index + 1, len(lines)):
                    if amt_pat.match(lines[k]):
                        amounts.append(lines[k])
                        if len(amounts) == 2:
                            current["BALANCE"] = amounts[1]
                            balance_found = True
                            amount_index = k
                            break

            # ---------- Final Narration after balance ----------
            if balance_found:
                final_parts = []
                for l in range(amount_index + 1, len(lines)):
                    if date_pat.match(lines[l]) or date_with_text_pat.match(lines[l]):
                        break
                    final_parts.append(lines[l])

                if final_parts:
                    current["Narration"] = (
                        current["Narration"] + " " + " ".join(final_parts)
                    ).strip()
                    i = l
                else:
                    i = amount_index + 1
            else:
                i = value_date_index + 1 if value_date_index != -1 else i + 1

            records.append(current)

        # ---------- DataFrame ----------
        df = pd.DataFrame(records, columns=[
            "Date", "Narration", "CHQ/REF NO", "VALUE DATE",
            "WITHDRAWALS", "DEPOSITS", "BALANCE"
        ])

        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        # ---------- Cleanup Narration ----------
        def clean_text(narr):
            if not isinstance(narr, str):
                return narr
            narr = re.split(r"\bPage\b", narr, flags=re.IGNORECASE)[0]
            narr = re.split(r"\bSTATEMENT SUMMARY\b", narr, flags=re.IGNORECASE)[0]
            return narr.strip()

        df["Narration"] = df["Narration"].apply(clean_text)

        # ---------- Withdrawals / Deposits ----------
        df["BALANCE_CALC"] = pd.to_numeric(
            df["BALANCE"].str.replace(",", "", regex=False),
            errors="coerce"
        )

        df["WITHDRAWALS"] = ""
        df["DEPOSITS"] = ""

        if len(df) > 0:
            df.loc[0, "WITHDRAWALS"] = "Opening Balance not found; kindly input manually."
            df.loc[0, "DEPOSITS"] = "Opening Balance not found; kindly input manually."

        for i in range(1, len(df)):
            prev = df.loc[i - 1, "BALANCE_CALC"]
            curr = df.loc[i, "BALANCE_CALC"]
            if pd.notna(prev) and pd.notna(curr):
                diff = curr - prev
                if diff > 0:
                    df.loc[i, "DEPOSITS"] = f"{diff:.2f}"
                elif diff < 0:
                    df.loc[i, "WITHDRAWALS"] = f"{abs(diff):.2f}"

        df["BALANCE"] = df["BALANCE_CALC"].apply(
            lambda x: f"{x:,.2f}" if pd.notna(x) else ""
        )
        df.drop(columns=["BALANCE_CALC"], inplace=True)

        # ---------- Swap Date & Value Date ----------
        df["Date"], df["VALUE DATE"] = df["VALUE DATE"], df["Date"]

        return df



# ----------------- HDFC Format 2 (Modified User Logic / Fallback) -----------------
    def parse_hdfc_format1(self, path):
        # Ignore warnings
        warnings.filterwarnings("ignore")

        # --- Step 1: Read PDF text (FIXED PASSWORD LOGIC) ---
        try:
            # 1. Open the document without the password keyword
            doc = fitz.open(path) 
            
            # 2. Authenticate the document if a password is provided
            if self.pdf_password:
                if not doc.authenticate(self.pdf_password):
                    print("ERROR: PDF requires a password, and authentication failed.")
                    doc.close()
                    return pd.DataFrame() 
                    
        except RuntimeError as e:
            print(f"ERROR: Could not open PDF in parse_hdfc_format1. Reason: {e}")
            return pd.DataFrame() # Return empty DataFrame on error

        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"

        # Close the document after reading
        doc.close() 

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # RegEx Patterns
        date_pat = re.compile(r"^\d{2}/\d{2}/\d{2}$")
        # Matches numbers with optional commas and two decimal places.
        amt_pat = re.compile(r"^-?[\d,]+\.\d{2}$")

        # --- Core Logic: Segmented Transaction Processing (Modified Logic) ---

        records = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # 1. Search for the Start of a New Transaction (Date)
            # A line is a new transaction if it starts with a Date.
            if date_pat.match(line.split()[0]): 
                
                # Split the line into the Date and the rest of the Narration
                parts = line.split(maxsplit=1)
                transaction_date = parts[0]
                initial_narration = parts[1] if len(parts) > 1 else ""
                
                current = {
                    "Date": transaction_date,
                    "Narration": initial_narration,
                    "CHQ/REF NO": "",
                    "VALUE DATE": "",
                    "WITHDRAWALS": "",
                    "DEPOSITS": "",
                    "BALANCE": ""
                }
                i += 1

                # Collect rows until the VALUE DATE is found
                intermediate_lines = []
                value_date_index = -1

                # Loop to find the VALUE DATE (the second date) and collect intermediate lines
                for j in range(i, len(lines)):
                    current_line = lines[j]
                    
                    # Check if the line ends with a date (VALUE DATE pattern)
                    # We look for a date that is the LAST word in the line.
                    words = current_line.split()
                    if words and date_pat.match(words[-1]):
                        # Found the second date (VALUE DATE)
                        current["VALUE DATE"] = words[-1]
                        value_date_index = j
                        
                        # The part before the VALUE DATE is the CHQ/REF NO.
                        # This handles 'HDFCN52025090347576001 03/09/25' -> CHQ: HDFCN520...001, VALUE DATE: 03/09/25
                        current["CHQ/REF NO"] = " ".join(words[:-1]).strip()
                        
                        break
                    else:
                        intermediate_lines.append(current_line)

                # --- APPLY NARRATION CONTINUATION LOGIC (Before CHQ/REF NO) ---
                # All lines between the first Date line and the CHQ/REF NO line are Narration continuation.
                if intermediate_lines:
                    current["Narration"] = (current["Narration"] + " " + " ".join(intermediate_lines)).strip()


                # --- Find Balance (The amount section comes after VALUE DATE) ---
                balance_found = False
                amount_index = -1

                if value_date_index != -1:
                    # Start searching for amounts immediately after VALUE DATE
                    start_search = value_date_index + 1
                    amounts_found = []

                    # Search for the next two consecutive amounts
                    for k in range(start_search, len(lines)):
                        amount_line = lines[k]

                        if amt_pat.match(amount_line):
                            amounts_found.append(amount_line)
                            if len(amounts_found) == 2:
                                # Found the second amount, which is the BALANCE
                                current["BALANCE"] = amounts_found[1]
                                balance_found = True
                                amount_index = k # This is the index of the BALANCE line
                                break
                            elif len(amounts_found) == 1 and not amt_pat.match(amount_line):
                                # Break if sequence is broken (e.g. text between two amounts)
                                break
                            elif len(amounts_found) == 0 and not amt_pat.match(amount_line):
                                # Ignore non-amount lines before the first amount (e.g. headers)
                                pass


                # --- Find Final Narration Continuation (Lines after Balance until next Transaction Date) ---
                if balance_found:
                    final_narration_parts = []

                    # Start searching after the BALANCE line
                    start_search = amount_index + 1

                    for l in range(start_search, len(lines)):
                        final_narration_line = lines[l]

                        # Stop if the next Transaction Date is found
                        if date_pat.match(final_narration_line.split()[0]):
                            # This is the line that starts the *next* transaction
                            break

                        final_narration_parts.append(final_narration_line)

                    # Append this final text to the existing Narration
                    if final_narration_parts:
                        current["Narration"] = (current["Narration"] + " " + " ".join(final_narration_parts)).strip()
                        # Move the main loop index 'i' to the line *before* the next transaction date (or end of file)
                        i = l 
                    else:
                        i = start_search # No continuation, set index after balance
                else:
                    # If balance wasn't found (problematic transaction), move index past the VALUE DATE
                    if value_date_index != -1:
                        i = value_date_index + 1
                    # If neither date was found, this shouldn't happen, but just in case
                    else:
                        i += 1

                records.append(current)
                continue

            # If the current line is not a date, just skip it (it could be header/footer/unwanted text)
            i += 1

        # --- Create DataFrame and Calculations (Your Original Logic - Unchanged) ---

        # --- Create DataFrame ---
        df = pd.DataFrame(records, columns=[
            "Date", "Narration", "CHQ/REF NO", "VALUE DATE",
            "WITHDRAWALS", "DEPOSITS", "BALANCE"
        ])

        # Clean whitespace safely
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        # --- Step 2/3: Remove unwanted trailing text (Your Original Logic) ---
        def clean_page_text(narr):
            if not isinstance(narr, str):
                return narr
            narr = re.split(r"\bPage\b", narr, flags=re.IGNORECASE)[0].strip()
            return narr

        df["Narration"] = df["Narration"].apply(clean_page_text)

        def clean_ST_text(narr):
            if not isinstance(narr, str):
                return narr
            narr = re.split(r"\bSTATEMENT SUMMARY\b", narr, flags=re.IGNORECASE)[0].strip()
            return narr

        df["Narration"] = df["Narration"].apply(clean_ST_text)


        # --- Step 4: Calculate WITHDRAWALS and DEPOSITS based on BALANCE (Your Original Logic) ---

        # Convert 'BALANCE' column to float after removing commas for calculation.
        df['BALANCE_CALC'] = df['BALANCE'].str.replace(',', '', regex=False)
        df['BALANCE_CALC'] = pd.to_numeric(df['BALANCE_CALC'], errors='coerce')

        df['WITHDRAWALS'] = ""
        df['DEPOSITS'] = ""

        # Handle Opening Balance Logic
        if len(df) > 0:
            df.loc[0, 'WITHDRAWALS'] = "Opening Balance not found; kindly input the transaction amount manually."
            df.loc[0, 'DEPOSITS'] = "Opening Balance not found; kindly input the transaction amount manually."

        for i in range(1, len(df)):
            prev_balance = df.loc[i - 1, 'BALANCE_CALC']
            current_balance = df.loc[i, 'BALANCE_CALC']

            if pd.notna(prev_balance) and pd.notna(current_balance):
                difference = current_balance - prev_balance

                if difference > 0:
                    df.loc[i, 'DEPOSITS'] = f"{difference:.2f}"
                elif difference < 0:
                    df.loc[i, 'WITHDRAWALS'] = f"{abs(difference):.2f}"

        df['BALANCE'] = df['BALANCE_CALC'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "")
        df = df.drop(columns=['BALANCE_CALC'])

        # --- Step 5: Swap Date and VALUE DATE columns (Your Original Logic) ---
        # NOTE: Your logic requires Date and VALUE DATE to be swapped for the final output.
        df["Date"], df["VALUE DATE"] = df["VALUE DATE"], df["Date"]
        return df

    
# ----------------- RAJLAXMI URBAN CO-OP BANK LTD ------------------------------   
    
    def parse_rajlaxmi_bank_format(self, path):

        rows = []
        seen = set()

        with pdfplumber.open(path, password=self.pdf_password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:

                        # Clean cells (None → "", strip spaces)
                        row = [cell.strip() if cell else "" for cell in row]

                        # Skip empty lines
                        if all(x == "" for x in row):
                            continue

                        # Skip headers (PDF  header  rows  repeat )
                        if (
                            "Date" in row[0]
                            or "Particular" in row[0]
                            or "Particular" in row[1]
                            or "Instrument" in row[1]
                            or "Closing" in row[0]
                            or "Debit" in row[-2]
                            or "Credit" in row[-1]
                            or "Balance" in row[-1]
                            or "Opening" in row[0]
                        ):
                            continue

                        # Rajlaxmi PDF rows  -> 6 column  normalize
                        # Format :
                        # DATE | DESCRIPTION | INSTR NO | DEBIT | CREDIT | BALANCE
                        clean = row + [""] * (6 - len(row))    # pad to 6 cols
                        clean = clean[:6]                      # limit to 6

                        key = tuple(clean)
                        if key in seen:
                            continue
                        seen.add(key)

                        rows.append({
                            "DATE": clean[0],
                            "DESCRIPTION": clean[1],
                            "CHQ/REF NO": clean[2],
                            "DEBIT": clean[3],
                            "CREDIT": clean[4],
                            "BALANCE": clean[5],
                        })

        df = pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)
        self.data = df

        # remove empty rows
        self.filter_empty_rows_rajlaxmi()
        return self.data


    def filter_empty_rows_rajlaxmi(self):
        """
        Remove rows where all 6 columns are empty.
        """
        if self.data is None or self.data.empty:
            return

        cols = ["DATE", "DESCRIPTION", "CHQ/REF NO", "DEBIT", "CREDIT", "BALANCE"]

        self.data = self.data[
            self.data[cols].apply(
                lambda r: any(str(v).strip() != "" for v in r),
                axis=1
            )
        ]

        self.data = self.data.reset_index(drop=True)


    # --------- TJSB SAHAKARI BANK LTD -------------
    def parse_tjsb_bank_format(self, path):

        """
        Extracts data from TJSB Sahakari Bank Ltd PDF.
        The columns are:
        SERIAL_NO, DATE, VALUE DATE, TRANS_REF,
        NARRATION, CHQ/REF NO, DEBIT, CREDIT, BALANCE
        """

        rows = []
        seen = set()

        with pdfplumber.open(path, password=self.pdf_password) as pdf:
            for page in pdf.pages:

                tables = page.extract_tables()

                for table in tables:
                    for row in table:

                        # Clean and normalize cells
                        row = [cell.strip() if cell else "" for cell in row]

                        # Skip fully empty rows
                        if all(x == "" for x in row):
                            continue

                        # Skip header rows
                        header_words = [
                            "Transaction", "Value", "Ref", "Narration",
                            "Debit", "Credit", "Balance",
                            "S.N", "Cheque"
                        ]

                        if any(h in row[0] for h in header_words):
                            continue
                        if len(row) > 1 and any(h in row[1] for h in header_words):
                            continue

                        # Normalize to 9 columns
                        fixed = row + [""] * (9 - len(row))
                        fixed = fixed[:9]

                        # Avoid duplicates
                        key = tuple(fixed)
                        if key in seen:
                            continue
                        seen.add(key)

                        # Correct column mapping (as per your requirement)
                        rows.append({
                            "SERIAL_NO": fixed[0],
                            "DATE": fixed[1],
                            "VALUE DATE": fixed[2],
                            "TRANS_REF": fixed[3],
                            "NARRATION": fixed[4],
                            "CHQ/REF NO": fixed[5],
                            "DEBIT": fixed[6],
                            "CREDIT": fixed[7],
                            "BALANCE": fixed[8],
                        })

        # Convert to DataFrame
        df = pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)
        self.data = df

        # Step 1: Remove empty rows
        self.filter_empty_rows_tjsb()

        # Step 2: Merge continuation narration rows + remove summary rows
        self.clean_tjsb_merged_rows()
        # Step 3: TRANS_REF → CHQ/REF NO merge (2 spaces)
        self.merge_transref_into_chequeno()

        return self.data



    def filter_empty_rows_tjsb(self):
        """
        Remove rows where all 9 columns are empty.
        Useful for discarding blank extracted lines.
        """

        if self.data is None or self.data.empty:
            return

        cols = [
            "SERIAL_NO", "DATE", "VALUE DATE",
            "TRANS_REF", "NARRATION", "CHQ/REF NO",
            "DEBIT", "CREDIT", "BALANCE"
        ]

        self.data = self.data[
            self.data[cols].apply(
                lambda r: any(str(v).strip() != "" for v in r),
                axis=1
            )
        ]

        self.data = self.data.reset_index(drop=True)



    def clean_tjsb_merged_rows(self):
        """
        Post-cleaning for TJSB Bank:
        1. Some rows are narration continuation (SERIAL_NO, DATE, VALUE DATE empty).
           These rows must be merged into the previous row's narration.
        2. Rows containing 'Total' without SERIAL_NO / DATE fields are removed.
        """

        if self.data is None or self.data.empty:
            return

        df = self.data.copy()
        rows_to_delete = []

        # --- 1. Merge continuation narration rows ---
        for i in range(1, len(df)):
            current_row = df.loc[i]

            is_continuation = (
                str(current_row["SERIAL_NO"]).strip() == "" and
                str(current_row["DATE"]).strip() == "" and
                str(current_row["VALUE DATE"]).strip() == "" and
                str(current_row["NARRATION"]).strip() != ""
            )

            if is_continuation:
                prev_index = i - 1

                # Append continuation narration to previous row
                df.loc[prev_index, "NARRATION"] = (
                    str(df.loc[prev_index, "NARRATION"]).strip() + " " +
                    str(current_row["NARRATION"]).strip()
                )

                rows_to_delete.append(i)

        # Delete continuation rows
        df = df.drop(rows_to_delete, errors="ignore").reset_index(drop=True)

        # --- 2. Remove 'Total' rows without SERIAL_NO & Date ---
        delete_total = df[
            df["NARRATION"].str.contains("Total", case=False, na=False) &
            (df["SERIAL_NO"].str.strip() == "") &
            (df["DATE"].str.strip() == "") &
            (df["VALUE DATE"].str.strip() == "")
        ].index

        df = df.drop(delete_total, errors="ignore").reset_index(drop=True)

        # Save cleaned dataframe
        self.data = df
    def merge_transref_into_chequeno(self):
        """
        Move TRANS_REF content into CHQ/REF NO with 2 spaces separation.
        Then delete TRANS_REF column.
        """

        if self.data is None or self.data.empty:
            return

        df = self.data.copy()

        # Append TRANS_REF to CHQ/REF NO
        df["CHQ/REF NO"] = (
            df["TRANS_REF"].astype(str).str.strip() +
            "  " +
            df["CHQ/REF NO"].astype(str).str.strip()
        ).str.strip()

        # Remove TRANS_REF column
        df = df.drop(columns=["TRANS_REF"])

        self.data = df.reset_index(drop=True)

    def parse_central_bank_format6(self, path):
        import fitz
        import re
        import pandas as pd

        text_data = ""

        # Read PDF
        with fitz.open(path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text")

        lines = text_data.split("\n")

        final_rows = []
        buffer = ""
        last_balance = None

        # Skip unwanted lines
        skip_words = [
            "STATEMENT OF ACCOUNT", "BROUGHT FORWARD", "CARRIED FORWARD",
            "Statement Summary", "Page No", "Value", "Post", "Details",
            "Debit", "Credit", "Balance", "Date Date"
        ]

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            if any(sw in line for sw in skip_words):
                continue

            # Detect start of transaction (01/04/24)
            if re.match(r"^\d{2}/\d{2}/\d{2}", line):
                if buffer:
                    row = self._process_central_bank_row(buffer, last_balance)
                    if row:
                        final_rows.append(row)
                        if row["BALANCE"]:
                            last_balance = float(row["BALANCE"])
                buffer = line
            else:
                buffer += " " + line

        # Process last entry
        if buffer:
            row = self._process_central_bank_row(buffer, last_balance)
            if row:
                final_rows.append(row)

        # Convert to DF
        df = pd.DataFrame(final_rows)

        # AUTO APPLY narrations fix
        df = self.fix_central_bank_narration(path, df)

        return df


    def _process_central_bank_row(self, text, last_balance):
        import re

        # Example row:
        # 01/04/24 01/04/24 BY TRF. 588.00 3,67,539.90Cr

        match = re.match(
            r"^(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})\s+(.*?)\s+([\d,]*\.?\d+)?\s+([\d,]*\.?\d+)?",
            text
        )

        if not match:
            return None

        date, post_date, particulars, amount, balance = match.groups()

        particulars = particulars.strip()

        debit = ""
        credit = ""

        if amount:
            amount = amount.replace(",", "")

        if balance:
            balance = balance.replace(",", "")
            balance = balance.replace("Cr", "").replace("Dr", "")

        # Credit / Debit logic
        if amount:
            if "TO " in particulars:
                debit = amount
            else:
                credit = amount

        return {
            "DATE": date,
            "POST DATE": post_date,
            "PARTICULARS": particulars,
            "DEBIT": debit,
            "CREDIT": credit,
            "BALANCE": balance
        }


    ####################################################################################
    # NEW FUNCTION — MULTI-LINE NARRATION FIX (AFTER EXTRACTION)
    ####################################################################################
    def fix_central_bank_narration(self, pdf_path, df):
        import fitz
        import re

        # Read PDF again
        text_data = ""
        with fitz.open(pdf_path) as doc:
            if self.pdf_password:
                doc.authenticate(self.pdf_password)
            for page in doc:
                text_data += page.get_text("text")

        # Break PDF into clean lines
        pdf_lines = [ln.strip() for ln in text_data.split("\n") if ln.strip()]

        # Skip header/footer
        skip_words = [
            "STATEMENT OF ACCOUNT", "BROUGHT FORWARD", "CARRIED FORWARD",
            "Statement Summary", "Value", "Post", "Date Date", "Debit", "Credit",
            "Balance", "Page No"
        ]

        txn_lines = []
        for ln in pdf_lines:
            if any(sw in ln for sw in skip_words):
                continue
            txn_lines.append(ln)

        fixed_parts = []

        p = 0   # pointer in PDF lines

        for i in range(len(df)):
            row = df.iloc[i]
            date = row["DATE"]

            # If no date (blank row), keep as is
            if not date:
                fixed_parts.append(row["PARTICULARS"])
                continue

            merged = row["PARTICULARS"]

            # Walk through PDF lines after matched date
            while p < len(txn_lines):

                ln = txn_lines[p]

                # Stop if next date begins (next transaction)
                if re.match(r"^\d{2}/\d{2}/\d{2}", ln) and ln[:8] != date:
                    break

                # Add missing narration lines
                if ln not in merged:
                    merged += " | " + ln

                p += 1

            fixed_parts.append(merged)

        df["PARTICULARS"] = fixed_parts
        return df











    # ----------------- Show Table -----------------
    def show_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        for _, row in self.data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def export_to_excel(self):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            folder = os.path.join(desktop, "PDF to Excel Bank Converter")
            os.makedirs(folder, exist_ok=True)

            base_name = self.bank_var.get().strip()
            file_name = base_name + ".xlsx"
            file_path = os.path.join(folder, file_name)
            count = 1
            while os.path.exists(file_path):
                file_path = os.path.join(folder, f"{base_name} ({count}).xlsx")
                count += 1

            self.data.to_excel(file_path, index=False, sheet_name="Bank Statement")
            messagebox.showinfo("Success", f"Excel file saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel:\n{str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()

    # Create splash
    splash = SplashScreen(root)

    def start_main_app():
        splash.destroy()      # ✅ now works
        root.deiconify()      # show main window
        root.state("zoomed")  # maximize
        app = MainApp(root)

    # Splash duration (adjust if needed)
    root.after(2500, start_main_app)

    root.mainloop()