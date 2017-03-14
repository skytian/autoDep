#!/usr/bin/python
import  sys
import  os
import  time
import  shutil
import  tarfile
import  urllib2
import  ConfigParser
import  hems_common
import  hems_install



#check run in unix like environment
def check_env():
	sys_name = os.name
	if not sys_name == 'posix':
	    print 'please run in linux like system!'
	    sys.exit();


def echo_exe(str_cmd, err_list):
	print(str_cmd);
	ret = os.system(str_cmd);
	if ret == 0:
		print(str_cmd + ' success');
	else:
		print(str_cmd + ' error');
		err_list.append(str_cmd);

def write_nms_property():
	config_list = [
	'[Mysql]','db.mysql.driverCls=com.mysql.jdbc.Driver','db.mysql.hostname=172.0.5.207','db.mysql.port=3306','db.mysql.name=hemsdb','db.mysql.username=root','db.mysql.password=casa',
	'[MongoDB]','db.mongo.hostname=localhost','db.mongo.name=hemsdb',
	'[ThreadPool]','nms.threadpool.corepoolsize = 64','nms.threadpool.maxpoolsize = 64',
	'[LogPatterns]','hemsLogAddr = /opt/casa/logs/', 'maxHistory=30',
	'[DeviceLog]','deviceLogAddr=/opt/casa/ftp/files/deviceLog/'
	]
	if not os.path.exists('/etc/casanms/'):
		os.mkdir('/etc/casanms')	
	f = open('/etc/casanms/nms.properties', 'a')
	for config in config_list:
		f.write(config + '\n')
	f.close()


def config_nms_property(mysql_usr, mysql_pwd):
	conf = ConfigParser.ConfigParser()
	conf.read("/etc/casanms/nms.properties")
	conf.set("Mysql", "db.mysql.username",mysql_usr)
	conf.set("Mysql", "db.mysql.password",mysql_pwd)
	print ("mysql database name: {0} password:{1}".format(conf.get("Mysql", "db.mysql.username",mysql_usr),conf.get("Mysql", "db.mysql.password",mysql_pwd)))

def print_install_package():
	print '1.install whole hems package\n'
	print '2.install libsigar\n'
	print '3.install mysql and update mysql database\n'
	print '4.install MongoDB\n'
	print '5.install ntp server\n'
	print '6.install apache tomcat\n'
	print '7.update mysql database\n'
	print '8.update hems software package\n'
	print '9.install ftp server\n'
	print '10.config https environment\n'
	print '11.exit'

def init_dir():
	if not os.path.exists('/opt'):
		os.mkdir('/opt')
	if not os.path.exists('/opt/casa'):
		os.mkdir('/opt/casa')
	

def add_ftp_user():	
	err_list=[]
	ftp_username = raw_input("please input ftp user name: ")
	ftp_data_dir  = '/opt/casa/ftp/'
	ftp_allow_users  = '/etc/allow_users'
	if not os.path.exists(ftp_data_dir):
		if os.mkdir(ftp_data_dir):
			print("create directory " + ftp_data_dir);
		else:
			print("exist"  + ftp_data_dir);
	cmd = 'chmod 777 '+ftp_data_dir
	echo_exe(cmd, err_list)
	cmd = 'useradd -d ' + ftp_data_dir + ' -s /bin/bash ' + ftp_username
	echo_exe(cmd, err_list)
	print 'please input ftp user password:'
	cmd = 'passwd ' + ftp_username
	echo_exe(cmd, err_list)
	cmd = 'touch ' + ftp_allow_users
	echo_exe(cmd, err_list)
	f = open(ftp_allow_users, 'a') 
	f.write(ftp_username +'\n')
	f.close()


if __name__=="__main__":
	check_env()
	init_dir()
	while 1:
		print_install_package()
		task = raw_input("select number of task: ")
		if task == '1':
			mysql_usr = raw_input("please input mysql user name: ")
			mysql_pwd = raw_input("please input mysql user password: ")
			mysql_db_file = raw_input("please input mysql '.sql' type database path: ")
			software_file = raw_input("please input update hems package: ")
			tomcat_port = 8080
			while hems_common.check_tomcat_port('localhost', int(tomcat_port)) == True:
				port = str(tomcat_port)
				tomcat_port = raw_input("tomcat port: " + port +" has been occupied,please input new port: ")
			hems_install.ctl_tomcat(1)			
			if not os.path.exists(mysql_db_file):
				print mysql_db_file + ' is not exist!'
				sys.exit()

			add_ftp_user()
			hems_install.install_libsigar()
			hems_install.install_mysql(mysql_usr, mysql_pwd, mysql_db_file)
			hems_install.install_mongo()
			hems_install.install_ntp()
			hems_install.install_ftp()
			hems_install.install_jdk()
			hems_install.install_tomcat()
			if int(tomcat_port) != 8080:
				hems_install.config_tomcat_port(int(tomcat_port))
			hems_install.ctl_tomcat(0)	
			write_nms_property()
			config_nms_property(mysql_usr, mysql_pwd)
			hems_common.update_software(software_file)
			#break
		elif task == '2':
			hems_install.install_libsigar()
		elif task == '3':
			mysql_usr = raw_input("please input mysql user name: ")
			mysql_pwd = raw_input("please input mysql user password: ")
			mysql_db_file = raw_input("please input mysql '.sql' type database path: ")
			hems_install.install_mysql(mysql_usr, mysql_pwd, mysql_db_file)
		elif task == '4':
			hems_install.install_mongo()
		elif task == '5':
			hems_install.install_ntp()
		elif  task == '6':
			tomcat_port = 8080
			while hems_common.check_tomcat_port('localhost', int(tomcat_port)) == True:
				port = str(tomcat_port)
				tomcat_port = raw_input("tomcat port: " + port +" has been occupied,please input new port: ")
			hems_install.ctl_tomcat(1)	
			hems_install.install_jdk()
			hems_install.install_tomcat()
			if int(tomcat_port) != 8080:
				hems_install.config_tomcat_port(tomcat_port)
			hems_install.ctl_tomcat(0)
		elif  task == '7':
			mysql_usr = raw_input("please input mysql user name: ")
			mysql_pwd = raw_input("please input mysql user password: ")
			mysql_db_file = raw_input("please input update database path: ")		
			hems_common.update_mysql(mysql_usr, mysql_pwd, mysql_db_file)
		elif  task == '8':
			mysql_usr = raw_input("please input mysql user name: ")
			mysql_pwd = raw_input("please input mysql user password: ")
			software_file = raw_input("please input update hems package: ")
			hems_common.update_software(software_file)
			write_nms_property()
			config_nms_property(mysql_usr, mysql_pwd)
		elif  task == '9':
			add_ftp_user()
			hems_install.install_ftp()
		elif  task == '10':
			add_ftp_user()
			hems_install.install_ftp()
		elif  task == '11':
			print 'exit\n'
			sys.exit()
		else:
			print 'please input the task number!\n'


