#!/usr/bin/python3
import sys, os
import argparse
import libvirt
import xml.etree.ElementTree as ET
import yaml
from jinja2 import Environment,FileSystemLoader
from crypt import crypt,mksalt,METHOD_SHA512

# Connect to local qemu
try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError as e:
    print(repr(e),file=sys.stderr)
    exit(1)

def menu():
    parser = argparse.ArgumentParser(description='Generate terraform module for maas')
    parser.add_argument("-o", "--output", help='Specify output file directory. Default is "output"', default="output")
    parser.add_argument("-f", "--file", help='Specify maas yaml file. Default is "maas.yaml"', default="maas.yaml")
    
    return parser.parse_args()

def render_tf(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("main.tf.j2")
    
    if not os.path.isdir(args.output):
        os.makedirs(args.output)
    
    output = open(args.output + "/main.tf","w")
    output.write(template_file.render(specs))
    output.close()
    
def render_network(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("network-config.cfg.j2")
    
    # Find virtual network by name
    try:
        network = conn.networkLookupByName(specs['net_name'])
    except libvirt.libvirtError as e:
        print(repr(e),file=sys.stderr)
        exit(1)
    
    net_xml = ET.XML(network.XMLDesc(0))
    specs["ip_gateway"] = net_xml.find("ip").attrib['address']
    specs["netmask"] = net_xml.find("ip").attrib['netmask']

    if not os.path.isdir(args.output):
        os.makedirs(args.output)
    
    output = open(args.output + "/config/network-config.cfg","w")
    output.write(template_file.render(specs))
    output.close()

def render_cloud_init(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("cloud-init.cfg.j2")
    
    specs['hashed_password']= crypt(specs['password'], mksalt(METHOD_SHA512))

    if "pub_key" not in specs.keys():
        specs["pub_key"] = open(os.path.expanduser('~/.ssh/id_rsa.pub'),"r").read().strip()
    else:
        specs["pub_key"] = open(specs["pub_key"],"r").read().strip()

    if not os.path.isdir(args.output+"/config"):
        os.makedirs(args.output+"/config")
    
    output = open(args.output + "/config/cloud-init.cfg","w")
    output.write(template_file.render(specs))
    output.close()

if __name__ == "__main__": 
    global args
    args = menu()

    maas_config = yaml.safe_load(open(args.file,"r"))
    render_tf(maas_config['machines'])
    render_cloud_init(maas_config['cloud_init'])
    render_network(maas_config['machines'])