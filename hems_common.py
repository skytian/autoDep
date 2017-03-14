#!/usr/bin/python
#set java environment
import os
import tarfile
import urllib2
import sys
import time
import socket


#function exe shell commond
def echo_exe(str_cmd, err_list):
	print(str_cmd);
	ret = os.system(str_cmd);
	if ret == 0:
		print(str_cmd + ' success');
	else:
		print(str_cmd + ' error');
		err_list.append(str_cmd);

def set_java_env():
    os.environ['JAVA_HOME']='/opt/casa/jdk1.7.0_67';
    os.environ['JRE_HOME']='/opt/casa/jdk1.7.0_67/jre'
    os.environ['CLASSPATH']='.:/opt/casa/jdk1.7.0_67/lib:/opt/casa/jdk1.7.0_67/jre/lib:'
    path_env = os.environ['PATH']
    os.environ['PATH']= path_env + ':/opt/casa/jdk1.7.0_67/bin'

def check_exist(file_name):
	return os.path.exists(file_name)

def check_tomcat_port(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((ip, int(port)))
		s.shutdown(2)
		print '%d is open' % port
		return True
	except:
		print  '%d is down' % port
		return False


def untar(fname, dirs):
	try:
		print 'start untar '+ fname + ' to ' + dirs
		t = tarfile.open(fname)
		t.extractall(path = dirs)
		print 'compete untar!'
	except:
		print 'untar file failed!'
		sys.exit()

def update_mysql(mysql_usr, mysql_pwd, mysql_db_file):
	print '\n\n\nstart update mysql database......'
	err_list = []
	if os.path.exists(mysql_db_file):
		if mysql_db_file[-4:] == '.sql':
			if os.path.exists('/usr/local/mysql/bin/mysql'):
				cmd = '/usr/local/mysql/bin/mysql -u ' + mysql_usr + ' -p'+ mysql_pwd + ' -e \'drop database hemsdb;\'';
				echo_exe(cmd, err_list);
				cmd = '/usr/local/mysql/bin/mysql -u ' + mysql_usr + ' -p'+ mysql_pwd + ' -e \'create database hemsdb;\'';
				echo_exe(cmd, err_list);
				cmd = '/usr/local/mysql/bin/mysql -u ' + mysql_usr + ' -p'+ mysql_pwd + ' hemsdb < ' + mysql_db_file;
				echo_exe(cmd, err_list);
			else:
				print 'please ensure mysql is running'
				sys.exit()
			print 'complete update mysql database......\n\n\n'
		else:
			print 'please input right format package like *.sql'
	else:
		print 'please input right path mysql database file!'


def update_software(software_file):
	print '\n\n\nstart update mysql database......'
	err_list = []
	if os.path.exists(software_file):
		if software_file[-4:] == '.war':
			if os.path.exists('/opt/casa/apache-tomcat-7.0.65/webapps/'):
				cmd = 'cp ' + software_file + ' /opt/casa/apache-tomcat-7.0.65/webapps/'
				echo_exe(cmd, err_list);
				cmd = '/opt/casa/apache-tomcat-7.0.65/bin/shutdown.sh'
				time.sleep(2)
				echo_exe(cmd, err_list);
				cmd = '/opt/casa/apache-tomcat-7.0.65/bin/startup.sh'
				echo_exe(cmd, err_list);
				time.sleep(2);
			else:
				print 'please install tomcat!'
				sys.exit()
			print 'complete update hems......\n\n\n'
		else:
			print 'please input right format package like *.war'
	else:
		print 'please input right hems package path'

def download_file(url, filename):
	if not check_exist(filename):
	    u = urllib2.urlopen(url)

	    #scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

	    with open(filename, 'wb') as f:
	        meta = u.info()
	        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
	        meta_length = meta_func("Content-Length")
	        file_size = None
	        if meta_length:
	            file_size = int(meta_length[0])
	        print("Downloading: {0} Bytes: {1}".format(filename, file_size))

	        file_size_dl = 0
	        block_sz = 8192
	        while True:
	            buffer = u.read(block_sz)
	            if not buffer:
	                break

	            file_size_dl += len(buffer)
	            f.write(buffer)

	            status = "{0:16}".format(file_size_dl)
	            if file_size:
	                status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
	            status += chr(13)
	    print ("download {0} success".format(filename))
	    return filename
	else:
		print filename + ' is already exist!\n'

class Package:
	def __init__(self, file_name, install_path, url, header_list):
		self.file_name = file_name
		self.install_path = install_path
		self.url = url
		self.header_list = header_list

	def set_name(self, file_name):
		self.file_name = file_name

	def print_all(self):
		print self.file_name
		print self.install_path
		print self.url
		print self.header_list

	def set_install_path(self, install_path):
		self.install_path = install_path

	def set_url(self, url):
		self.url = url

	def set_header(self, header_list):
		self.header_list = header_list

	def decompress_file(self):
		untar(self.file_name, self.set_install_path)

	def download_package(self):
		if not check_exist(self.file_name):
			list_len = len(self.header_list)
			if not list_len == 0:
				if list_len == 3:
					req = urllib2.Request(self.url)
					req.add_header('Cookie', self.header_list[0])
					req.add_header('X-Forwarded-For',self.header_list[1])
					req.add_header('User-Agent',self.header_list[2])
					download_file(req, self.file_name)
				else:
					print 'need 3 header to download this file'
			else:
				download_file(self.url, self.file_name)
		else:
			print 'exist package '+ self.file_name

	def untar_package(self):
		try:
			untar(self.file_name, self.install_path)
		except:
			print 'untar package error!'
			sys.exit()









