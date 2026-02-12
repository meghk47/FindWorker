import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import random
from datetime import datetime

# --- CONFIGURATION & COLORS ---
APP_COLOR = "#008080"  # Teal
BTN_COLOR = "#005555"
BG_COLOR = "#F0F2F5"
CARD_COLOR = "#FFFFFF"

# --- DATABASE MANAGER ---
class Database:
    def __init__(self, db_name="workforce_pro.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.seed_admin()

    def create_tables(self):
        # Users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT,
                phone TEXT
            )
        """)
        # Workers (Expanded info)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                experience TEXT,
                rate TEXT,
                phone TEXT,
                address TEXT,
                availability TEXT,
                rating TEXT
            )
        """)
        # Requests (Booking System)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_user TEXT,
                worker_name TEXT,
                work_date TEXT,
                status TEXT, -- Pending, Accepted, Rejected
                payment_status TEXT
            )
        """)
        # Feedback
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                comment TEXT
            )
        """)
        self.conn.commit()

    def seed_admin(self):
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", 
                              ("admin", "admin123", "admin", "0000000000"))
            # Seed Demo Workers
            demos = [
                ("Ramesh Patil", "Electrician", "10 Yrs", "₹300/hr", "9890011223", "Shivaji Nagar, Pune", "9 AM - 6 PM", "4.8"),
                ("Suresh Kale", "Plumber", "5 Yrs", "₹200/hr", "9988776655", "Satara Road", "10 AM - 5 PM", "4.5"),
                ("Sunita Deshmukh", "Farm Helper", "8 Yrs", "₹500/day", "8877665544", "Village Zone 2", "6 AM - 2 PM", "4.9")
            ]
            self.cursor.executemany("INSERT INTO workers (name, category, experience, rate, phone, address, availability, rating) VALUES (?,?,?,?,?,?,?,?)", demos)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor

# --- UI COMPONENTS ---

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg=APP_COLOR, fg="white", font=("Segoe UI", 10, "bold"), 
                    relief="flat", activebackground=BTN_COLOR, padx=10, pady=5)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg=BG_COLOR)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_window = tk.Frame(canvas, bg=BG_COLOR)

        self.scrollable_window.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_window, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# --- APP CONTROLLER ---

class WorkforceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rural Workforce Connect Pro")
        self.geometry("450x700")
        self.configure(bg=BG_COLOR)
        self.db = Database()
        self.user_data = None
        self.language = "English"

        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)
        
        self.switch_frame(LoginScreen)

    def switch_frame(self, frame_class):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = frame_class(self.container, self)
        frame.pack(fill="both", expand=True)

# --- SCREENS ---

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Logo/Header
        header = tk.Frame(self, bg=APP_COLOR, height=150)
        header.pack(fill="x")
        tk.Label(header, text="Digital Workforce", bg=APP_COLOR, fg="white", 
                 font=("Segoe UI", 20, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Form
        form_frame = tk.Frame(self, bg="white", padx=20, pady=20)
        form_frame.pack(pady=40, padx=20, fill="x")

        tk.Label(form_frame, text="Login", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=(0, 20))

        tk.Label(form_frame, text="Username", bg="white").pack(anchor="w")
        self.user_entry = ttk.Entry(form_frame)
        self.user_entry.pack(fill="x", pady=(0, 10))

        tk.Label(form_frame, text="Password", bg="white").pack(anchor="w")
        self.pass_entry = ttk.Entry(form_frame, show="*")
        self.pass_entry.pack(fill="x", pady=(0, 20))

        ModernButton(form_frame, text="LOGIN", command=self.do_login).pack(fill="x")
        
        tk.Button(self, text="New User? Sign Up Here", bg=BG_COLOR, fg=APP_COLOR, 
                  bd=0, command=lambda: controller.switch_frame(SignupScreen)).pack(pady=10)

    def do_login(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Please fill all fields")
            return

        res = self.controller.db.query("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        if res:
            self.controller.user_data = {"username": res[0], "role": res[2]}
            if res[2] == "admin":
                self.controller.switch_frame(AdminDashboard)
            else:
                self.controller.switch_frame(LanguageScreen)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

class SignupScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        
        tk.Label(self, text="Create Account", font=("Segoe UI", 18, "bold"), bg=BG_COLOR).pack(pady=30)
        
        f = tk.Frame(self, bg="white", padx=20, pady=20)
        f.pack(padx=20, fill="x")

        tk.Label(f, text="Username", bg="white").pack(anchor="w")
        self.u_ent = ttk.Entry(f)
        self.u_ent.pack(fill="x")
        
        tk.Label(f, text="Password", bg="white").pack(anchor="w")
        self.p_ent = ttk.Entry(f, show="*")
        self.p_ent.pack(fill="x")

        tk.Label(f, text="Phone Number", bg="white").pack(anchor="w")
        self.ph_ent = ttk.Entry(f)
        self.ph_ent.pack(fill="x")

        tk.Label(f, text="Role (customer/admin)", bg="white").pack(anchor="w")
        self.role_ent = ttk.Entry(f)
        self.role_ent.insert(0, "customer")
        self.role_ent.pack(fill="x", pady=(0,20))

        ModernButton(f, text="REGISTER", command=self.register).pack(fill="x")
        tk.Button(self, text="< Back to Login", bg=BG_COLOR, bd=0, 
                  command=lambda: controller.switch_frame(LoginScreen)).pack(pady=10)

    def register(self):
        u, p, ph, r = self.u_ent.get(), self.p_ent.get(), self.ph_ent.get(), self.role_ent.get()
        if not u or not p or not ph:
            messagebox.showerror("Wait", "All fields are required!")
            return
        
        try:
            self.controller.db.query("INSERT INTO users VALUES (?,?,?,?)", (u, p, r, ph))
            messagebox.showinfo("Success", "Account created successfully!")
            self.controller.switch_frame(LoginScreen)
        except:
            messagebox.showerror("Error", "Username taken")

class LanguageScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        tk.Label(self, text="Select Language", font=("Segoe UI", 16, "bold"), bg=BG_COLOR).pack(pady=50)
        
        for lang, lbl in [("English", "English"), ("Hindi", "हिंदी"), ("Marathi", "मराठी")]:
            ModernButton(self, text=lbl, font=("Arial", 14), 
                         command=lambda l=lang: self.set_lang(l, controller)).pack(fill="x", padx=40, pady=10)

    def set_lang(self, l, c):
        c.language = l
        c.switch_frame(CustomerDashboard)

# --- CUSTOMER PANEL ---

class CustomerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_home = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_status = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_profile = tk.Frame(self.notebook, bg=BG_COLOR)

        self.notebook.add(self.tab_home, text="Find Workers")
        self.notebook.add(self.tab_status, text="My Bookings")
        self.notebook.add(self.tab_profile, text="Profile")

        self.build_home()
        self.build_status()
        self.build_profile()

    def build_home(self):
        scroll = ScrollableFrame(self.tab_home)
        scroll.pack(fill="both", expand=True)

        # Header
        tk.Label(scroll.scrollable_window, text=f"Welcome, {self.controller.user_data['username']}", 
                 bg=BG_COLOR, font=("Arial", 14, "bold"), fg=APP_COLOR).pack(pady=10, padx=10, anchor="w")

        # Worker Cards
        workers = self.controller.db.query("SELECT * FROM workers").fetchall()
        for w in workers:
            self.create_worker_card(scroll.scrollable_window, w)

    def create_worker_card(self, parent, data):
        # data: id, name, type, exp, rate, phone, address, avail, rating
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", padx=10, pady=8)

        # Avatar
        avatar = tk.Canvas(card, width=50, height=50, bg="#e0e0e0", highlightthickness=0)
        avatar.pack(side="left", padx=10, pady=10)
        avatar.create_oval(5,5,45,45, fill=APP_COLOR)
        avatar.create_text(25,25, text=data[1][0], fill="white", font=("Arial", 20, "bold"))

        # Info
        info = tk.Frame(card, bg="white")
        info.pack(side="left", fill="both", expand=True, pady=5)
        
        tk.Label(info, text=data[1], font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(info, text=f"{data[2]} | Exp: {data[3]} | ⭐ {data[8]}", bg="white", fg="gray").pack(anchor="w")
        tk.Label(info, text=f"📍 {data[6]}", bg="white", font=("Arial", 8)).pack(anchor="w")
        tk.Label(info, text=f"🕒 {data[7]}", bg="white", font=("Arial", 8)).pack(anchor="w")
        tk.Label(info, text=f"📞 {data[5]}", bg="white", font=("Arial", 8, "bold")).pack(anchor="w")

        # Action
        action_frame = tk.Frame(card, bg="white")
        action_frame.pack(side="right", padx=10)
        tk.Label(action_frame, text=data[4], font=("Arial", 12, "bold"), fg="green", bg="white").pack()
        ModernButton(action_frame, text="Book Now", command=lambda: self.book_worker(data)).pack(pady=5)

    def book_worker(self, worker_data):
        # Simulating a booking dialog
        dialog = tk.Toplevel(self)
        dialog.title("Confirm Booking")
        dialog.geometry("300x350")
        dialog.configure(bg="white")

        tk.Label(dialog, text=f"Book {worker_data[1]}", font=("bold"), bg="white").pack(pady=10)
        
        tk.Label(dialog, text="Select Date (DD/MM/YYYY):", bg="white").pack()
        date_ent = ttk.Entry(dialog)
        date_ent.insert(0, datetime.now().strftime("%d/%m/%Y"))
        date_ent.pack(pady=5)

        def proceed_payment():
            if not date_ent.get(): return
            self.payment_gateway(worker_data, date_ent.get(), dialog)

        ModernButton(dialog, text="Proceed to Payment", command=proceed_payment).pack(pady=20)

    def payment_gateway(self, worker, date_str, old_window):
        old_window.destroy()
        pay_win = tk.Toplevel(self)
        pay_win.title("Secure Payment")
        pay_win.geometry("350x400")
        
        tk.Label(pay_win, text="Payment Gateway", font=("Arial", 16, "bold"), fg=APP_COLOR).pack(pady=20)
        tk.Label(pay_win, text=f"Paying: {worker[4]}", font=("Arial", 12)).pack()

        tk.Label(pay_win, text="Select Method:").pack(anchor="w", padx=20)
        combo = ttk.Combobox(pay_win, values=["UPI", "Credit Card", "Cash on Work"])
        combo.current(0)
        combo.pack(fill="x", padx=20, pady=5)

        tk.Label(pay_win, text="Enter Details (UPI ID / Card No):").pack(anchor="w", padx=20)
        detail = ttk.Entry(pay_win)
        detail.pack(fill="x", padx=20, pady=5)

        def complete():
            if not detail.get():
                messagebox.showerror("Error", "Enter Payment Details")
                return
            
            # Save Request
            self.controller.db.query(
                "INSERT INTO requests (customer_user, worker_name, work_date, status, payment_status) VALUES (?,?,?,?,?)",
                (self.controller.user_data['username'], worker[1], date_str, "Pending", "Success")
            )
            messagebox.showinfo("Success", "Booking Request Sent! Wait for Worker Acceptance.")
            pay_win.destroy()
            self.refresh_status_tab()

        ModernButton(pay_win, text="PAY NOW", command=complete).pack(pady=20, fill="x", padx=20)

    def build_status(self):
        # Refresh logic
        for widget in self.tab_status.winfo_children(): widget.destroy()
        
        tk.Label(self.tab_status, text="My Bookings Status", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=10)
        
        cols = ("Worker", "Date", "Status", "Payment")
        tree = ttk.Treeview(self.tab_status, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Load data
        rows = self.controller.db.query("SELECT worker_name, work_date, status, payment_status FROM requests WHERE customer_user=?", 
                                      (self.controller.user_data['username'],)).fetchall()
        for r in rows:
            tree.insert("", "end", values=r)

    def refresh_status_tab(self):
        self.build_status()

    def build_profile(self):
        tk.Label(self.tab_profile, text="User Profile", font=("bold"), bg=BG_COLOR).pack(pady=20)
        ModernButton(self.tab_profile, text="Logout", 
                     command=lambda: self.controller.switch_frame(LoginScreen)).pack()
        
        # Feedback
        tk.Label(self.tab_profile, text="Send App Feedback:", bg=BG_COLOR).pack(pady=(20,5))
        fb_ent = tk.Entry(self.tab_profile)
        fb_ent.pack()
        def send_fb():
            if fb_ent.get():
                self.controller.db.query("INSERT INTO feedback (user, comment) VALUES (?,?)", 
                                       (self.controller.user_data['username'], fb_ent.get()))
                messagebox.showinfo("Thanks", "Feedback Recorded")
        ModernButton(self.tab_profile, text="Submit", command=send_fb).pack(pady=5)

# --- ADMIN PANEL ---

class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        
        tk.Label(self, text="ADMIN CONTROL PANEL", bg="#333", fg="white", font=("Arial", 14)).pack(fill="x", pady=0)
        
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        
        self.f_req = tk.Frame(nb)
        self.f_work = tk.Frame(nb)
        
        nb.add(self.f_req, text="Manage Requests")
        nb.add(self.f_work, text="Manage Workers")
        
        self.setup_requests()
        self.setup_workers()
        
        tk.Button(self, text="Logout", command=lambda: controller.switch_frame(LoginScreen)).pack(pady=5)

    def setup_requests(self):
        tk.Label(self.f_req, text="Pending Requests", font=("bold")).pack(pady=10)
        
        cols = ("ID", "Customer", "Worker", "Status")
        self.tree = ttk.Treeview(self.f_req, columns=cols, show="headings", height=8)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("ID", width=30)
        self.tree.pack(fill="x", padx=10)

        # Load Pending
        self.refresh_requests()

        btn_frame = tk.Frame(self.f_req)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="ACCEPT", bg="green", fg="white", command=lambda: self.update_status("Accepted")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="REJECT", bg="red", fg="white", command=lambda: self.update_status("Rejected")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_requests).pack(side="left", padx=5)

    def refresh_requests(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = self.controller.db.query("SELECT id, customer_user, worker_name, status FROM requests").fetchall()
        for r in rows:
            self.tree.insert("", "end", values=r)

    def update_status(self, status):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        req_id = item['values'][0]
        self.controller.db.query("UPDATE requests SET status=? WHERE id=?", (status, req_id))
        self.refresh_requests()
        messagebox.showinfo("Updated", f"Request marked as {status}")

    def setup_workers(self):
        # Simple Add Form
        f = tk.Frame(self.f_work)
        f.pack(pady=10)
        
        entries = {}
        labels = ["Name", "Category", "Experience", "Rate", "Phone", "Address", "Availability"]
        for l in labels:
            tk.Label(f, text=l).pack()
            e = tk.Entry(f)
            e.pack()
            entries[l] = e
            
        def add_w():
            vals = [entries[l].get() for l in labels]
            if "" in vals:
                messagebox.showerror("Error", "Fill all fields")
                return
            vals.append("4.0") # Default rating
            self.controller.db.query("INSERT INTO workers (name, category, experience, rate, phone, address, availability, rating) VALUES (?,?,?,?,?,?,?,?)", vals)
            messagebox.showinfo("Success", "Worker Added")
            
        tk.Button(f, text="Add New Worker", command=add_w).pack(pady=10)

if __name__ == "__main__":
    app = WorkforceApp()
    app.mainloop()
