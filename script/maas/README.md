## Create virtual machine for maas

This script will generate `main.tf` file based on yaml file by default will looking for `maas.yaml` file. 

The `gen_tf.py` has several options as can see below

```
usage: gen_tf.py [-h] [-o OUTPUT] [-f FILE]

Generate terraform module for maas

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Specify output file directory. Default is "output"
  -f FILE, --file FILE  Specify maas yaml file. Default is "maas.yaml"
```

Well, basically this script just generate `main.tf` file from provided `maas.yaml` configuration.
After that go to directory output, then `terraform init` and `terraform apply -auto-approve` to create vm.

Check if vm running using `virsh list` then, try access to `maas` vm using ssh.

```
 virsh list

 Id   Name   State
----------------------
 1    maas   running
```

Access using ssh

```
ssh ubuntu@137.100.100.101 

The authenticity of host '137.100.100.101 (137.100.100.101)' can't be established.
ECDSA key fingerprint is SHA256:G6y7E2TSZRWqpyrmuFl3qR2SYuVwVpn2btI9hOfw8QA.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '137.100.100.101' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-167-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Wed Jan 10 13:36:14 UTC 2024

  System load:  0.06              Processes:             124
  Usage of /:   3.1% of 48.27GB   Users logged in:       0
  Memory usage: 5%                IPv4 address for ens3: 137.100.100.101
  Swap usage:   0%


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Wed Jan 10 13:32:58 2024
ubuntu@maas:~$ 
```

Next step is setup the maas machine

[Next Step](setup-maas.md)