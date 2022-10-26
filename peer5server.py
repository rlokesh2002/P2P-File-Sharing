from socket import *
import subprocess
import sys
import glob
import os
import re

peer_num = 5
curr_path = os.getcwd()


def create_socket():
    try:
        global host  # IP address
        global server_port  # Port number
        global s  # socket

        host = ""
        server_port = 4090 #peer1 server port numbers

        s = socket(AF_INET, SOCK_DGRAM) #AF_INET -> says that the underlying network is using IPv4 and SOCK_DGRAM -> UDP Socket

    except socket.error as msg:
        print("Peer %d Socket Creation Error: %s"%(peer_num,str(msg)))

#Binding the socket and listening for connection_socketections
def bind_socket():
    try:
        global host  # IP address
        global server_port  # Server Port number
        global s  # socket  -> This is a server socket used as 'Welcoming socket'

        print("Peer %d Server Binding the Port %d"%(peer_num, server_port))

        s.bind((host,server_port)) #host and port as tuple
        #No requirement of listening and accepting request - NO Handshake required
        send_commands(s)
        s.close()

    except  socket.error as msg:
        print("Peer %d Socket Binding Error: %s"%(peer_num, str(msg)))
        print("Retrying....")
        bind_socket()

#Send commands to a client/victim/friend
def send_commands(s):
    while True:
        client_message, client_address = s.recvfrom(1024)    #Receiving greeting message from client
        client_response = client_message.decode("utf-8") #Decoding message
        print("Received a Message from Peer! | Client IP: %s | Server Port: %d" % (client_address, server_port))
        #print(client_response)

        #If the message is a file inquiry
        if re.findall('^file_inquiry', client_response):
            file_name, client_ip_addr, client_port_num = client_response.split(',')[1:]    #Seperated by commas

            file_path = glob.glob('%s/**/%s'%(curr_path, file_name), recursive=True)    #Search for file
            resp = ""

            if len(file_path) > 0:
               txt_file = file_path[0]
               num_charc = 0
               with open(txt_file, 'r') as f:
                   for line in f:
                       line = line.strip(os.linesep)
                       num_charc = num_charc + sum(1 for c in line if c not in (os.linesep, ' '))

               resp = "FileFound, %d"%(num_charc)

            else:
               resp = "FileError"

            s.sendto(str.encode("%s" % resp), client_address)  # Send reponse to client

        elif re.findall('^file_request', client_response):
            file_name, client_ip_addr, client_port_num = client_response.split(',')[1:]    #Seperated by commas

            file_path = glob.glob('%s/**/%s'%(curr_path, file_name), recursive=True)    #Search for file
            resp = ""

            if len(file_path) > 0:
               txt_file = file_path[0]
               file_txt = ""
               with open(txt_file, 'r') as f:
                   file_txt = f.read()

               resp = file_txt

            else:
               resp = "FileError"

            s.sendto(str.encode("%s" % resp), client_address)  # Send reponse to client



#Main file to execute the above functions
if __name__ == "__main__":
    create_socket()
    bind_socket()
