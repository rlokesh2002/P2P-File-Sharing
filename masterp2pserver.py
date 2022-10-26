import re
from socket import *
import sys

identifier = set() #Set of IP address and port

def process_peer_query(client_addr, client_port_num):
    res = []
    for peer in identifier:
        if peer[0]!=client_addr or peer[1]!=client_port_num:
            res.append(peer)

    return res

def peer_database(client_addr, client_port_num):
    try:
        global identifier
        identifier.add((client_addr, client_port_num))   #Creating a tuple of ip-address and port number
        return True #Successful registration
    except:
        print("Peer registration with Port Number: %d Failed!"%client_port_num)
        return False    #Unsuccessful registration

def unregister_peer(client_addr, client_port_num):
    try:
        global identifier
        identifier.remove((client_addr, client_port_num))   #Creating a tuple of ip-address and port number
        return True #Successful Unregistration
    except:
        print("Peer registration with Port Number: %d Failed!"%client_port_num)
        return False    #Unsuccessful unregistration

def create_socket():
    try:
        global host  # IP address
        global server_port  # Port number
        global s  # socket

        host = ""
        server_port = 40000 #Master server port numbers

        s = socket(AF_INET, SOCK_DGRAM) #AF_INET -> says that the underlying network is using IPv4 and SOCK_DGRAM -> UDP Socket
        print("Master Peer Socket Creation Successful")
    except socket.error as msg:
        print("Master Peer Socket Creation Error: "+str(msg))

#Binding the socket and listening for connection_socketections
def bind_socket():
    try:
        global host  # IP address
        global server_port  # Server Port number
        global s

        print("Master Server Binding the Port %d"%server_port)

        s.bind((host,server_port)) #host and port as tuple
        #No requirement of listening and accepting request - NO Handshake required
        send_commands(s)
        s.close()

    except  socket.error as msg:
        print("Master Peer Socket Binding Error: %s"%str(msg))
        print("Retrying....")
        bind_socket()

#Send commands to a client/victim/friend
def send_commands(s):
    while True:
        client_message, client_address = s.recvfrom(1024)    #Receiving greeting message from client
        client_response = client_message.decode("utf-8") #Decoding message
        print("Received a Message from Peer! | Client IP: %s | Server Port: %d" % (client_address, server_port))
        #print("Client Initial Response: ", client_response)

        #If the message is a registration
        if re.findall('^peer_join_request', client_response):   #If the message starts with "peer_join_request"
            client_ip_addr, client_port_num = client_response.split(',')[1:]    #Seperated by commas
            res = peer_database(client_ip_addr, client_port_num)  #Adding client to identifier database after converting to integers
            response = 0
            if res:
                response = 200
            else:
                response = 500

            s.sendto(str.encode("%d"%response), client_address)   #Send reponse to client regarding registration

        #If the message is a peer inquiry
        elif re.findall('^peer_inquiry', client_response):   #If the message starts with "peer_join_request"
            client_ip_addr, client_port_num = client_response.split(',')[1:]    #Seperated by commas

            peer_list = process_peer_query(client_ip_addr, client_port_num) #Return list of peers except the current peer represented as strings

            response = "@".join([",".join(peer) for peer in peer_list])
            print("Client Response: %s"%response)

            s.sendto(str.encode("%s"%response), client_address)  # Send reponse to client

        elif re.findall('^peer_leave_request', client_response):   #If the message starts with "peer_join_request" :
            client_ip_addr, client_port_num = client_response.split(',')[1:]    #Seperated by commas
            print("Got Peer Leave Request!")
            res = unregister_peer(client_ip_addr, client_port_num)  #Adding client to identifier database after converting to integers
            response = 0
            if res:
                response = 200
            else:
                response = 500
            print("Leave Request Response: %d"%response)
            s.sendto(str.encode("%d"%response), client_address)   #Send reponse to client regarding registration

#Main file to execute the above functions
if __name__ == "__main__":
    create_socket()
    bind_socket()
