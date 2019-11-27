import socket
import os
import hashlib
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


server = socket.socket()
server.bind(("localhost", 9998))

def decode_data(data):
	if data.decode()==("fail"):
		return data.decode()
	else:
		return struct.unpack('I',data)[0]

def encode_data(data):
	return struct.pack('I',data)

def login_check(uname,password):
	username="Elapse"
	client_password="md5password"  #这里是md5密码
	if uname.decode()==username:
		if password.decode() == client_password:
			return "Login_success"
		else:
			return "Login_Fail"
	else:
		return "Login_Fail"

server.listen(5)
print("已开启FTP服务..")
check_close=""
while True:
	if check_close=="close":
		break
	conn,addr = server.accept()
	print("检测到新连接: ", addr,"  正在验证身份...")
	uname = conn.recv(6)
	password=conn.recv(33)
	checking=login_check(uname,password)
	if checking=="Login_success":
		conn.send("login_succ".encode())
		while True:
			print("等待客户端指令中....")
			data = conn.recv(1024)
			if not data:  #如果没有数据，则断开连接
				print("断开连接")
				break
			a = str(data.decode())
			if a.startswith("put"):
				receive_file_size = decode_data(conn.recv(4))
				if receive_file_size==('fail'):
					print("文件上传失败，客户端文件不存在")
				else:
					print("正在接收大小为"+str(receive_file_size)+"的文件")
					receive_size = 0
					file_total_size = int(receive_file_size)
					#获取文件名
					filename = data.split()[1]
					f = open(filename.decode() + ".client", "wb")
					while file_total_size > receive_size:
						if file_total_size - receive_size > 1024:
							size = 1024
						else:
							size = file_total_size - receive_size
							print("剩下没接收的数据大小为: ",size)
						data = conn.recv(size)
						receive_size += len(data)
						f.write(data)
					else:
						print("文件传输完成")
						print(receive_size, file_total_size)
						f.close()
			if str(data.decode()) == ("dir"):
				list_file = os.listdir('.')
				ls = len(list_file)
				conn.send(encode_data(ls))  #告诉客户端目录有多少个文件，也就是for循环多少次接收
				num=1
				for i in list_file:
					print("当前目录下第"+str(num)+"个文件: "+i)
					conn.send(encode_data(len(i)))  # 发送文件名的长度，让客户端做好包限制
					conn.send(i.encode())  # 发送文件名
					num += 1
				continue
			if a.startswith("del"):
				filename = data.split()[1]
				fail=("Error")
				if os.path.exists(filename):
					print("正在执行文件删除...")
					os.remove(filename.decode())
					text=("文件删除完毕")
					print(text)
					conn.send(text.encode())
				else:
					print("文件删除失败，该文件不存在")
					conn.send(fail.encode())


			if a.startswith("get"):
				filename=data.decode().split()[1]
				if os.path.isfile(filename):
					f = open(filename, "rb")
					m = hashlib.md5() #创建MD5对象
					file_size = os.stat(filename).st_size #os.stat(path) .st_size指定内容为文件大小
					conn.send(encode_data(file_size))
					conn.recv(24)
					for line in f:
						conn.send(line)
						m.update(line)
					#输出文件MD5
					print("文件MD5值: ", m.hexdigest())
					conn.send(m.hexdigest().encode())
					f.close()
				else:
					conn.send("fail".encode())
					print("客户端下载失败，文件不存在")
			
			if str(data.decode()) == ("close"):
				print("服务关闭....")
				check_close="close"
				break
	elif checking=="Login_Fail":
		print("账户名或者密码错误")
		conn.send("login_fail".encode())
		pass
server.close()
