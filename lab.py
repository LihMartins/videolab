import sqlite3  # Import the SQLite3 module to work with SQLite databases
from tkinter import *  # Import all classes from the tkinter module
import tkinter.ttk as ttk  # Import the themed tkinter module under the alias 'ttk'
import tkinter.messagebox as mb  # Import the messagebox module from tkinter under the alias 'mb'
import tkinter.simpledialog as sd  # Import the simpledialog module from tkinter under the alias 'sd'

# Connect to SQLite database
connector = sqlite3.connect('video_library.db')  # Create a connection object to the SQLite database
cursor = connector.cursor()  # Create a cursor object to execute SQL queries

# Create table if not exists
cursor.execute(
    'CREATE TABLE IF NOT EXISTS Library (VIDEO_NAME TEXT, VIDEO_ID TEXT PRIMARY KEY NOT NULL, DIRECTOR_NAME TEXT, VIDEO_STATUS TEXT, CARD_ID TEXT)'
)  # Execute an SQL query to create a table if it doesn't exist in the database

def get_card_id():
    """
    Function to get issuer's card ID.

    Returns:
        str: Card ID entered by the user.
    """
    card_id = sd.askstring('Issuer Card ID', 'Enter Issuer Card ID:')  # Display a dialog box to input the card ID
    if not card_id:  # Check if the card ID is not provided
        mb.showerror('Issuer ID cannot be empty!', 'Please provide a valid Issuer ID')  # Display an error message if the card ID is empty
    else:
        return card_id  # Return the card ID entered by the user

def display_records():
    """
    Function to display records in the tree view.
    """
    tree.delete(*tree.get_children())  # Clear all items in the tree view
    curr = cursor.execute('SELECT * FROM Library')  # Execute an SQL query to select all records from the database
    data = curr.fetchall()  # Fetch all the records returned by the query
    for records in data:  # Iterate through each record
        tree.insert('', END, values=records)  # Insert the record into the tree view

def clear_fields():
    """
    Function to clear input fields and selection in the tree view.
    """
    for field in [video_id, video_name, director_name, card_id]:  # Iterate through each input field variable
        field.set('')  # Set the value of the input field variable to an empty string
    try:
        tree.selection_remove(tree.selection()[0])  # Remove the selection from the tree view
    except IndexError:
        pass

def clear_and_display():
    """
    Function to clear input fields, selection, and display records.
    """
    clear_fields()  # Clear input fields and selection in the tree view
    display_records()  # Display records in the tree view

def add_record():
    """
    Function to add a new record to the database.
    """
    if video_status.get() == 'Issued':  # Check if the video status is 'Issued'
        card_id.set(get_card_id())  # Set the card ID by calling the get_card_id function
    else:
        card_id.set('N/A')  # Set the card ID to 'N/A'

    surety = mb.askyesno('Are you sure?', 'Do you want to add this record?')  # Display a confirmation message

    if surety:  # Check if the user confirms the action
        try:
            cursor.execute(
                'INSERT INTO Library (VIDEO_NAME, VIDEO_ID, DIRECTOR_NAME, VIDEO_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (video_name.get(), video_id.get(), director_name.get(), video_status.get(), card_id.get())
            )  # Execute an SQL query to insert a new record into the database
            connector.commit()  # Commit the transaction

            clear_and_display()  # Clear input fields, selection, and display records

            mb.showinfo('Record added', 'New record successfully added')  # Display a success message
        except sqlite3.IntegrityError:
            mb.showerror('Video ID already exists!', 'Video ID already exists')  # Display an error message if the video ID already exists
def issuer_card():
    # Function to retrieve the issuer's card ID
    card_id = sd.askstring('Issuer Card ID', 'Enter Issuer Card ID:')
    if not card_id:
        mb.showerror('Issuer ID cannot be empty!', 'Please provide a valid Issuer ID')
    else:
        return card_id
def update_record():
    def update():
        # Function to update a selected record
        global video_status, video_name, video_id, director_name, clear_id
        global connector, tree 
        
        # Check if the video status is 'Issued'
        if video_status.get() == 'Issued':
            # If it is, set the card_id to the issuer's card
            card_id.set(issuer_card())
        else:
            # If not, set the card_id to 'N/A'
            card_id.set('N/A')
            
        # Execute the SQL command to update the record in the database
        cursor.execute('UPDATE Library SET VIDEO_NAME=?, VIDEO_STATUS=?, DIRECTOR_NAME=?, CARD_ID=? WHERE VIDEO_ID=?', (video_name.get(), video_status.get(), director_name.get(), card_id.get(), video_id.get()))
        # Commit the changes to the database
        connector.commit()
        
        # Clear the fields and display the updated records
        clear_and_display()
        
        # Destroy the 'edit' button
        edit.destroy()
        # Enable the video_id_entry and clear buttons
        video_id_entry.config(state='normal')
        clear.config(state='normal')
        
    # Call the view_record function
    view_record()
    
    # Disable the video_id_entry and clear button
    video_id_entry.config(state='disable')
    clear.config(state='disable')
    
    # Create the 'edit' button and place it on the left_frame
    edit = Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit.place(x=50, y=375)

def view_record():
    """
    Function to view a selected record from the tree view.
    """
    global video_name, video_id, video_status, director_name, card_id
    global tree 

    if not tree.focus():
        mb.showerror('Select a row!', 'To view a record, you must select it in the table. Please, do so before continuing!')
        return
    
    current_item_selected = tree.focus() 
    values_in_selected_item = tree.item(current_item_selected) 
    selection = values_in_selected_item['values'] 
    
    video_name.set(selection[0]) ; video_id.set(selection[1]) ; video_status.set(selection[3]) ; director_name.set(selection[2])

def remove_record():
    """
    Function to remove a selected record from the database.
    """
    if not tree.selection():
        mb.showerror('Error!', 'Please, select an item from the database')
        return
        
    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]
    
    cursor.execute('DELETE FROM Library WHERE VIDEO_ID=?', (selection[1],))
    connector.commit()
    
    tree.delete(current_item)

    mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

    clear_and_display()

def delete_inventory():
    """
    Function to delete the entire inventory from the database.
    """
    if mb.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())

        cursor.execute('DELETE FROM Library')
        connector.commit()
    else:
        return

def change_availability():
    """
    Function to change the availability of a video.
    """
    global card_id, tree, connector

    if not tree.selection():
        mb.showerror('Error!', 'Please select a video from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    VIDEO_id = values['values'][1]
    VIDEO_status = values["values"][3]

    if VIDEO_status == 'Issued':
        surety = mb.askyesno('Is return confirmed?', 'Has the video been returned to you?')
        if surety:
                cursor.execute('UPDATE Library SET video_status=?, card_id=? WHERE video_id=?', ('Available', 'N/A', VIDEO_id))
                connector.commit()
        else: 
                mb.showinfo('Cannot be returned', 'The video status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET video_status=?, card_id=? where video_id=?', ('Issued', get_card_id(), VIDEO_id))
        connector.commit()

    clear_and_display()

# GUI window and Placing its Components
# Variables
lf_bg = 'LightSkyBlue' # Left Frame Background Color
rtf_bg = 'DeepSkyBlue' # Right Top Frame Background Color
rbf_bg = 'DodgerBlue' # Right Bottom Frame Background Color
btn_hlb_bg = 'SteelBlue' # Background color for Head Labels and Buttons

lbl_font = ('Georgia', 13) # Font for all labels
entry_font = ('Times New Roman', 12) # Font for all Entry widgets
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
root = Tk()  # Create a Tkinter window
root.title('PythonGeeks Video Library Management System')  # Set the title of the window
root.geometry('1010x530')  # Set the dimensions of the window
root.resizable(0, 0)  # Disable window resizing

# Create and place a label widget at the top of the window
Label(root, text='VIDEO LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(side=TOP, fill=X)

# StringVars
video_status = StringVar()  # Variable to store the video status
video_name = StringVar()  # Variable to store the video name
video_id = StringVar()  # Variable to store the video ID
director_name = StringVar()  # Variable to store the director's name
card_id = StringVar()  # Variable to store the card ID

# Frames
left_frame = Frame(root, bg=lf_bg)  # Create a frame for input fields on the left side of the window
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)  # Place the left frame within the window

RT_frame = Frame(root, bg=rtf_bg)  # Create a frame for buttons on the right top side of the window
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)  # Place the right top frame within the window

RB_frame = Frame(root)  # Create a frame for the tree view on the right bottom side of the window
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)  # Place the right bottom frame within the window

# Left Frame
# Create and place labels and entry fields for input data in the left frame
Label(left_frame, text='Video Name', bg=lf_bg, font=lbl_font).place(x=98, y=25)
Entry(left_frame, width=25, font=entry_font, text=video_name).place(x=45, y=55)

Label(left_frame, text='Video ID', bg=lf_bg, font=lbl_font).place(x=110, y=105)
video_id_entry = Entry(left_frame, width=25, font=entry_font, text=video_id)
video_id_entry.place(x=45, y=135)

Label(left_frame, text='Director Name', bg=lf_bg, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, text=director_name).place(x=45, y=215)

Label(left_frame, text='Status of the Video', bg=lf_bg, font=lbl_font).place(x=75, y=265)
dd = OptionMenu(left_frame, video_status, *['Available', 'Issued'])
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)

# Create buttons for adding a new record and clearing fields in the left frame
submit = Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record)
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
# Create buttons for deleting a video record, deleting the full inventory, updating video details, and changing video availability in the right top frame
Button(RT_frame, text='Delete video record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8, y=30)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
Button(RT_frame, text='Update video details', font=btn_font, bg=btn_hlb_bg, width=17, command=update_record).place(x=348, y=30)
Button(RT_frame, text='Change Video Availability', font=btn_font, bg=btn_hlb_bg, width=19, command=change_availability).place(x=518, y=30)

# Right Bottom Frame
# Create a label for 'VIDEO INVENTORY' and a tree view for displaying records in the right bottom frame
Label(RB_frame, text='VIDEO INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)
tree = ttk.Treeview(RB_frame, selectmode=BROWSE, columns=('Video Name', 'Video ID', 'Director', 'Status', 'Issuer Card ID'))
XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)
tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)
tree.heading('Video Name', text='Video Name', anchor=CENTER)
tree.heading('Video ID', text='Video ID', anchor=CENTER)
tree.heading('Director', text='Director', anchor=CENTER)
tree.heading('Status', text='Status of the Video', anchor=CENTER)
tree.heading('Issuer Card ID', text='Card ID of the Issuer', anchor=CENTER)
tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)
tree.place(y=30, x=0, relheight=0.9, relwidth=1)

clear_and_display()

# Finalizing the window
root.update()
root.mainloop()
