#!/bin/python

from operator import index
from pickle import FALSE
from platform import node
from process_node import Node
from client_k8s import K8SClient
import sys
import array
from datetime import datetime


import time
def output(
    text,
    err_level,
        ):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if  err_level == 1:
            str = "\t[INFO - %s] %s\n" % (dt_string,text)
        if err_level == 2:
            str = "\t[REPORT] *%s\n*" % text
        
        print(str)

old_ami_ids=[]
new_am_ids=[]
def main():
    
    (node_list_worker,c) =  K8SClient.get_node_list_worker()
    counter = 0

    for item in node_list_worker:
            node=item

            status = K8SClient.get_node_status(node)
 
            node_count = K8SClient.desired_state_num_node(node) # This is optimised by AWS so does chane depending on pods I recon
        
                # Node ....... Rotational 
            output("****node to process[%s]*****" % node,1)
            output("node_count=(%s) Desired State=(%s)" % (node_count,K8SClient.desired_state_num_node(node)),1)
            output("hostname of [%s] =  (%s)" % (node,K8SClient.get_hostname(node)),1)

            desired_state = K8SClient.desired_state_num_node(node)
            output("desired state = (%s)" % K8SClient.desired_state_num_node(node),1)

            output("Cordoning [%s]" % node,1)
          
            K8SClient.cordon_node(node)

            output("Drain %s" % node,1)

            K8SClient.drain_node(node),

        
            output("Terminating instanceID=%s in AWS" % K8SClient.get_hostname(node),1)

            old_ami_ids.append(K8SClient.ami_id(K8SClient.get_hostname(node)))

        
           # Using functions as return value parameters. 
            output("%s" % K8SClient.terminate_ec2(K8SClient.get_hostname(node)),1)

            output("Awaiting for graceful termination [%s]..." % K8SClient.get_hostname(node),1)

           # Check here to see if node is ready, if so then it hasn't been dropped.
            status_of_node_after_termination = K8SClient.get_node_status(node)

            while status_of_node_after_termination == "Ready": # node still on-line
                    output("node %s still showing as ready by k8s" % node,1)
                    time.sleep(180) # 3 mins. LET K8s settle, its very fussy. The Desired State can change any split second
                    status_of_node_after_termination = K8SClient.get_node_status(node)

            output("Number of workers=[%s]" % K8SClient.number_of_node(),1)

            output("node dropped off! [%s]" % node,1) 
            output ("Number of nodes = [%s] Desired State = [%s]" % (K8SClient.number_of_node(),K8SClient.desired_state_num_node(node)),1)


            while K8SClient.number_of_node() < K8SClient.desired_state_num_node(node):
            # less worker nodes than started with, we have lost a node(s)
                    output("Awaiting for all nodes to come online",1)
                    output("Number of nodes = [%s]\n Desired State = [%s]\n" % (K8SClient.number_of_node(),K8SClient.desired_state_num_node(node)),1) 

                    time.sleep(180) # 3 minutes to settle down and let K8s evaluate it's state

            if K8SClient.number_of_node() >= K8SClient.desired_state_num_node(node):
                      output("All nodes back, checking status!!",1)
                      output("Number of nodes = [%s]\n Desired State = [%s]\n" % (K8SClient.number_of_node(),K8SClient.desired_state_num_node(node)),1) 
                      all_status = K8SClient.get_all_status()

            while all_status == "pending":

                if all_status == "Ready":
                        output("All nodes are good!",1)
                        break

                all_status = K8SClient.get_all_status()        

    output("Number of nodes = [%s]\n Desired State = [%s]\n" % (K8SClient.number_of_node(),K8SClient.desired_state_num_node(node)),1)
    output("Finished!",1)

        
def report():

        (node_list_worker,count) =  K8SClient.get_node_list_worker()

        for item in node_list_worker:
            hn = K8SClient.get_hostname(item)
            
            new_am_ids.append(K8SClient.ami_id(hn))

        for images in new_am_ids:
            output("New Image loaded on node [%s] %s" % (item,images),1)

        for old_images in old_ami_ids:
            output("Old image id on node [%s] %s" % (item,old_images),1)
        
        quit()







if __name__ == '__main__':  # pragma: no cover
    main()
    report()
