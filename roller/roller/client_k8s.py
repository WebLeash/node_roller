import os
import json
from termios import VT1
from kubernetes import client, config
from kubernetes.client import ApiException
from kubernetes.client.rest import ApiException
import subprocess
import boto3

config.load_kube_config()




class K8SClient:  # pragma: no cover


    def get_hostname(
        node_name,
        ):

        worker_nodes = []
        v1 = client.CoreV1Api()
        ret = v1.list_node(label_selector='node-role.kubernetes.io/worker =true')
        for items in ret.items:           
            worker_nodes.append(items.metadata.name)
            if node_name == items.metadata.name:
                hn=items.spec.provider_id[-19:]
                return hn


    def get_template(
        node

        ):
        nodes_host = []
        v1 = client.CoreV1Api()
        ret = v1.list_node(label_selector='node-role.kubernetes.io/worker =true')
        for items in ret.items:           
            worker_node = items.metadata.name
            if node == worker_node:
                labels=items.metadata.labels
                template = K8SClient.get_hostname_from_labels(labels)
                return template

    def get_hostname_from_labels(
        labels
    ):
        for i,v in labels.items():
            if i == "kubernetes.io/hostname":
                hostname=v[-19:]
                asg_template=v[0:-20] # strip of the n chars that make up the ami_id plus "-" which = 20 chars. This then allows for variable length description in tag.
                return asg_template

    def desired_state_num_node(
        node_name
        ):
        DEFAULT=1
        desired_state=DEFAULT # When we get the template track down the desired state
        client = boto3.client('autoscaling',region_name='eu-west-2')

        template = K8SClient.get_template(node_name)

        response = client.describe_auto_scaling_groups()

        all_asg = response['AutoScalingGroups']
        for i in range(len(all_asg)):
            asg_templates = all_asg[i]['AutoScalingGroupName']
            asg_desired_c = all_asg[i]['DesiredCapacity']

            if template == asg_templates:
                desired_state = asg_desired_c

        return desired_state


    def number_of_node():
        (node_list_worker,num) = K8SClient.get_node_list_worker()
        counter = 0
        for line in node_list_worker:
            counter += 1
        return counter



    def get_node_list_worker():
        worker_nodes = []
        v1 = client.CoreV1Api()
        ret = v1.list_node(label_selector='node-role.kubernetes.io/worker =true')
        counter = 0
        for items in ret.items:  
            counter = counter + 1         
            worker_nodes.append(items.metadata.name)
        
        return (worker_nodes,counter)

    def get_node_list():
        nodes = []
        v1 = client.CoreV1Api()
        ret = v1.list_node(label_selector='node-role.kubernetes.io/worker =true')
        count = 0
        for items in ret.items:           
            nodes.append(items.metadata.name)
            count = count + 1
        
        return (nodes,count)
    

    def cordon_node_old(
       node_name,
       ):
      node = str(node_name)
      node = node.rstrip()
      cmd_get_cordon = ['kubectl','cordon', node ]
      out = subprocess.check_output(cmd_get_cordon)
      return out


    def cordon_node(
        node_name,
        ):

        body = {
            "spec": {
            "unschedulable": True
                  }
               }
        v1 = client.CoreV1Api()
        v1.patch_node(node_name,body)
        return



    def drain_node(
        node_name,
        ):
        v1 = client.CoreV1Api()
        field_selector = 'spec.nodeName='+node_name
        ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)

        for i in ret.items:
           print("DRAIN: (%s) pod in namespace (%s) for node (%s)" % (i.metadata.namespace,i.metadata.name,node_name))
           K8SClient.delete_pods(i.metadata.namespace,i.metadata.name) 




    def delete_pods(
        namespace,
        pod_name,
        ):
        v1 = client.CoreV1Api()
        body = client.V1DeleteOptions()
        v1.delete_namespaced_pod(pod_name, namespace, body=body) 

    def get_node_status(
        node_name,
        ):
        node = str(node_name)
        node = node.rstrip()
        cmd = "kubectl describe node %s |grep KubeletReady | head -1" % node
        gp = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = gp.communicate()[0]
        output=output.decode('UTF-8')
        output=output[2:]
        output=output.rstrip()
        status = output[0:5]
        return status


    def get_all_status():
       node_list_worker = K8SClient.get_node_list_worker()
       not_ready = False
       status = "pending"


       for line in node_list_worker:
           node = line

           status = K8SClient.get_node_status(node)     
           if status == "Ready":
              print ("Node {} is {}".format(line,status))
           if status == "":
              not_ready = True
              print ("set not ready to TRUE (%s)" % str(not_ready))
              print ("Node {} is Not ready {}".format(line,status))

       if not_ready == True:
           status = "pending"

       
       return status 

            
    def terminate_ec2(
        id,
        ):
        ec2_id = id
        cmd = "aws ec2 terminate-instances --instance-ids %s"  % ec2_id
        out = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return out

    def ami_id(
        node
        ):
        cmd = "aws ec2 describe-instances --instance-ids %s |grep  ImageId |head -1 |cut -d'\"' -f4"  % node
        #out = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out = subprocess.check_output(cmd,shell=True,universal_newlines=True)
        return str(out)







          





        





    