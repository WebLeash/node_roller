#!/bin/bash/python

from pdb import line_prefix
import subprocess
from sys import stdout



class Node:
   def get_node_list_worker():
      cmd_get_nodes = ['kubectl','get','nodes','-l','node-role.kubernetes.io/worker=true','-o=name']
      nodes = subprocess.Popen(cmd_get_nodes, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      return nodes.stdout

   def cordon_node(
       node_name,
       ):
      node = str(node_name)
      node = node.rstrip()
      cmd_get_cordon = ['kubectl','cordon', node ]
      out = subprocess.check_output(cmd_get_cordon)
      return out
      
   def drain_node(
         node_name,
         ):
      node = str(node_name)
      node = node.rstrip()
      cmd_get_drain = ['kubectl','drain', node,'--ignore-daemonsets', '--force', '--dry-run', '--delete-local-data', '--timeout=30s' ]
      out = subprocess.check_output(cmd_get_drain)
      return out

   def get_hostname(
        node_name,
        ):
        node = str(node_name)
        node = node.rstrip()
        cmd = "kubectl describe node %s |grep Hostname" % node
        gp = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = gp.communicate()[0]
        output=output.decode('UTF-8')
        output=output[34:]
        output=output.rstrip()
        return output

   def terminate_ec2(
        id,
        ):

        ec2_id = str(id)
        ec2_id= ec2_id.rstrip()

        print("terminating id [%s]" % ec2_id)
        cmd = "aws ec2 terminate-instances --instance-ids %s"  % ec2_id
        out = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return out

   def number_of_node():
       node_list_worker = Node.get_node_list_worker()
       counter = 0
       for line in node_list_worker:
           line = line.decode('UTF-8')
           counter += 1
       return counter

   def get_node_status(
        node_name,
        ):
        node = str(node_name)
        node = node.rstrip()
        cmd = "kubectl describe node %s |grep KubeletReady | head -1" % node
        gp = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = gp.communicate()[0]
        output=output.decode('UTF-8')
        print ("DEBUG 1 output from grep [%s]" % output)
        output=output[2:]
        output=output.rstrip()
        status = output[0:5]
        return status

   def get_all_status():
       node_list_worker = Node.get_node_list_worker()
       not_ready = False
       status = "pending"


       for line in node_list_worker:
           line = line.decode('UTF-8')
           line = line[5:]
           node = line.rstrip()
           print ("Checking status of node [%s]"% node)
           status = Node.get_node_status(node)     
           if status == "Ready":
              print ("Node {} is {}".format(line,status))
           if status == "":
              not_ready = True
              print ("set not ready to TRUE (%s)" % str(not_ready))
              print ("Node {} is Not ready {}".format(line,status))

       if not_ready == True:
           status = "pending"

       print ("status=", status)
       
       return status 



# [root@controller ~]# kubectl label nodes worker-2.example.com color=blue
# node/worker-2.example.com labeled





