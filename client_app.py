from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import messagebox

from smtp_gmail import smtp_send_mail
from threading import Thread
from time import sleep

def insert_command(commands):
    command_list.configure(state='normal')
    command_list.insert(END, commands+"\n")
    command_list.see(END)
    command_list.configure(state='disable')
    sleep(0.1)

def send():
    command_list.configure(state='normal')
    command_list.delete('1.0', END)
    command_list.configure(state='disable')
    if username_text.get() == '' or password_text.get() == '' or Sendto_text.get() == '' or subject_text.get() == '' or message_text.get('1.0', END) == '':
        messagebox.showwarning('ERROR', 'PLEASE ENTER ALL FIELDS!!!')
        return
    send_btn.configure(state='disable', text='sending...')
    insert_command(">>> CLIENT: ESTABLISHING TCP CONNECTION TO SERVER smtp.gmail.com, port:465...")
    cmd_list = smtp_send_mail(username_text.get(), password_text.get(), Sendto_text.get(), subject_text.get(), message_text.get('1.0', END), file_list.get('1.0', END).replace('\n', '').split(';'))
    send_btn.configure(state='active', text='send mail')
    for i in cmd_list:
        insert_command(i)

def browse_file():
    filename = filedialog.askopenfilenames(title="SELECT ATTACHMENT FILE", filetype=(('jpeg', '*jpg'), ('ALL TPYE', '*.*')))
    filename = list(filename)
    file_list.configure(state='normal')
    file_list.delete('1.0', END)
    file_list.insert('1.0', ';'.join(filename))
    file_list.configure(state='disable')

    

# create window
app = Tk()

app.title('SMTP CLIENT PROGRAM')
app.geometry('700x600')

# username
username_text = StringVar()
username_label = Label(app, text='username', font=('bold', 14), pady=20)
username_label.grid(row=0, column=0, sticky=W)
username_entry = Entry(app, textvariable=username_text, width=35)
username_entry.grid(row=0, column=1, sticky=W)
# password
password_text = StringVar()
password_label = Label(app, text='password', font=('bold', 14))
password_label.grid(row=0, column=2, sticky=W)
password_entry = Entry(app, textvariable=password_text, show="*")
password_entry.grid(row=0, column=3, sticky=W)
# Send to
Sendto_text = StringVar()
Sendto_label = Label(app, text='Send to', font=('bold', 14))
Sendto_label.grid(row=1, column=0, sticky=W)
Sendto_entry = Entry(app, textvariable=Sendto_text, width=35)
Sendto_entry.grid(row=1, column=1, sticky=W)
# subject
subject_text = StringVar()
subject_label = Label(app, text='subject', font=('bold', 14), pady=20)
subject_label.grid(row=2, column=0, sticky=W)
subject_entry = Entry(app, textvariable=subject_text, width=35)
subject_entry.grid(row=2, column=1, sticky=W)
# message
message_text = ScrolledText(app, width=60,height=6)
message_label = Label(app, text='message', font=('bold', 14))
message_label.grid(row=3, column=0, sticky=NW)
message_text.grid(row=3, column=1, columnspan=3, sticky=W)
# file_list
file_list = Text(app, height=1, width=47, wrap=NONE, state='disable')
file_list.grid(row=4, column=1, columnspan=3, sticky=W)
textHsb = Scrollbar(orient="horizontal", command=file_list.xview)
file_list.configure(xscrollcommand=textHsb.set)
textHsb.grid(row=5, column=1, columnspan=2, sticky=EW)

# button
send_btn = Button(app, text='add attachments', state='active', command=browse_file)
send_btn.grid(row=4, column=0, padx=10, sticky=W)
send_btn = Button(app, text='send mail', state='active', command=lambda: Thread(target=send).start())
send_btn.grid(row=6, column=0, columnspan=4, pady=10)

# create listbox
command_list = ScrolledText(app, height=15, width=82, border=0, state='disable')
command_list.grid(row=7, column=0, columnspan=4, rowspan=6, padx=15, sticky=W)

# start program
app.mainloop()
