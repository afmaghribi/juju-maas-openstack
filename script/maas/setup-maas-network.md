# Setup Network MAAS

## Create space

Create 2 space "external" and "internal".


Add `space` menu
<details>

![](../../img/maas5.png)
</details>


Add `external` space
<details>

![](../../img/maas6.png)
</details>


Add `internal` space
<details>

![](../../img/maas7.png)
</details>

To see result choose group by space

<details>

![](../../img/maas8.png)
</details>

## Create vlan

Create vlan id 1337, using `fabric-0` and `internal` space

<details>

![](../../img/maas9.png)
</details>

## Create subnet

Create subnet for vlan we created before

<details>

![](../../img/maas10.png)
</details>

## Config DHCP

Need to active DHCP server for PXE boot from fabric-0

Click `untagged` vlan. Then, on vlan summary `edit` change space to `external`

<details>

![](../../img/maas11.png)
</details>

Click configure DHCP

<details>

![](../../img/maas12.png)
</details>

Back to subnets tab. On DHCP column maas still detect DHCP from `External` but it should be `MAAS-provided`

<details>

![](../../img/maas13.png)
</details>

At this point, need to recreate network using `manage_network.py` script. Then, `virsh destroy maas` and `virsh start maas` to fix it

Now, fixed

<details>

![](../../img/maas14.png)
</details>


Add dns to subnet untagged vlan

<details>

![](../../img/maas15.png)
</details>


Next step to provision machine and commision

[Next Step](../machines/)