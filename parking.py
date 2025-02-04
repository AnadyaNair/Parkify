from tkinter import *
from tkinter import messagebox
from datetime import datetime
import mysql.connector as sqltor
import csv

# Connect to MySQL database
mycon = sqltor.connect(
    host="localhost",
    user="root",
    password="admin123",  # Replace with your MySQL password
    database="parking_db"  # Ensure the database exists
)
cursor = mycon.cursor()

# Functions for database operations
def add_vehicle():
    """
    Adds a vehicle to the parking database.
    Validates the license plate format and prevents duplicate entries.
    Logs the operation in a text file.
    """
    vehicle_no = vehicle_entry.get().upper()  # Convert input to uppercase
    if not vehicle_no:
        messagebox.showerror("Input Error", "License plate cannot be empty!")
        return
    if len(vehicle_no) > 10:
        messagebox.showerror("Format Error", "License plate format is invalid!")
        return

    # Check for duplicate entry
    cursor.execute("SELECT vehicle_no FROM parking WHERE vehicle_no = %s", (vehicle_no,))
    if cursor.fetchone():
        messagebox.showerror("Duplicate Entry", "Vehicle already parked!")
        return

    registration_time = datetime.now()
    # Insert vehicle into the database
    cursor.execute("INSERT INTO parking (vehicle_no, registration_time) VALUES (%s, %s)",
                   (vehicle_no, registration_time))
    mycon.commit()
    log_operation("ADD", vehicle_no)  # Log the operation
    vehicle_entry.delete(0, END)  # Clear the input field
    refresh_list()

def delete_vehicle():
    """
    Removes a vehicle from the parking database.
    Calculates the tariff based on parking duration and logs the operation.
    """
    selected = vehicle_listbox.get(ACTIVE)  # Get the selected vehicle from the listbox
    if not selected:
        messagebox.showerror("Selection Error", "No vehicle selected!")
        return

    vehicle_id, vehicle_no = selected.split(" ")[0], selected.split(" ")[1]  # Extract vehicle ID and number
    cursor.execute("SELECT registration_time FROM parking WHERE id = %s", (vehicle_id,))
    entry_time = cursor.fetchone()[0]
    exit_time = datetime.now()

    # Calculate duration and tariff
    duration = (exit_time - entry_time).total_seconds() / 3600  # Duration in hours
    tariff = max(10, round(duration * 20))  # ₹20 per hour, minimum ₹10

    cursor.execute("DELETE FROM parking WHERE id = %s", (vehicle_id,))
    mycon.commit()
    log_operation("REMOVE", vehicle_no)  # Log the operation
    messagebox.showinfo("Tariff", f"Vehicle removed. Total parking fee: ₹{tariff}")
    refresh_list()

def refresh_list():
    """
    Refreshes the list of parked vehicles displayed in the GUI.
    """
    cursor.execute("SELECT id, vehicle_no, registration_time FROM parking")
    vehicles = cursor.fetchall()
    vehicle_listbox.delete(0, END)  # Clear the listbox

    # Add each vehicle to the listbox
    for vehicle in vehicles:
        vehicle_listbox.insert(END, f"{vehicle[0]} {vehicle[1]} - {vehicle[2].strftime('%Y-%m-%d %H:%M:%S')}")

def search_vehicle():
    """
    Searches for a vehicle by its license plate.
    Displays the search result in a dialog box.
    """
    search_query = vehicle_entry.get().upper()  # Get search input
    if not search_query:
        messagebox.showerror("Search Error", "Enter a license plate to search!")
        return

    cursor.execute("SELECT * FROM parking WHERE vehicle_no = %s", (search_query,))
    result = cursor.fetchone()
    if result:
        # Display vehicle details
        messagebox.showinfo("Search Result", f"Vehicle Found: {result[1]} - {result[2]}")
    else:
        messagebox.showerror("Search Result", "Vehicle not found!")

def display_total_vehicles():
    """
    Displays the total number of vehicles currently parked.
    """
    cursor.execute("SELECT COUNT(*) FROM parking")
    count = cursor.fetchone()[0]
    messagebox.showinfo("Total Vehicles", f"Total vehicles parked: {count}")

def export_to_csv():
    """
    Exports the current parking data to a CSV file.
    """
    cursor.execute("SELECT * FROM parking")
    vehicles = cursor.fetchall()
    with open("parking_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Vehicle No", "Registration Time"])  # Write headers
        writer.writerows(vehicles)  # Write data rows

    messagebox.showinfo("Export", "Parking data exported to parking_data.csv")

def log_operation(operation, vehicle_no):
    """
    Logs an operation (ADD/REMOVE) with details into a text file.
    """
    with open("parking_log.txt", "a") as log_file:
        log_file.write(f"{operation} - {vehicle_no} at {datetime.now()}\n")

# Tkinter GUI setup
root = Tk()
root.title("Parkify Parking Management")

# Vehicle License Plate Label and Entry
Label(root, text="Vehicle License Plate:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
vehicle_entry = Entry(root, width=20, relief="solid", borderwidth=2)
vehicle_entry.grid(row=0, column=1, padx=10, pady=10)

# Frame for the Floating Panel (Buttons)
button_frame = Frame(root)
button_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="n")

# Buttons in the Floating Panel
Button(button_frame, text="Register Parking Slot", command=add_vehicle).grid(row=0, column=0, padx=5, pady=5, sticky="w")
Button(button_frame, text="Remove Vehicle", command=delete_vehicle).grid(row=1, column=0, padx=5, pady=5, sticky="w")
Button(button_frame, text="Search Vehicle", command=search_vehicle).grid(row=2, column=0, padx=5, pady=5, sticky="w")
Button(button_frame, text="Total Vehicles", command=display_total_vehicles).grid(row=3, column=0, padx=5, pady=5, sticky="w")
Button(button_frame, text="Export to CSV", command=export_to_csv).grid(row=4, column=0, padx=5, pady=5, sticky="w")

# Listbox to display parked vehicles
vehicle_listbox = Listbox(root, width=50, height=15)
vehicle_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Load the vehicle list initially
refresh_list()

# Run the Tkinter event loop
root.mainloop()