from functools import partial
from tkinter import *
from tkinter import messagebox
import pymysql
import color as cs
import database as cr
from datetime import datetime
from tkinter import ttk 

class Management:
    def __init__(self, root):
        self.window = root
        self.window.title("Hotel Management")
        self.window.maxsize(width=940, height=680)
        self.window.minsize(width=940, height=680)
        self.window.config(bg="white")

        # Customization
        self.color_1 = cs.color_1
        self.color_2 = cs.color_2
        self.color_3 = cs.color_3
        self.color_4 = cs.color_4
        self.font_1 = cs.font_1
        self.font_2 = cs.font_2

        # User Credentials
        self.host = cr.host
        self.user = cr.user
        self.password = cr.password
        self.database = cr.database

        self.initial()


    def initial(self) :
        
        # Left Frame
        self.frame_1 = Frame(self.window, bg=self.color_1)
        self.frame_1.place(x=0, y=0, width=940, height=100)

        # Right Frame
        self.frame_2 = Frame(self.window, bg=self.color_2)
        self.frame_2.place(x=0, y=100, width=940, height=580)

        # Buttons
        Button(self.frame_1, text='MENU', font=(self.font_1, 12), bd=2,
               command=self.Menu, cursor="hand2",
               bg=self.color_1, fg=self.color_3).place(x=40, y=40, width=90)
        Button(self.frame_1, text='ORDER', font=(self.font_1, 12), bd=2,
               command=self.Order, cursor="hand2",
               bg=self.color_1, fg=self.color_3).place(x=160, y=40, width=90)
        Button(self.frame_1, text='EXIT', font=(self.font_1, 12), bd=2,
               command=self.Exit, cursor="hand2",
               bg=self.color_1, fg=self.color_3).place(x=280, y=40, width=90)

    def Order(self):
        self.ClearScreen()
        
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            curs = connection.cursor()
            
            curs.execute("SELECT Food_name, Price FROM menu")
            menu_items = curs.fetchall()
            
            self.quantity_entries = {}
            for food_name, price in menu_items:
                self.foodname = Label(self.frame_2, text=f"{food_name} - {price:.2f}rs", font=(self.font_1, 12), bg=self.color_2)
                self.foodname.pack(pady=5)

                self.quantity_entry = Entry(self.frame_2, width=5)
                self.quantity_entry.pack(pady=5)
                self.quantity_entries[food_name] = self.quantity_entry
            
            submit_button = Button(self.frame_2, text='Submit Order', font=(self.font_1, 12),
                                   command=self.submit_order, bg=self.color_3, fg="white")
            submit_button.pack(pady=20)

        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            curs.close()
            connection.close()

    def submit_order(self):
        
        order_details = {}
        total_value = 0

        connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        
        curs = connection.cursor()
        
        curs.execute("SELECT Food_name, Price FROM menu")
        menu_items = curs.fetchall()
        
        for food_name, entry in self.quantity_entries.items():
            quantity = entry.get()
            if quantity.isdigit() and int(quantity) > 0:
                order_details[food_name] = int(quantity)

        for food_name,price in menu_items:
            if food_name in order_details:
                total_value+=price * order_details[food_name]

        for name in order_details:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        
            curs = connection.cursor()
            curs.execute('select food_id,price from menu where food_name = (%s)',(name))
            item_details = curs.fetchone()
            print(item_details)
            curs.execute('insert into food_orders (food_id,quantity,food_price,total_value,date) values (%s,%s,%s,%s,%s)',
                         (item_details[0],
                          order_details[name],
                          item_details[1],
                          (order_details[name]*item_details[1]),
                          datetime.now().date()
                          ))
            connection.commit()
            connection.close()

        self.reset_fields()


        print(total_value)
        print(type(total_value))

        
        if order_details:
            messagebox.showinfo("Order Submitted", f"Your order: {order_details}")
        else:
            messagebox.showwarning("Input Error", "Please enter valid quantities for your order.")


    def ClearScreen(self):
        for widget in self.frame_2.winfo_children():
            widget.destroy()

    def Exit(self):
        self.window.destroy()

    def Menu(self):
        self.ClearScreen()
        # Create a Treeview to display the menu
        columns = ("food_id", "food_name", "quantity", "price")
        self.tree = ttk.Treeview(self.frame_2, columns=columns, show="headings")
        
        # Define the column headings
        self.tree.heading("food_id", text="Food ID")
        self.tree.heading("food_name", text="Food Name")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("price", text="Price (rs)")

        # Set column widths
        self.tree.column("food_id", width=100)
        self.tree.column("food_name", width=200)
        self.tree.column("quantity", width=100)
        self.tree.column("price", width=100)

        self.tree.pack(pady=20)  # Place the Treeview in the frame

        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            curs = connection.cursor()
            curs.execute("SELECT food_id, food_name, quantity, price FROM menu")
            menu_items = curs.fetchall()

            # Insert data into the Treeview
            for item in menu_items:
                self.tree.insert("", "end", values=item)

        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            curs.close()
            connection.close()

    def reset_fields(self):
        for entry in self.quantity_entries.values():
            entry.delete(0, END)

# The main function
if __name__ == "__main__":
    root = Tk()
    obj = Management(root)
    root.mainloop()
