#!/usr/bin/python
import  sys
import  os
import  time
import  shutil
import  tarfile
import  urllib2
import  ConfigParser
import  hems_common
import  platform
import  xml.dom.minidom
from xml.etree.ElementTree import ElementTree,Element

#function exe shell commond
def echo_exe(str_cmd, err_list):
	print(str_cmd);
	ret = os.system(str_cmd);
	if ret == 0:
		print(str_cmd + ' success');
	else:
		print(str_cmd + ' error');
		err_list.append(str_cmd);



'''
jdk_file = "jdk-7u67-linux-x64.tar.gz";
mysql_file = "mysql-5.6.17-linux-glibc2.5-x86_64.tar.gz";
tomcat_file = "apache-tomcat-7.0.65.tar.gz";
mongodb_file = 'mongodb-linux-x86_64-2.4.9.tgz';
ntp_file = 'ntp-4.2.8p8.tar.gz';
'''


##############################################################################
#download libsigar 
def install_libsigar():
	print("\n\n\nstart process  libsigar ......");
	err_list = []
	if not (os.path.exists('/usr/lib/libsigar-amd64-linux.so') and os.path.exists('/usr/lib/libsigar-x86-linux.so')):
		if os.path.exists('libsigar-amd64-linux.so'):
			print('exist '+'libsigar-amd64-linux.so');
		else:
			url = "https://github.com/jitsi/jitsi-videobridge/raw/06981d96576c2b4bae5d28509d7a9de9f0842e52/lib/native/linux-64/libsigar-amd64-linux.so"
			hems_common.download_file(url, os.path.basename(url))			
		if not os.path.exists('libsigar-amd64-linux.so'):
			print 'download libsigar failed!'
			sys.exit();
		cmd = 'cp libsigar-amd64-linux.so /usr/lib/';
		echo_exe(cmd, err_list);
		if os.path.exists('libsigar-x86-linux.so'):
			print('libsigar is exist!');
		else:
			url = "https://github.com/jitsi/jitsi-videobridge/raw/06981d96576c2b4bae5d28509d7a9de9f0842e52/lib/native/linux/libsigar-x86-linux.so"
			hems_common.download_file(url, os.path.basename(url))
		if not os.path.exists('libsigar-x86-linux.so'):
			print  'download libsigar failed!'
			sys.exit();
		cmd = 'cp libsigar-x86-linux.so /usr/lib/';
		echo_exe(cmd, err_list);
	else:
		print 'libsigar has been installed!'
	print err_list
	print 'complete process libsigar ......\n\n\n'
##############################################################################











##############################################################################
def install_mysql(mysql_usr, mysql_pwd, mysql_db_file):
	err_list = []
	#check platform
	platform_type = platform.linux_distribution()[0]
	if platform_type.lower() == 'Ubuntu'.lower():
		cmd = 'apt-get install libaio1'
	elif platform_type.lower() == 'Centos'.lower():
		cmd = 'yum install libaio'
	else:
		print 'can not support currently!'
		sys.exit()
	echo_exe(cmd, err_list)
	#mysql package para
	mysql_file_name = "mysql-5.6.17-linux-glibc2.5-x86_64.tar.gz";
	mysql_install_path = "/usr/local/"
	mysql_url = "http://dev.mysql.com/get/archives/mysql-5.6/mysql-5.6.17-linux-glibc2.5-x86_64.tar.gz"
	mysql_head_list = []


	#install mysql 
	print '\n\n\nstart mysql install ......'
	mysql_dir = mysql_file_name[0:-7] ;
	mysql_install_dir = '/usr/local/mysql';
	mysql_pack = hems_common.Package(mysql_file_name, mysql_install_path, mysql_url, mysql_head_list)
	mysql_pack.download_package()
	mysql_pack.untar_package()
	os.rename(mysql_install_path+mysql_dir, mysql_install_dir)
	cmd = 'groupadd mysql';
	echo_exe(cmd, err_list);
	cmd = 'useradd -r -g mysql mysql';
	echo_exe(cmd, err_list);
	cur_dir = os.getcwd();
	print(cur_dir);
	cmd = 'cd ' + mysql_install_dir;
	os.chdir(mysql_install_dir);
	cmd = 'chown -R mysql:mysql ./';
	echo_exe(cmd, err_list);
	cmd = './scripts/mysql_install_db --user=mysql';
	echo_exe(cmd, err_list);
	cmd = 'chown -R root:root ./';
	echo_exe(cmd, err_list);
	cmd = 'chown -R mysql:mysql ' + 'data';
	echo_exe(cmd, err_list);
	cmd = 'cp '+ 'support-files/mysql.server /etc/init.d/mysql';
	echo_exe(cmd, err_list);
	cmd = 'cd ' + cur_dir;
	os.chdir(cur_dir);
	cur_dir = os.getcwd();
	print(cur_dir);

	#config mysql
	conf = ConfigParser.ConfigParser()
	conf.read(mysql_install_dir+"/my.cnf")
	conf.set("mysqld", "lower_case_table_names",'1')
	conf.set("mysqld", "datadir",'/usr/local/mysql/data')
	conf.set("mysqld", "event_scheduler",'ON')
	conf.set("mysqld", "default-time-zone",'+0:00')
	conf.write(open("/usr/local/mysql/my.cnf", "w"))
	'''
	[mysqld]
	default-time-zone='+0:00'
	if not os.path.exists(mysql_install_path + 'my.cnf'):
		print('my.cnf is not exist!');
		sys.exit();
	cmd = 'cp my.cnf /etc/';
	echo_exe(cmd, err_list);
	'''
	cmd = '/etc/init.d/mysql restart';
	var = os.system(cmd);
	if var == 0:
		print('restart mysql success!\n\n');
		cmd = mysql_install_dir +'/bin/mysqladmin -u ' + mysql_usr + ' password ' + mysql_pwd;
		echo_exe(cmd, err_list);
	else:
		print('restart mysql failed!\n\n');
		sys.exit();
	cmd = '/usr/local/mysql/bin/mysql -u ' + mysql_usr + ' -p'+ mysql_pwd + ' -e \'create database hemsdb;\'';
	echo_exe(cmd, err_list);
	if not os.path.exists(mysql_db_file):
		print mysql_db_file + ' is not exist!'
		sys.exit();
	cmd = '/usr/local/mysql/bin/mysql -u ' + mysql_usr + ' -p'+ mysql_pwd + ' hemsdb < ' + mysql_db_file;
	echo_exe(cmd, err_list);
	print err_list
	print 'complete mysql install ......\n\n\n'
##############################################################################





##############################################################################
def install_mongo():
	err_list = []
	#mongodb package para
	mongodb_file_name = "mongodb-linux-x86_64-2.4.9.tgz";
	mongodb_install_path = "/usr/local/"
	mongodb_url = "http://downloads.mongodb.org/linux/mongodb-linux-x86_64-2.4.9.tgz"
	mongodb_head_list = []


	#install mongodb 
	print '\n\n\nstart mongodb  install ......'
	mongodb_install_dir = '/usr/local/mongodb'
	mongodb_dir = mongodb_file_name[:-4]
	mongodb_pack = hems_common.Package(mongodb_file_name, mongodb_install_path, mongodb_url, mongodb_head_list)
	mongodb_pack.download_package()
	mongodb_pack.untar_package()
	os.rename(mongodb_install_path+mongodb_dir, mongodb_install_dir)
	cmd = 'pkill mongod'
	echo_exe(cmd, err_list);
	time.sleep(2);
	#create monngodb log directory and file
	mongo_data  = '/opt/casa/mongodb'
	mongo_data_dir  = '/opt/casa/mongodb/data/'
	mongo_log_file  = '/opt/casa/mongodb/logs'
	if not os.path.exists(mongo_data):
		if os.mkdir(mongo_data):
			print("create directory " + mongo_data);
	else:
		print("exist"  + mongo_data);

	if not os.path.exists(mongo_data_dir):
		if os.mkdir(mongo_data_dir):
			print("create directory " + mongo_data_dir)
	else:
		print("exist"  + mongo_data_dir);

	if not os.path.exists(mongo_log_file):
		f = open(mongo_log_file,'a');
		print("create directory " + mongo_log_file)
	print 'complete create mongodb log file\n'
	cmd = mongodb_install_dir +'/bin/mongod --dbpath=' + mongo_data_dir + ' --logpath=' + mongo_log_file + ' --logappend --port=27017 --fork';
	print(cmd);
	var = os.system(cmd);
	if var == 0:
		print('install and start mongodb success!\n\n');
		print('set auto start');
		cmd = 'echo \'/usr/local/mongodb/bin/mongod --dbpath=/opt/casa/mongodb/data/ --logpath=/opt/casa/mongodb/logs --logappend --port=27017 --fork\' >> /etc/rc.local';
		echo_exe(cmd, err_list);
	else:
		print('install mongodb failed!\n\n');
		sys.exit();
	print err_list
	print 'complete mongodb  install ......\n\n\n'
##############################################################################





##############################################################################
def config_ntp():
	config_list = ['server 210.72.145.44 perfer\n','server 202.108.6.95\n','server s2g.time.edu.cn\n','Restrict defalut nomodify\n' ,'Restrict 172.0.0.0 mask 255.255.0.0 nomodify\n']
	i = 0
	f_bak  = open('/etc/ntp.conf.bak', 'r')
	f = open('/etc/ntp.conf', 'a') 
	while 1:
		str_ntp = f_bak.readline()
		if not str_ntp:break
		f.write(str_ntp)
		if str_ntp.find('#') == -1 and not i == 2:
			if str_ntp.find('server') and i == 0:
				f.write(config_list[0])
				f.write(config_list[1])
				f.write(config_list[2])
				i = 1
			elif str_ntp.find('server') and i == 1:
				f.write(config_list[3])
				f.write(config_list[4])
				i = 2	
	f.close()
	f_bak.close()


def install_ntp():
	err_list = []
	#check platform
	platform_type = platform.linux_distribution()[0]
	if platform_type.lower() == 'Ubuntu'.lower():
		cmd = 'apt-get install ntp'
	elif platform_type.lower() == 'Centos'.lower():
		cmd = 'yum -y install ntp'
	else:
		print 'can not support currently!'
		sys.exit()
	echo_exe(cmd, err_list)
	'''
	#ntp package para 
	ntp_file_name = "ntp-4.2.8p8.tar.gz";
	ntp_install_path = "./"
	ntp_url = "https://www.eecis.udel.edu/~ntp/ntp_spool/ntp4/ntp-4.2.8p8.tar.gz"
	ntp_head_list = []

	#install ntp 
	print '\n\n\nstart ntp install ......'
	ntp_dir = ntp_file_name[0:-7];
	ntp_pack = hems_common.Package(ntp_file_name, ntp_install_path, ntp_url, ntp_head_list)
	ntp_pack.download_package()
	ntp_pack.untar_package()
	cur_dir = os.getcwd()
	print(cur_dir)
	os.chdir(ntp_dir)
	cmd = './configure --prefix=/usr/local/ntp --enable-all-clocks --enable-parse-clocks;make && make install'
	echo_exe(cmd, err_list)
	os.chdir(cur_dir)
	'''

	#config ntp server 	
	cmd = 'cp /etc/ntp.conf /etc/ntp.conf.bak;rm /etc/ntp.conf'
	echo_exe(cmd, err_list)
	config_ntp()

	print err_list
	print 'complete ntp install ......\n\n\n'

	
	
	

##############################################################################





##############################################################################
def install_jdk():
	err_list = []
	#jdk package para
	jdk_file_name = "jdk-7u67-linux-x64.tar.gz"
	jdk_install_path = "/opt/casa/"
	jdk_url = "http://download.oracle.com/otn-pub/java/jdk/7u67-b01/jdk-7u67-linux-x64.tar.gz"
	jdk_head_list = ['s_cc=true; oraclelicense=accept-securebackup-cookie; s_nr=1407131063040; gpw_e24=http%3A%2F%2Fwww.oracle.com%2Ftechnetwork%2Fjava%2Fjavase%2Fdownloads%2Fjdk7-downloads-1880260.html; s_sq=%5B%5BB%5D%5D;','12.145.16.17','Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0']

	#install jdk 
	print '\n\n\nstart jdk install ......'
	java_pack = hems_common.Package(jdk_file_name, jdk_install_path, jdk_url, jdk_head_list)
	java_pack.download_package()
	java_pack.untar_package()
	lines =  ["\nexport JAVA_HOME=/opt/casa/jdk1.7.0_67\n","export JRE_HOME=$JAVA_HOME/jre\n","export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH\n","export PATH=.:$JAVA_HOME/bin:$PATH\n"]
	f = open('/etc/profile', 'a')
	f.writelines(lines)
	f.close();
	cmd = 'source /etc/profile';
	echo_exe(cmd, err_list);
	hems_common.set_java_env()
	var = os.system('java -version');
	if var == 0:
		print('java jdk install success!\n\n');
	else:
		print('install jdk install package error!\n');
		sys.exit();
	print err_list
	print 'complete jdk install ......\n\n\n'
	
##############################################################################



##############################################################################
def config_tomcat(tomcat_install_dir):
	i = 0
	f_bak  = open(tomcat_install_dir +'/bin/catalina.sh.bak', 'r')
	f = open(tomcat_install_dir +'/bin/catalina.sh', 'a') 
	while 1:
		str_cnf = f_bak.readline()
		if not str_cnf:break
		f.write(str_cnf)
		if not str_cnf.find('-Djava.io.tmpdir') == -1:
			f.write('    -Djava.awt.headless=true \\\n')

	f.close()
	f_bak.close()


def ctl_tomcat(flag):
	tomcat_file_name = "apache-tomcat-7.0.65.tar.gz"
	tomcat_install_path = "/opt/casa/"
	tomcat_dir = tomcat_file_name[:-7] + '/'
	tomcat_install_dir = tomcat_install_path + tomcat_dir
	tomcat_bin = tomcat_install_dir +'bin/';
	if flag == 0:
		cmd = tomcat_bin + 'startup.sh';
	elif flag == 1:
		cmd = tomcat_bin + 'shutdown.sh';
	else:
		print 'flag error!'
	if os.path.exists(cmd):
		var = os.system(cmd);	
		print(var);
		if var == 0:
			print('execeed ' + cmd + ' success!\n\n')
			time.sleep(3);
		else:
			print('start tomcat error!');
			sys.exit();
	else:
		print(cmd + ' is not exsit!')

def read_xml(in_path):
    tree = ElementTree()  
    tree.parse(in_path)  
    return tree

def write_xml(tree, out_path):
    tree.write(out_path, encoding="utf-8",xml_declaration=True)

def if_match(node, kv_map):
    for key in kv_map:  
        if node.get(key) != kv_map.get(key):  
            return False  
    return True

def find_nodes(tree, path): 
    return tree.findall(path) 

def get_node_by_keyvalue(nodelist, kv_map):
    result_nodes = []  
    for node in nodelist:  
        if if_match(node, kv_map):  
            result_nodes.append(node)  
    return result_nodes

def change_node_properties(nodelist, kv_map, is_delete=False): 
    for node in nodelist:  
        for key in kv_map:  
            if is_delete:   
                if key in node.attrib:  
                    del node.attrib[key]  
            else:  
                node.set(key, kv_map.get(key)) 


def config_tomcat_port(tomcat_port):
	tomcat_file_name = "apache-tomcat-7.0.65.tar.gz"
	tomcat_install_path = "/opt/casa/"
	tomcat_dir = tomcat_file_name[:-7] + '/'
	tomcat_install_dir = tomcat_install_path + tomcat_dir
	tomcat_conf_file= tomcat_install_dir +'conf/server.xml'
	cmd = "cp " + tomcat_conf_file +" " +tomcat_conf_file +".bak"
	var = os.system(cmd);	
	print(var);
	tree = read_xml(tomcat_conf_file)
	nodes = find_nodes(tree, "Service/Connector")
	result_nodes = get_node_by_keyvalue(nodes,{"port": "8080"})
	change_node_properties(result_nodes, {"port": tomcat_port}) 
	write_xml(tree, tomcat_conf_file)


def install_tomcat():
	err_list = []
	#tomcat package para
	tomcat_file_name = "apache-tomcat-7.0.65.tar.gz"
	tomcat_install_path = "/opt/casa/"
	tomcat_url = "http://archive.apache.org/dist/tomcat/tomcat-7/v7.0.65/bin/apache-tomcat-7.0.65.tar.gz"
	tomcat_head_list = []


	#install tomcat
	print '\n\n\nstart tomcat install ......'
	tomcat_dir = tomcat_file_name[:-7] + '/'
	tomcat_install_dir = tomcat_install_path + tomcat_dir 
	tomcat_pack = hems_common.Package(tomcat_file_name, tomcat_install_path, tomcat_url, tomcat_head_list)
	tomcat_pack.download_package()
	tomcat_pack.untar_package()
	#os.rename(tomcat_install_path + tomcat_dir, tomcat_install_dir)
	


	#config tomcat 
	cmd = 'cp ' + tomcat_install_dir +'bin/catalina.sh ' +  tomcat_install_dir + 'bin/catalina.sh.bak;rm ' + tomcat_install_dir +'bin/catalina.sh'
	echo_exe(cmd, err_list)
	config_tomcat(tomcat_install_dir)
	cmd = 'chmod +x ' + tomcat_install_dir +'bin/catalina.sh'
	echo_exe(cmd, err_list)	
	print err_list
	print 'complete tomcat install ......\n\n\n'
##############################################################################



##############################################################################
def config_ftp():
	err_list = []
	flag = 0	
	cmd = 'cp /etc/vsftpd.conf /etc/vsftpd.conf.bak;rm /etc/vsftpd.conf'
	echo_exe(cmd, err_list)	
	f_bak  = open('/etc/vsftpd.conf.bak', 'r')
	f = open('/etc/vsftpd.conf', 'a') 
	while 1:
		str_cnf = f_bak.readline()
		if not str_cnf:break
		if not str_cnf.find('#local_enable=YES') == -1:
			f.write('local_enable=YES\n')
		elif not str_cnf.find('#write_enable=YES') == -1:
			f.write('write_enabel=YES\n')
		elif not str_cnf.find('userlist_deny=NO\n') == -1:
			flag = 1
		else:
			f.write(str_cnf)
	if flag == 1:
		f.write('userlist_deny=NO\n')
		f.write('userlist_enable=YES\n')
		f.write('userlist_file=/etc/allowed_users\n')
		f.write('seccomp_sandbox=NO\n')
	f.close()
	f_bak.close()
	cmd = 'service vsftpd restart'
	echo_exe(cmd, err_list)

def install_alarm_mp3():
	err_list = []
	install_dir = '/opt/casa/'
	ftp_dir = '/opt/casa/ftp/'
	ftp_file_dir = '/opt/casa/ftp/files/'
	ftp_file_alarm_dir = '/opt/casa/ftp/files/alarm/'
	alram_mp3_dir = '/opt/casa/ftp/files/alarm/mp3/'
	if not os.path.exists(install_dir):
		os.mkdir(install_dir)
	if not os.path.exists(ftp_dir):
		os.mkdir(ftp_dir)
	if not os.path.exists(ftp_file_dir):
		os.mkdir(ftp_file_dir)
	if not os.path.exists(ftp_file_alarm_dir):
		os.mkdir(ftp_file_alarm_dir)
	if not os.path.exists(alram_mp3_dir):
		os.mkdir(alram_mp3_dir)
	cmd = 'cp ./mp3/* /opt/casa/ftp/files/alarm/mp3/ -r'
	echo_exe(cmd, err_list)
	print err_list

def install_ftp():
	err_list = []
	ftp_vsftpd_conf  = '/etc/vsftpd.conf'
	'''
	#tomcat package para
	ftp_file_name = "apache-tomcat-7.0.65.tar.gz"
	ftp_install_path = "/opt/casa/"
	ftp_url = "http://archive.apache.org/dist/tomcat/tomcat-7/v7.0.65/bin/apache-tomcat-7.0.65.tar.gz"
	ftp_head_list = []
	'''
	platform_type = platform.linux_distribution()[0]
	if platform_type.lower() == 'Ubuntu'.lower():
		cmd = 'apt-get install vsftpd'
		echo_exe(cmd, err_list)
	elif platform_type.lower() == 'Centos'.lower():
		cmd = 'yum -y install vsftpd'
		echo_exe(cmd, err_list)
	else:
		print 'can not support currently!'
		sys.exit()
	config_ftp()
	install_alarm_mp3()
	print err_list
##############################################################################




	









