#!/usr/bin/python
import hems_common
import hems_install
import  ConfigParser

conf = ConfigParser.ConfigParser()
conf.read("/usr/local/mysql//my.cnf")
conf.set("mysqld", "lower_case_table_names",'1')
conf.set("mysqld", "datadir",'/usr/local/mysql/data')
conf.set("mysqld", "event_scheduler",'ON')
conf.set("mysqld", "default-time-zone",'+0:00')
conf.write(open("/usr/local/mysql/my.cnf", "w"))
print "end"
