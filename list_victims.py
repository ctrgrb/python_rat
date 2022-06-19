import os, time
from termcolor import colored

def list_victims():
	f1 = open("/root/Folder/RAT/.IPs",'r')
	print("|═══════════════════════════|VICTIMS|═══════════════════════════|")
	IP_LIST = f1.readlines()
	for ips in IP_LIST:
		ip, port = ips.split("<SEPARATOR>")
		print("["+str(IP_LIST.index(ips))+"]"+"~~~[IP: "+colored(str(ip),'cyan',attrs=['bold'])+" / Port: "+colored(int(port),'magenta')+"]")
	print("|═══════════════════════════════════════════════════════════════|")

def main():
	os.system("clear")
	while True:
		try:
			list_victims()
			print(colored("\nListening...", 'yellow',attrs=['bold']))
			with open("/root/Folder/RAT/.log",'r') as f2:
				for line in f2.readlines():
					if line == "Server closed...":
						return
					elif "Connection lost from: " in line:
						print(colored(line[:-1], 'red',attrs=['bold']))
					else:
						print(colored(line[:-1], 'green',attrs=['bold']))
			time.sleep(2)
			os.system("clear")
		except: break
			
main()