from socket import *
import ssl
import base64

commands=[]


def insert_command(cmd):
    new_cmd = ">>> " + cmd.replace('\r', '').replace('\n', f'\n>>> {cmd[:8]}')
    new_cmd = new_cmd.split('\n')
    # new_cmd = list(filter(lambda a: a != a[:12], new_cmd))
    commands.extend(new_cmd)

from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import copy

def create_mime_multipart(send_from, send_to, subject, text, files):

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))
    clone_msg = copy.deepcopy(msg)
    for f in files or []:
        f = f.replace('\r', '\\r').replace('\t', '\\t').replace('\a', '\\a').replace('\f', '\\f').replace('\v', '\\v').replace('\b', '\\b').replace('\n', '\\n')
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
        clone_part = copy.deepcopy(part)
        clone_part.set_payload('base64 encoded data')
        clone_msg.attach(clone_part)
        
    return [msg.as_string(), clone_msg.as_string()]


def smtp_send_mail(username, password, receiver, subjects, msg, files):
    commands.clear()
    input_username = username
    input_password = password
    input_receiver = receiver
    input_subject = subjects
    input_msg = msg

    # msg = "\r\n" + input_msg
    endmsg = "\r\n.\r\n"

    address    = "smtp.gmail.com"
    port       = 465
    mailserver = (address, port)

    sockplain = socket(AF_INET) 
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    clientSocket = context.wrap_socket(sockplain, server_hostname=address)
    
    clientSocket.connect(mailserver)
    
    recv = clientSocket.recv(1024)
    recv = recv.decode()
    print("Message after connection request:" + recv)
    insert_command("SERVER: " + recv[:-2])
    if recv[:3] != '220':
        print('220 reply not received from server.')
    heloCommand = f'EHLO {address}\r\n'
    insert_command("CLIENT: " + heloCommand[:-2])
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024)
    recv1 = recv1.decode()
    insert_command("SERVER: " + recv1[:-2])
    print("Message after EHLO command:" + recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')

    #Info for username and password
    username = input_username
    password = input_password

    base64_str = ("\x00"+username+"\x00"+password).encode()
    base64_str = base64.b64encode(base64_str)
    authMsg = "AUTH PLAIN ".encode()+base64_str+"\r\n".encode()
    print(authMsg)
    clientSocket.send(authMsg)
    authMsg = authMsg.decode()
    insert_command("CLIENT: " + authMsg[:-2])
    recv_auth = clientSocket.recv(1024)
    print("response 1: " + recv_auth.decode())
    insert_command("SERVER: " + recv_auth.decode()[:-2])


    mailFrom = "MAIL FROM:<"+ username +">\r\n"
    insert_command("CLIENT: " + mailFrom[:-2])
    clientSocket.send(mailFrom.encode())
    recv2 = clientSocket.recv(1024)
    recv2 = recv2.decode()
    print("After MAIL FROM command: "+recv2)
    insert_command("SERVER: " + recv2[:-2])
    rcptTo = "RCPT TO:<"+ input_receiver +">\r\n"
    insert_command("CLIENT: " + rcptTo[:-2])
    clientSocket.send(rcptTo.encode())
    recv3 = clientSocket.recv(1024)
    recv3 = recv3.decode()
    print("After RCPT TO command: "+recv3)
    insert_command("SERVER: " + recv3[:-2])
    data = "DATA\r\n"
    insert_command("CLIENT: " + data[:-2])
    clientSocket.send(data.encode())
    recv4 = clientSocket.recv(1024)
    recv4 = recv4.decode()
    print("After DATA command: "+recv4)
    insert_command("SERVER: " + recv4[:-2])

    # subject = "Subject: "+ input_subject +"\r\n\r\n" 
    # clientSocket.send(subject.encode())
    # insert_command("CLIENT: " + subject)
    # clientSocket.send(msg.encode())
    # insert_command("CLIENT: " + msg)

    mime_multipart = create_mime_multipart(input_username, input_receiver, input_subject, input_msg, files)
    clientSocket.send(mime_multipart[0].replace('\n', '\r\n').encode())
    insert_command("CLIENT: " + mime_multipart[1])

    clientSocket.send(endmsg.encode())
    insert_command("CLIENT: " + endmsg.replace('\r\n', ''))
    recv_msg = clientSocket.recv(1024)
    print("Response after sending message body:"+recv_msg.decode())
    insert_command("SERVER: " + recv_msg.decode()[:-2])
    quit = "QUIT\r\n"
    insert_command("CLIENT: " + quit[:-2])
    clientSocket.send(quit.encode())
    recv5 = clientSocket.recv(1024)
    print(recv5.decode())
    insert_command("SERVER: " + recv5.decode()[:-2])
    clientSocket.close()
    return commands