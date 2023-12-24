## Create libvirt network

The script will create libvirt network based on yaml file by default will looking for `networks.yaml` file. The structure of yaml file that used by script can be see in `networks.yaml`.

The `manage_network.py` has several options as can see below

```
usage: manage_network.py [-h] (-c | -d | -r) [-f FILE]

Generate virtual network using libvirt

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          Create network based on file provided
  -d, --delete          Delete network based on file provided
  -r, --recreate        Recreate network based on file provided
  -f FILE, --file FILE  Specify network yaml file. Default is "networks.yaml"
```

Well, basically just `create` and `delete` the network. The `recreate` is needed on later steps. You can create network with provided `networks.yaml` or make some modification. But, note that the `external endpoint` should `not` provide `dhcp` because we will use `dhcp from maas` for `PXE boot`.

```
./manage_network.py -c
Created virtual network details
Name:	sekai-net
UUID:	c6ec0dae-a5f6-44c0-af46-3cfc8af2b16b
bridge:	sekai-br

Created virtual network details
Name:	isekai-net
UUID:	4425f326-7c89-44cf-9f0c-8bea88cb3aca
bridge:	isekai-br
```

[Next Step](../maas/)