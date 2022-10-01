
import PySimpleGUI as sg
import os.path
import sqlite3

conn = sqlite3.connect("Teachers.db") 
c = conn.cursor()


## commit the changes

c.execute("""CREATE TABLE IF NOT EXISTS Teachers_Records (
      fullname text,
      fathername text,
      dob text, 
      document blob
   )""")

conn.commit()


sg.theme('LightGreen1')
sg.set_options(font=('Calibri 12'))
layout_ = [[sg.Push(),sg.Text("Welcome To Teacher's Records", font=('Calibri 16')), sg.Push()], 
            [sg.Text()],
            [sg.Text("Name"),sg.Push(),sg.InputText(key="NAME")],
            [sg.Text("Father's Name"),sg.Push(),sg.InputText(key="FATHER_NAME")], 
            [sg.CalendarButton(button_text = "Date of Birth",  format='%d-%m-%y', no_titlebar=True, close_when_date_chosen=True, target='DOB'),sg.Push(),sg.InputText(default_text="DD-MM-YY",key="DOB")], 
            [sg.Text("Upload Document"),sg.Push(),sg.In(enable_events=True, key="-FILE_PATH-"),sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
            [sg.Text()],
            [sg.Button("Submit", expand_x='True'),sg.Button('Clear', expand_x='True'), sg.Button('Exit', expand_x='True'), sg.Button('Show Records', expand_x='True')],
            [sg.Text()],
            [sg.Push(), sg.Text("Made with ❤ by Maecenas.Inc"), sg.Push()]
         ]

window = sg.Window(title="Teacher's Record Management", layout=layout_)

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")



def read_blob_data(name, fathername, dob):
   conn = sqlite3.connect('Teachers.db') 
   c = conn.cursor()
   sqlite_select_query = "SELECT * from Teachers_Records where fullname=? and fathername=? and dob=?"
   c.execute(sqlite_select_query, (name, fathername, dob,))

   record = c.fetchall()

   for row in record:
      name = row[0]  
      fathername = row[1]
      dob = row[2]
      document_blob = row[3]

      print(name)

      username = os.getlogin()

      #TODO: create a document viewer
      DOCUMENT_PATH = os.getcwd()

      with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
         f.write(document_blob)
      subprocess.Popen([DOCUMENT_PATH, f.name])
      if os.path.exists(f.name):
        os.unlink(f.name)

      #document_path = f"C:\\Users\\{username}\\Downloads\\{name}_{dob}.pdf"
      #writeTofile(document_blob, document_path)
      #sg.PopupQuick("Downloaded the document!")

   c.close()


def retrive_patient_records():
   results = []
   conn = sqlite3.connect('Teachers.db') 
   c = conn.cursor()
   sqlite_select_query = "SELECT fullname, fathername, dob from Teachers_Records"
   c.execute(sqlite_select_query) 

   for row in c:
      results.append(list(row))

   return results

def get_patient_records():
   client_records=retrive_patient_records()
   return client_records

def create_records():
   client_records_array = get_patient_records()
   headings = ['NAME', 'FATHER NAME', 'DATE OF BIRTH']

   layout_for_display = [
      [sg.Text("Name"), sg.Input(size=(25, 1), enable_events=True, key='-NAME_INPUT-'), sg.Push()],

      [sg.Table(values=client_records_array, 
      headings = headings,
      max_col_width=35, 
      auto_size_columns=True,
      display_row_numbers=True,
      justification='left', 
      num_rows=10,
      key="KHOJO_USER_LIST",
      row_height=60,
      enable_events=True,
      tooltip='All Users Records'
       )],
   ]

   windr = sg.Window('Existing User Records', layout_for_display)

   while True:

      curr_record = []
      event, values = windr.read() 
      if event == sg.WIN_CLOSED:
         break
   
      user_names_list = []
      for _ in client_records_array:
         user_names_list.append(_[0])

      if values['-NAME_INPUT-'] != '':                   
         search = values['-NAME_INPUT-'] 
         new_values = [x for x in user_names_list if search in x]  # do the filtering
         client_records_array = [x for x in client_records_array if x[0] in new_values]


         windr['KHOJO_USER_LIST'].update(client_records_array)     # display in the listbox
         print(client_records_array)

      if values['-NAME_INPUT-'] == '':
         # display original unfiltered list
         client_records_array = get_patient_records()
         windr['KHOJO_USER_LIST'].update(client_records_array)     # display in the listbox

      if event == 'KHOJO_USER_LIST':
         
         curr_record = client_records_array[values['KHOJO_USER_LIST'][0]]
         print(curr_record)
         read_blob_data(name=curr_record[0], fathername=curr_record[1], dob=curr_record[2])


def clear_inputs():
   print("Hello world")

   for key in values:
         window['NAME'].update('')
         window['FATHER_NAME'].update('')
         window['DOB'].update('')
         window['-FILE_PATH-'].update('')
   return None  

def convertToBinaryData(filepath):
   with open(filepath, 'rb') as file:
      blobData = file.read()
   
   return blobData

def save_data_to_database(fullname, fathername, dob, filepath):
   conn = sqlite3.connect("Teachers.db") 
   c = conn.cursor()

   ## commit the changes
   sqlite_insert_query = """INSERT INTO Teachers_Records (fullname, fathername, dob, document) VALUES (?, ?, ?, ?)"""
   userDocument = convertToBinaryData(filepath) 
   data_tuple = (fullname, fathername, dob, userDocument)

   c.execute(sqlite_insert_query, data_tuple)
   conn.commit()

   c.close()

conn.commit()

while True:
   event, values = window.read()
   if event == 'Exit' or event == sg.WIN_CLOSED:
      break 

   if event == 'Clear':
      clear_inputs()

   if event == 'Submit':
      name=values['NAME']
      father_name = values['FATHER_NAME']
      dob=values['DOB']
      file=values['-FILE_PATH-']
      if name == '':
         sg.PopupError("Missing Name", "The name Can't be empty")
      if father_name == '':
         sg.PopupError("Missing father's name", "Father's name can't be empty.")
      if dob == '':
         sg.PopupError("Missing DOB", "The DOB can't be empty")
      if file == '':
         sg.PopupError("Missing document", "Please upload the document.")
      else:
         summary_list= "A new record is added to the database:"
         na="\nName: " + values['NAME']
         summary_list += na 
         fna="\nFather's Name: " + values['FATHER_NAME']
         summary_list += fna
         db="\nDate of Birth: " + values['DOB']
         summary_list += db 
         file="\nFile Path: " + values['-FILE_PATH-']
         summary_list += file
         choice = sg.PopupOKCancel(summary_list, "Please Confirm Entry")

         if choice == "OK":
            clear_inputs()
            save_data_to_database(fullname=values['NAME'], fathername=values['FATHER_NAME'], dob=values['DOB'], filepath=values['-FILE_PATH-'])
            sg.PopupQuick("Successfully saved to Database!")
               
         #except:
         #   sg.Popup("Some Error", "kindly report to the team.")

   if event =='Show Records':
      create_records()

window.close()   