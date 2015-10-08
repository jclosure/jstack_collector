#!/usr/bin/env python
# coding: utf-8

import sys
import subprocess
import re
import smtplib
import csv
import socket
import StringIO

# mail related
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
    
############ USAGE #################
#
# just set automatic=True and load
#
####################################

class JstackInterrogator:

    def __init__(self):
        self.output_file = 'output.csv'
        # self._to = ['admin@yourdomain.com','support@yourdomain.com']
        self._to = ['jclosure@yourdomain.com']
        self._from = 'jstack-interrogator@yourdomain.com'
        
    ### DRIVER ###

    def go(self):
        #ipdb.set_trace()
        start = self.get_eof_count()
        fuse_pid = self.get_fuse_pid()
        self.run_jstack(fuse_pid)
        lines = self.get_new_lines(start)
        if len(lines) > 0:
            buckets = self.bucketize(lines)
            flattened = self.flattenize(buckets)
            self.write_csv(flattened, self.output_file)
            hostname = socket.gethostname()
            self.send_mail(self._from, self._to, "thread interrogator report: " + hostname, "jstack data", [self.output_file])
        else:
            print "no lines"

    ### PROG FUNCTIONS ###        

    def get_eof_count(self):
        cmd = 'cat /opt/jboss-fuse/data/log/wrapper.log | wc -l'
        start = self.run_cmd(cmd)[0]
        return int(start)

    def get_fuse_pid(self):
        # note the [] to exclude the grep itself
        cmd = "ps -ef | grep '[j]ava -Dkaraf.home=/opt/jboss' | awk '{ print $2 }'"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        result = [i for i in self.run_proc(p) if i != str(p.pid)]
        if not len(result) > 0:
            print 'could not get fuse pid'
            raise   
        fuse_pid = result[0]
        print "pid: " + fuse_pid
        return fuse_pid

    def run_jstack(self, pid):
        self.run_cmd("jstack " + pid)

    def get_new_lines(self, start):
        end = self.get_eof_count()
        delta = end - start
        lines = self.run_cmd("tail -n " + str(delta) + " /opt/jboss-fuse/data/log/wrapper.log")
        return lines[2:]


    ### PARSING ###

    def bucketize(self, lines):
        return_dict = {}
        key = 0
        for line in lines:
            tup = line.split('|')
            tup = map(lambda l : l.strip(), tup)
            if tup[3] == "":
                key = key + 1
            if not key in return_dict:
                    return_dict[key] = []
            if not tup[3] =="":
                return_dict[key].append(tup)
        return return_dict
                        
    def flattenize(self, buckets):
        flattened = []
        regex = re.compile('"(.+ )"')
        for key, bucket  in buckets.items():
            if len(bucket) > 0:
                f = lambda v : v[3].strip()
                values = map(f, bucket)
                flat = "\n".join(values)
                try:
                    result = bucket[:1][0]
                    result.append(flat)
                    r = re.search(r'"(.+)"', result[3])
                    if not r is None:
                        g = r.groups()
                        if not g is None:
                            result[3] = g[0]
                            flattened.append(result)
                except Exception, e:
                    print "error: "
                    raise
        return flattened

    
    #### PROCESS EXECUTION ####
    
    def run_cmd(self, cmd):    
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = self.run_proc(p)
        return lines

    def run_proc(self, p):    
        lines = []
        try:
            # for line in p.stdout.readlines():
            #     lines.append(line.rstrip("\r\n"))
            #     #print line,
            # retval = p.wait()
            stdout, stderr = p.communicate()
            buf = StringIO.StringIO(stdout)
            for line in buf.readlines():
                lines.append(line.strip())
        except p.CalledProcessError as ex:
            print "error code:", ex.returncode, ex.output
        return lines


    ### HELPERS ###

    def filterbyvalue(self, seq, value):
        for el in seq:
            if el.attribute==value: yield el

    def write_csv(self, flattened, file_name):
        with open(file_name, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(flattened)

    def send_mail(self, send_from, send_to, subject, text, files=[], server="txsmtp.amd.com", port=25, username='', password='', isTls=False):
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = subject

        msg.attach( MIMEText(text) )

        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
            msg.attach(part)

        smtp = smtplib.SMTP(server, port)
        #if isTls: smtp.starttls()
        #smtp.login(username,password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()

### GLOBAL ###
import inspect

def defined(var):
    try:
        eval(var)
        #ipdb.set_trace()
        result = True
    except Exception:
        result = False
    return result


####################
## SELF EXECUTING ##
####################

# catch from bash script
# print 'env var automatic is: ' + str(os.getenv('automatic'))

# SETUP AUTOMATIC RUNNING
if not defined('automatic'):
    automatic = False

if 'automatic' in sys.argv:
    automatic = True

# AUTO EXEC?
if not automatic is None and automatic:
    print 'automatically executing'
    jsi = JstackInterrogator()
    jsi.go()
else:
    pass

# NEED TO EXIT?
try:
    sys.exit()
except:
    pass

