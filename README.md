# insaas-ami-build

## The gitlab pipeline will 

* Set default region to AWS eu-west-2. London
* Pull in the pre-configured runner
* call the launcher script. (Runs poetry and creats a virt env with deps).
* Launcher script initialises the AWS environment config. (AWS KEYS from secret storage. Not Vault)
* Launcher script fires up poetry for python and calls main.

## Python "roller"

* Rotational "worker" node processing.
* Leverages the python k8's client.
* Cordons worker node.
* Drains worker node.
* Terminates node instance in AWS via BOTO3.(SDK)
* Awaits for graceful termination of AWS node.
* Then processes next worker node.



## The process works well for the Development environments.
# Some consideration needs to be made around optimising the secret store. Vault service account would be good.


