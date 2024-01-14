# Commisioning machine in maas

## Adding machines to maas

Open maas dashboard, go to tab machines. Add hardware > Machine

<details>

![](../../img/maas16.png)
</details>


First, we will add `juju-controller` machine. Fill `MAC address` and `Virsh VM ID` from the output of previous step. The rest just follow the screenshot below. Then choose `Save machine`

<details>

![](../../img/maas17.png)
</details>

Waiting commisioning process (+- 10 mins)

<details>

![](../../img/maas18.png)
</details>

Make sure, now the machine is `ready`

<details>

![](../../img/maas19.png)
</details>

Repeat the steps for the remaining machines and make user machine is now `ready`

<details>

![](../../img/maas20.png)
</details>

## Config commissioned machine

Click the machine, start from `juju-controller`. Go to tab `Network`, Action choose `Edit physical`.

<details>

![](../../img/maas21.png)
</details>

Change ip mode to `Static assign`, then give the ip based on specs.

<details>

![](../../img/maas22.png)
</details>

Next, go to `configuration` tab. Edit the tags, create tag `juju-controller`.

<details>

![](../../img/maas23.png)
</details>

Save

<details>

![](../../img/maas24.png)
</details>

Do same steps for `openstack-controller` machine.

<details>

![](../../img/maas25.png)
</details>

For all compute machine, need to add vlan `1337` to `fabric-0` interface.

<details><summary>compute01</summary>

![](../../img/maas26.png)
</details>

<details><summary>compute02</summary>

![](../../img/maas27.png)
</details>

<details><summary>compute03</summary>

![](../../img/maas28.png)
</details>

Now, all machine is ready and confogured.

<details>

![](../../img/maas29.png)
</details>

Next, setup juju controller

[Next Step](setup-juju-controller.md)