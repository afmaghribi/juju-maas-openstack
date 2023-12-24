#!/usr/bin/python3
import sys
import argparse
import libvirt
import xml.etree.ElementTree as ET
import yaml
from uuid import uuid4 as gen_uuid

# Connect to local qemu
try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError as e:
    print(repr(e),file=sys.stderr)
    exit(1)

def menu():
    parser = argparse.ArgumentParser(description='Generate virtual network using libvirt')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("-c", "--create", help='Create network based on file provided',action="store_true")
    action.add_argument("-d", "--delete", help='Delete network based on file provided',action="store_true")
    action.add_argument("-r", "--recreate", help='Recreate network based on file provided',action="store_true")

    parser.add_argument("-f", "--file", help='Specify network yaml file. Default is "networks.yaml"', default="networks.yaml")
    
    return parser.parse_args()

def generate_network_xml(net_name,config):
    # Network root section
    network = ET.Element("network")

    # Name section
    ET.SubElement(network, "name").text = net_name
    
    # Uuid section
    ET.SubElement(network, "uuid").text = str(gen_uuid())
    
    # Forward section
    network_forward = ET.SubElement(network, "forward", mode="nat") # forward mode
    forward_nat = ET.SubElement(network_forward, "nat") # nat
    ET.SubElement(forward_nat, "port", start="1024", end="65535") # nat port

    # Bridge section
    ET.SubElement(network, "bridge", name=config["bridge"], stp="on", delay="0")

    # Mac address section
    ET.SubElement(network, "mac", address=config["mac_addr"])

    # IP address section
    network_ip = ET.SubElement(network, "ip", address=config["ip_addr"], netmask=config["netmask"])

    # DHCP section
    if "dhcp" in config.keys():
        ranges = config["dhcp"].split(",")
        network_dhcp = ET.SubElement(network_ip, "dhcp")
        ET.SubElement(network_dhcp, "range", start=ranges[0], end=ranges[1]) # DHCP pool range
        
    return ET.tostring(network).decode()

def create_network(net_name,config):
    # List all virtual network
    networks = conn.listNetworks()

    # Check if virtual network already exist
    if net_name in networks:
        network = conn.networkLookupByName(net_name)
        print_result(network)
        return

    # Generate network xml
    net_xml = generate_network_xml(net_name,config)
    
    # Create virtual network from xml
    try:
        network = conn.networkDefineXML(net_xml)
    except libvirt.libvirtError as e:
        print(repr(e),file=sys.stderr)
        exit(1)

    # Create virtual network
    network.create()

    # Set autostart
    network.setAutostart(1)
    
    # Show network info if not recreate network
    if not args.recreate:
        print_result(network)

def delete_network(net_name):
    # Find virtual network by name
    try:
        network = conn.networkLookupByName(net_name)
    except libvirt.libvirtError as e:
        print(repr(e),file=sys.stderr)
        exit(1)
    
    # Show network info if not recreate network
    if not args.recreate:
        print_result(network)
    
    # Deactive virtual network
    network.destroy()
    
    # Remove virtual network
    network.undefine()

def print_result(virt_net):

    if args.create:
        print("Created virtual network details")
    elif args.delete:
        print("Below virtual network will be removed")

    print("Name:\t" + virt_net.name())
    print("UUID:\t" + virt_net.UUIDString())
    print("bridge:\t" + virt_net.bridgeName())
    print()

if __name__ == "__main__": 
    global args
    args = menu()

    network_config = yaml.safe_load(open(args.file,"r"))
    for net_name in network_config['networks']:
        if args.create:
            create_network(net_name,network_config['networks'][net_name])
        elif args.delete:
            delete_network(net_name)
        elif args.recreate:
            delete_network(net_name)
            create_network(net_name,network_config['networks'][net_name])
            print("Network",net_name,"already recreated")

    # Close libvirt connection
    conn.close()