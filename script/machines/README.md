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
UUID:	642e49f9-0d42-42ae-a70e-e05c5df3dd74
Mac1:	52:54:00:f2:5a:76

Created virtual machines details
Name:	openstack-controller
UUID:	9a2c7699-192a-4c9f-bc11-bcbce969c5fa
Mac1:	52:54:00:dc:03:19

Created virtual machines details
Name:	compute01
UUID:	804f4607-ee7a-417b-88eb-e78e70440430
Mac1:	52:54:00:99:72:85

Created virtual machines details
Name:	compute02
UUID:	10b4d145-4f4e-4b13-89e7-89d0d854431f
Mac1:	52:54:00:79:21:51

Created virtual machines details
Name:	compute03
UUID:	020fb276-fdb9-4f63-aae6-780bbcbd073f
Mac1:	52:54:00:fb:53:71
```

Next step to commisioning all machines

[Next Step](commissioning-machines.md)