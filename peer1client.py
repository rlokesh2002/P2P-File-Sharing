from socket import *
import subprocess
import sys
import glob
import os
import re

master_server_ip_addr = "127.0.0.1"
master_server_port = 40000
peer_num = 1

curr_path = os.getcwd()

p2p_reg = False

peer_server_ip_addr = "127.0.0.1"  # IP address
peer_server_port = 4050  # Port number
global s  # UDP Client socket


def run_program():
    # Create socket
    global s
    try:
        s = socket(AF_INET, SOCK_DGRAM)  # AF_INET -> says that the underlying network is using IPv4 and SOCK_DGRAM -> UDP Socket
        peer_registration()
    except socket.error as msg:
        print("Socket Creation Error: " + str(msg))
        sys.exit("Peer %d Client Socket Creation Error" % peer_num)


# Running the Client
def peer_registration():
    key = input("Press R to Register Peer %d with Master Peer else press any other key:     " % peer_num)
    global p2p_reg
    if key == "R":
        s.sendto(str.encode("peer_join_request,%s,%d" % (peer_server_ip_addr, peer_server_port)),
                 (master_server_ip_addr, master_server_port))
        reg_response, server_addr = s.recvfrom(1024)  # Chunk size
        reg_response = reg_response.decode("utf-8")
        if reg_response == "200":
            p2p_reg = True
            print("Peer %d Registration to P2P Network Successful" % peer_num)

            peer_network_function()
        else:
            p2p_reg = False
            print("Peer %d Registration to P2P Network Unsuccessful" % peer_num)

    else:
        print("Wrong Key entered! | Couldn't Register with Master Server | Try again to register\n")
        peer_registration()

    return

def peer_network_function():
    print("Welcome to P2P file sharing. This is Peer %d"%peer_num)
    while True:
        file_name = input("Enter the file name to start download:   ")
        file_path = glob.glob('%s/**/%s'%(curr_path, file_name), recursive=True)

        if len(file_path)>0:
            print("File present locally, no need for file transfer")
        else:
            available_peers = requestmasterpeer()
            if len(available_peers) == 0:
                print("No Peers Available! | Couldn't Fetch the file at the moment | Please Try Again Later")
                continue
            else:
                break_loop = requestfile(available_peers, file_name)
                if break_loop:
                    break
    return

def requestmasterpeer():
    s.sendto(str.encode("peer_inquiry,%s,%d" % (peer_server_ip_addr, peer_server_port)), (master_server_ip_addr, master_server_port))
    peerlist, server_addr = s.recvfrom(4096)  # Chunk size
    peerlist = peerlist.decode("utf-8")
    print("Peerlist: %s"%peerlist)
    if peerlist == '':
        return []
    available_peers = peerlist.split("@")   #Splitting by delimiter
    for i in range(len(available_peers)):
        available_peers[i] = available_peers[i].split(",")
        available_peers[i] = tuple([available_peers[i][0], int(available_peers[i][1])])   #converting port number to int

    print("Available Peers", end = ": ")
    print(available_peers)

    return available_peers


def requestfile(peers, filename):
    peers_with_file = []
    for peer in peers:
        peer_ip_addr = peer[0]
        peer_port = peer[1]
        s.sendto(str.encode("file_inquiry,%s,%s,%d" % (filename, peer_server_ip_addr, peer_server_port)), (peer_ip_addr, peer_port))
        peer_response, peer_server_addr = s.recvfrom(4096)  # Chunk size
        peer_response = peer_response.decode("utf-8")
        if peer_response == 'FileError':  # File Not found with the peer
            continue
        elif re.findall('^FileFound', peer_response):  # File found with the peer
            char_cnt = int(peer_response.split(",")[1])
            peers_with_file.append((char_cnt, peer))

    print("Peers with File: ", end="")
    print(peers_with_file)

    file_txt = ""

    final_peer = peers_with_file[0]  # Peer from whom file should be requested

    # Select the peer who has more character count
    for peer in peers_with_file:
        if final_peer[0] < peer[0]:
            final_peer = peer

    peer_ip_addr = final_peer[1][0]
    peer_port = final_peer[1][1]
    s.sendto(str.encode("file_request,%s,%s,%d" % (filename, peer_server_ip_addr, peer_server_port)),
             (peer_ip_addr, peer_port))
    peer_response, peer_server_addr = s.recvfrom(4096)  # Chunk size
    peer_response = peer_response.decode("utf-8")

    if peer_response == 'FileError':  # File Not found with the peer
        print("File Deleted Quickly!")
    else:
        file_txt = ""

        flag = peer_response[0]
        while flag=='0':
            file_txt += peer_response[1:]
            peer_response, peer_server_addr = s.recvfrom(4096)  # Chunk size
            peer_response = peer_response.decode("utf-8")
            print("Flag: %s"%flag)
            flag = peer_response[0]

        print("Flag: %s" % flag)
        file_txt += peer_response[1:]


        print("#########File '%s' Retrieved!############\n" % filename)
        key = input("Enter D to print the file content or Enter U to unregister & Exit from peer network and press any other key to skip:   ")
        if key == 'D':
            print(file_txt)
        elif key == 'U':
            peer_unregistration()
            return True

    return  False

# Running the Client
def peer_unregistration():
    global p2p_reg

    s.sendto(str.encode("peer_leave_request,%s,%d" % (peer_server_ip_addr, peer_server_port)), (master_server_ip_addr, master_server_port))
    reg_response, server_addr = s.recvfrom(1024)  # Chunk size
    reg_response = reg_response.decode("utf-8")
    if reg_response == "200":
        p2p_reg = False
        print("Peer %d Unregistration to P2P Network Successful | Exiting Program" % peer_num)
    else:
        print("Couldn't unregister | Trying Again....\n")
        peer_unregistration()

    return



if __name__ == "__main__":
    run_program()