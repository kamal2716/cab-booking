import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import random
import os

# Delete the existing database if it exists to reset it
if os.path.exists('cab_booking.db'):
    os.remove('cab_booking.db')

# List of famous places in Chennai
famous_places = ["Marina Beach", "Fort St. George", "Kapaleeshwarar Temple", "Santhome Cathedral Basilica",
                 "Arignar Anna Zoological Park", "Valluvar Kottam", "Guindy National Park", "Express Avenue",
                 "Elliot's Beach", "Birla Planetarium", "Thousand Lights Mosque", "Government Museum",
                 "Chennai Central", "Phoenix Marketcity", "Cholamandal Artists' Village"]

# Initialize the database
def initialize_db():
    conn = sqlite3.connect('cab_booking.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        cab_name TEXT NOT NULL,
        service_due_date DATE NOT NULL,
        spare_type TEXT NOT NULL,
        spare_usage INTEGER NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        user_phone TEXT NOT NULL,
        pickup TEXT NOT NULL,
        destination TEXT NOT NULL,
        driver_name TEXT NOT NULL,
        driver_phone TEXT NOT NULL,
        fare INTEGER NOT NULL,
        otp INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rating INTEGER,
        accident_description TEXT
    )
    ''')

    # Add default owner account
    c.execute('INSERT OR IGNORE INTO users (username, password, phone) VALUES (?, ?, ?)', ('kamal', '1234', '1234567890'))

    # Add default drivers
    default_drivers = [
        ('John Doe', '9876543210', 'Toyota Innova', '2024-12-31', 'Brake Pads', 5000),
        ('Jane Smith', '8765432109', 'Honda City', '2024-11-30', 'Oil Filter', 3000),
        ('James Brown', '7654321098', 'Maruti Swift', '2024-10-31', 'Air Filter', 2000),
    ]
    c.executemany('INSERT INTO drivers (name, phone, cab_name, service_due_date, spare_type, spare_usage) VALUES (?, ?, ?, ?, ?, ?)', default_drivers)

    conn.commit()
    conn.close()

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x300")

        tk.Label(root, text="KSA Cabs", font=("Helvetica", 20, "bold")).pack(pady=20)

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.login).pack(pady=20)
        tk.Button(root, text="Register", command=self.show_registration_window).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.root.destroy()
            root = tk.Tk()
            if username == 'kamal' and password == '1234':
                app = OwnerDashboard(root)
            else:
                app = CabBookingApp(root, username)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def show_registration_window(self):
        self.root.destroy()
        root = tk.Tk()
        app = RegistrationWindow(root)
        root.mainloop()

class RegistrationWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Register")
        self.root.geometry("400x400")

        tk.Label(root, text="Register", font=("Helvetica", 20, "bold")).pack(pady=20)

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="Phone").pack(pady=5)
        self.phone_entry = tk.Entry(root)
        self.phone_entry.pack(pady=5)

        tk.Button(root, text="Register", command=self.register).pack(pady=20)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        phone = self.phone_entry.get()

        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()

        try:
            c.execute('INSERT INTO users (username, password, phone) VALUES (?, ?, ?)', (username, password, phone))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.root.destroy()
            root = tk.Tk()
            app = LoginWindow(root)
            root.mainloop()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        finally:
            conn.close()

class OwnerDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Owner Dashboard")
        self.root.geometry("800x600")

        tk.Label(root, text="Owner Dashboard", font=("Helvetica", 20, "bold")).pack(pady=20)

        tk.Button(root, text="View All Drivers", command=self.view_drivers).pack(pady=10)
        tk.Button(root, text="View All Bookings", command=self.view_bookings).pack(pady=10)
        tk.Button(root, text="View Service Reminders", command=self.view_service_reminders).pack(pady=10)
        tk.Button(root, text="Logout", command=self.logout).pack(pady=10)

    def view_drivers(self):
        self.display_table("SELECT * FROM drivers", ["ID", "Name", "Phone", "Cab Name", "Service Due Date", "Spare Type", "Spare Usage"])

    def view_bookings(self):
        self.display_table("SELECT * FROM bookings", ["ID", "Username", "User Phone", "Pickup", "Destination", "Driver Name", "Driver Phone", "Fare", "OTP", "Payment Method", "Booking Time", "Rating", "Accident Description"])

    def view_service_reminders(self):
        self.display_table("SELECT * FROM drivers WHERE service_due_date < date('now', '+30 days')", ["ID", "Name", "Phone", "Cab Name", "Service Due Date", "Spare Type", "Spare Usage"])

    def display_table(self, query, cols):
        top = tk.Toplevel(self.root)
        top.title("Data View")
        top.geometry("800x600")

        listBox = ttk.Treeview(top, columns=cols, show='headings')

        for col in cols:
            listBox.heading(col, text=col)
            listBox.column(col, width=100)

        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        conn.close()

        for row in rows:
            listBox.insert("", "end", values=row)
        
        listBox.pack(expand=True, fill='both')

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        app = LoginWindow(root)
        root.mainloop()

class CabBookingApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Cab Booking")
        self.root.geometry("600x600")

        tk.Label(root, text="Book a Cab", font=("Helvetica", 20, "bold")).pack(pady=20)

        tk.Label(root, text="Pickup Location").pack(pady=5)
        self.pickup_combobox = ttk.Combobox(root, values=famous_places)
        self.pickup_combobox.pack(pady=5)

        tk.Label(root, text="Destination").pack(pady=5)
        self.destination_combobox = ttk.Combobox(root, values=famous_places)
        self.destination_combobox.pack(pady=5)

        tk.Label(root, text="Payment Method").pack(pady=5)
        self.payment_method_combobox = ttk.Combobox(root, values=["Cash", "Credit Card", "UPI"])
        self.payment_method_combobox.pack(pady=5)

        tk.Button(root, text="Book Now", command=self.book_cab).pack(pady=20)

    def book_cab(self):
        pickup_location = self.pickup_combobox.get()
        destination = self.destination_combobox.get()
        payment_method = self.payment_method_combobox.get()

        if not pickup_location or not destination or not payment_method:
            messagebox.showerror("Error", "All fields are required!")
            return

        if pickup_location == destination:
            messagebox.showerror("Error", "Pickup and destination cannot be the same!")
            return

        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()

        # Get a random driver for the booking
        c.execute('SELECT * FROM drivers ORDER BY RANDOM() LIMIT 1')
        driver = c.fetchone()
        if not driver:
            messagebox.showerror("Error", "No drivers available!")
            conn.close()
            return

        driver_name, driver_phone, cab_name = driver[1], driver[2], driver[3]

        # Get user's phone number
        c.execute('SELECT phone FROM users WHERE username = ?', (self.username,))
        user_phone = c.fetchone()[0]

        fare = random.randint(100, 500)
        otp = random.randint(1000, 9999)

        c.execute('''
        INSERT INTO bookings (username, user_phone, pickup, destination, driver_name, driver_phone, fare, otp, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.username, user_phone, pickup_location, destination, driver_name, driver_phone, fare, otp, payment_method))
        conn.commit()
        conn.close()

        confirmation_message = f'''
        Booking Confirmed!
        Driver: {driver_name}
        Phone: {driver_phone}
        Cab: {cab_name}
        OTP: {otp}
        Pickup: {pickup_location}
        Destination: {destination}
        Fare: {fare} INR
        Payment Method: {payment_method}
        '''
        messagebox.showinfo("Booking Confirmation", confirmation_message)

        self.ask_accident_occurred()

    def ask_accident_occurred(self):
        if messagebox.askyesno("Accident", "Did any accident occur during the trip?"):
            description = simpledialog.askstring("Accident Description", "Please describe the accident:")
            self.rate_driver(description)
        else:
            self.rate_driver(None)

    def rate_driver(self, accident_description):
        rating = simpledialog.askinteger("Rate Driver", "Rate the driver (0-10):", minvalue=0, maxvalue=10)

        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()
        c.execute('''
        UPDATE bookings
        SET rating = ?, accident_description = ?
        WHERE id = (SELECT MAX(id) FROM bookings)
        ''', (rating, accident_description))
        conn.commit()
        conn.close()

        if messagebox.askyesno("Thank You", "Thank you for booking KSA cabs. Do you want to book another cab?"):
            self.root.destroy()
            root = tk.Tk()
            app = CabBookingApp(root, self.username)
            root.mainloop()
        else:
            self.root.destroy()
            root = tk.Tk()
            app = LoginWindow(root)
            root.mainloop()

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
