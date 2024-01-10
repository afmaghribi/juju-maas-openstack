## Create others virtual machines

This script will provisioning several virtual machines that enable PXE boot based on yaml file by default will looking for `machines.yaml` file. 

The `manage_machine.py` has several options as can see below

```
./manage_machines.py -h
usage: manage_machines.py [-h] (-c | -d) [-f FILE]

Generate virtual machines using libvirt

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          Create virtual machines based on file provided
  -d, --delete          Delete virtual machines based on file provided
  -f FILE, --file FILE  Specify machines yaml file. Default is "machines.yaml"
```

Well, basically just `create` and `delete` virtual machines based on `machines.yaml`.

Create the virtual machines. Take note the output because we will use it for commisioning.

```
 ./manage_machines.py -c
Created virtual machines details
Name:	juju-controller
UUID:	1680256e-f552-4963-bc6c-01811b0bbe3a
Mac1:	52:54:00:16:ec:8f

Created virtual machines details
Name:	openstack-controller
UUID:	0570e540-6427-4aa9-9a90-0457bd2d3357
Mac1:	52:54:00:84:ac:08

Created virtual machines details
Name:	compute01
UUID:	95b2743b-a0af-4509-ace4-a8ec87476f05
Mac1:	52:54:00:be:1c:93

Created virtual machines details
Name:	compute02
UUID:	b1f3889e-fe36-404c-a200-73dc6e183aed
Mac1:	52:54:00:95:64:8f

Created virtual machines details
Name:	compute03
UUID:	4ef9d2a3-874d-4ecd-8c47-d7a6642cf20d
Mac1:	52:54:00:b5:f8:f1
```

Next step to commisioning all machines

[Next Step](commissioning-machines.md)