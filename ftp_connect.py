import socket
import hashlib
import os
import time
import struct
import hashlib
print('''

 /$$$$$$$$ /$$
| $$_____/| $$
| $$      | $$  /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$
| $$$$$   | $$ |____  $$ /$$__  $$ /$$_____/ /$$__  $$
| $$__/   | $$  /$$$$$$$| $$  \ $$|  $$$$$$ | $$$$$$$$
| $$      | $$ /$$__  $$| $$  | $$ \____  $$| $$_____/
| $$$$$$$$| $$|  $$$$$$$| $$$$$$$/ /$$$$$$$/|  $$$$$$$
|________/|__/ \_______/| $$____/ |_______/  \_______/
                        | $$
                        | $$
                        |__/

''')
client = socket.socket()
server_ip=input("请输入服务端IP地址: ")
client.connect((server_ip, 9998))

def encode_data(data):
	return struct.pack('I',data)

def decode_data(data):
	try:
		if data.decode()==("fail"):
			return data.decode()
		else:
			return struct.unpack('I',data)[0]
	except UnicodeDecodeError:
		return struct.unpack('I',data)[0]
def md5pass(password):
	m=hashlib.md5()
	b=password.encode(encoding='utf-8')
	m.update(b)
	return m.hexdigest()

fail=("fail")

uname=str(input("请输入用户名："))
password=str(input("请输入密码："))

client.send(uname.encode())
client.send(md5pass(password).encode())

logincheck=client.recv(10)
if logincheck.decode()=="login_succ":
	while True:
		cmd = input("请输入命令 (help)查看帮助信息: ").strip()
		if cmd ==("help"):
			print('''
			帮助信息:
			命令语法: <命令> <文件名>  |  <command> <filename>
			dir  查看当前目录下所有文件 | View all files in the current directory
			del <filename>  删除指定文件 | Delete specify file
			get <filename>  下载文件 | Download file
			put <filename>  上传文件  | Upload file
			close  关闭服务器FTP功能  |  Service closure
			''')
		elif cmd.startswith("put"):
			client.send(cmd.encode())
			print("正在发送文件中...")
			cmd1,filename=cmd.split()
			if os.path.exists(filename):
				print(filename)
				f = open(filename, "rb")
				file_size = os.stat(filename).st_size
				client.send(encode_data(file_size))
				for line in f:
					client.send(line)
				f.close()
			else:
				print("文件上传失败，该文件不存在")
				client.send(fail.encode())
		elif len(cmd) == 0:
			continue
		#判断命令是否是exit
		elif cmd == ("exit"):
			print("Bye")
			break
		#目录遍历
		elif cmd == ("dir"):
			client.send(cmd.encode())
			file_num = decode_data(client.recv(4)) # 从服务端那接收需要for循环多少次的数据（也就是多少个文件）
			print("总共有"+str(file_num).replace('b\'','').replace('\'','')+"个文件")
			for i in range(int(file_num)):
				filename_size=client.recv(4)  # 文件名长度
				list_file = client.recv(decode_data(filename_size)) #只接收这个长度的包
				print("当前目录有: ",list_file.decode('utf8'))
			continue
		#文件删除
		elif cmd.startswith("del"):
			print("正在删除文件...")
			client.send(cmd.encode())
			error = client.recv(1024)
			print(error.decode())
			if error.decode() == ("Error"):
				print("文件删除失败，该文件不存在")
			else:
				print("文件删除成功")
		#文件下载
		elif cmd.startswith("get"):
			client.send(cmd.encode())
			#接收来自服务器的数据（文件大小）
			receive_file_size = decode_data(client.recv(4))
			if receive_file_size == ("fail"):
				print("文件下载失败，该文件不存在")
			else:
				print("server file size: ",str(receive_file_size)) 
				#这里对应server.py的第26行，需要发送数据给服务端接受后继续执行下面的操作，可删除
				client.send("really to send the file".encode())
				#初始化接收数据的大小为0
				receive_size = 0
				file_total_size = int(receive_file_size)
				#切片，把前面的get给去掉
				filename = cmd.split()[1]
				f = open(filename + ".server", "wb")
				m = hashlib.md5()
				#防止数据沾包
				while file_total_size > receive_size:
					#若剩下的数据还有1024没接收，则size定义为1024，再收1024个数据
					if file_total_size - receive_size > 1024:
						size = 1024
					else:
					#没有大于1024，则剩下多少接收多少
						size = file_total_size - receive_size
						print("剩下没接收的数据大小为: ",size)
					data = client.recv(size)

					receive_size += len(data)
					m.update(data)
					f.write(data)
				else:
					new_file_md5 = m.hexdigest()
					print("文件接收完成")
					print(receive_size, file_total_size)
					f.close()
				receive_file_md5 = client.recv(1024)
				print("MD5校验值: ", receive_file_md5.decode())
				print("下载文件MD5校验值: ", new_file_md5)
		elif cmd == ("close"):
			client.send(cmd.encode())
			break
		else:
			print("命令错误!")
			continue
else:
	print("[-] 用户名或密码错误")

client.close()
