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
    parser = argparse.ArgumentParser(description='Generate virtual machines using libvirt')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("-c", "--create", help='Create virtual machines based on file provided',action="store_true")
    action.add_argument("-d", "--delete", help='Delete virtual machines based on file provided',action="store_true")

    parser.add_argument("-f", "--file", help='Specify machines yaml file. Default is "machines.yaml"', default="machines.yaml")
    
    return parser.parse_args()

def generate_pool_xml(pool_name,pool_path):
    # Pool root section
    pool = ET.Element("pool", type="dir")

    # Pool name section
    ET.SubElement(pool,"name").text = pool_name

    # Pool path section
    pool_target = ET.SubElement(pool,"target")
    ET.SubElement(pool_target, "path").text = pool_path

    # XML to string
    return ET.tostring(pool).decode()

def generate_vol_xml(specs,pool_path):
    # Volume root section
    volume = ET.Element("volume")
    
    # Name section
    ET.SubElement(volume, "name").text = specs['name']

    # Size Section
    ET.SubElement(volume, "capacity", unit=specs['size'][-1:]).text = specs['size'][:-1]

    # Specs section
    volume_target = ET.SubElement(volume, "target")
    ET.SubElement(volume_target, "format", type="qcow2") # Volume format 
    ET.SubElement(volume_target, "path").text =  pool_path + "/" + specs['name'] # Pool directory
    
    # Permissions section
    target_permissions = ET.SubElement(volume_target, "permissions")
    ET.SubElement(target_permissions,"mode").text = "644"

    # XML to string
    return ET.tostring(volume).decode()

def generate_domain_xml(machine_name,specs):
    # Domain root section
    domain = ET.Element("domain",type="kvm")

    # Name section
    ET.SubElement(domain, "name").text = machine_name
    
    # Uuid section
    ET.SubElement(domain, "uuid").text = str(gen_uuid())

    # Metadata Section
    domain_metadata = ET.SubElement(domain, "metadata")
    metadata_libosinfo = ET.SubElement(domain_metadata, "libosinfo:libosinfo", {"xmlns:libosinfo":"http://libosinfo.org/xmlns/libvirt/domain/1.0"})
    ET.SubElement(metadata_libosinfo, "libosinfo:os", id="http://ubuntu.com/ubuntu/20.04")
    
    # Memory section
    ET.SubElement(domain, "memory", unit="MiB").text = str(specs['ram'])

    # Vcpu section
    ET.SubElement(domain, "vcpu").text = str(specs['vcpu'])

    # OS section
    domain_os = ET.SubElement(domain, "os")
    ET.SubElement(domain_os, "type", arch="x86_64", machine="pc-q35-4.2").text = 'hvm'
    ET.SubElement(domain_os, "boot", dev="network") # For pxe boot
    ET.SubElement(domain_os, "boot", dev="hd")

    # CPU section
    domain_cpu = ET.SubElement(domain, "cpu", mode="host-passthrough", check="none")
    ET.SubElement(domain_cpu, "cache", mode="passthrough")
    
    # Devices sections
    domain_devices = ET.SubElement(domain, "devices")

    ## Device emulator section
    ET.SubElement(domain_devices, "emulator").text = "/usr/bin/qemu-system-x86_64"

    ## Device disks section
    for device,size in specs["disk"].items():
        # Gather disk specs
        vol_specs = {}
        vol_specs["name"] = machine_name + "-" + device + ".qcow2"
        vol_specs["size"] = str(size)

        # Create disk
        vol_path = create_disk(vol_specs)
        
        # Add new created disk path
        domain_disk = ET.SubElement(domain_devices, "disk", type="file", device="disk")
        ET.SubElement(domain_disk, "driver", name="qemu", type="qcow2")
        ET.SubElement(domain_disk, "source", file=vol_path)
        ET.SubElement(domain_disk, "target", dev=device, bus="virtio")
    
    # Device NIC section
    for br_name in specs['nic']:
        domain_interface = ET.SubElement(domain_devices, "interface", type="bridge")
        ET.SubElement(domain_interface, "source", bridge=br_name) # Network bridge
        ET.SubElement(domain_interface, "model", type="virtio")

    # Device graphics Section
    ET.SubElement(domain_devices, "graphics", type="vnc", port="-1", autoport="yes")

    # Device video Section
    domain_video = ET.SubElement(domain_devices, "video")
    ET.SubElement(domain_video, "model", type="qxl", primary="yes")

    return ET.tostring(domain).decode()

def create_pool(pool_name,pool_path):
    # Generate volume xml
    pool_xml = generate_pool_xml(pool_name,pool_path)

    # create a new persistent storage pool
    pool = conn.storagePoolDefineXML(pool_xml, 0)
    if pool == None:
       print('Failed to create StoragePool object.', file=sys.stderr)
       exit(1)

def delete_pool(pool_name):
    # Get pool object
    pool = conn.storagePoolLookupByName(pool_name)

    # Delete pool
    pool.undefine()

def create_disk(vol_specs):
    # Get Pool object
    try:
        pool = conn.storagePoolLookupByName(pool_name)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    # List all existed volume in pool
    volumes = pool.listVolumes()
    
    # Check if volume already exist
    if vol_specs['name'] in volumes:
        volume = pool.storageVolLookupByName(vol_specs['name'])
        vol_path = ET.XML(volume.XMLDesc(0)).find("target")[0].text
        return vol_path

    # Get pool object xml info
    pool_xml = ET.XML(pool.XMLDesc(0))
    pool_path = pool_xml.find("target")[0].text
    
    # Generate volume xml
    vol_xml = generate_vol_xml(vol_specs,pool_path)

    # Get new volume path
    vol_path = ET.XML(vol_xml).find("target")[1].text
    
    # Create volume to pool
    volume = pool.createXML(vol_xml, 0)

    # Check if volume failed to create
    if volume == None:
        print('Failed to create a volume objects.', file=sys.stderr)
        exit(1)

    # Refresh pool list
    pool.refresh(0)

    # Return new created volume path
    return vol_path
    
def create_domain(machine_name,machine_specs):
    # List all existed domain
    domains =  conn.listAllDomains()
    
    # Check if domain already exist and print the info
    for domain in domains:
        if machine_name == domain.name():
            domain = conn.lookupByName(machine_name)
            if domain.isActive():
                domain.destroy()
            print_result(domain)
            return

    # Generate domain xml
    domain_xml = generate_domain_xml(machine_name,machine_specs)

    # Define new domain
    try:
        domain = conn.defineXMLFlags(domain_xml, 0)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    # Boot/start domain
    if domain.create() < 0:
        print('Cannot boot guest domain.', file=sys.stderr)
        exit(1)

    # Shutdown domain
    domain.destroy()

    # Show created domain
    print_result(domain)

def delete_disk(vol_name):
    # Get Pool object
    try:
        pool = conn.storagePoolLookupByName(pool_name)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    # Get Volume object
    try:
        volume = pool.storageVolLookupByName(vol_name)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)
    
    # Physically remove the storage volume from the underlying disk media
    volume.wipe(0)

    # Logically remove the storage volume from the storage pool
    volume.delete(0)

def delete_domain(machine_name):
    # Find virtual machine by name
    try:
        domain = conn.lookupByName(machine_name)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)
    
    # Get domain object xml info
    domain_xml = domain.XMLDesc(0)

    # Show remove domain
    print_result(domain)

    # Deactive virtual machine
    if domain.isActive():
        domain.destroy()

    # Remove virtual machine
    domain.undefine()

    # Delete domain's disk
    for disks in ET.XML(domain_xml).findall(".//disk"):
        for disk in disks:
            if disk.tag == 'source':
                    vol_name = disk.attrib['file'].split("/")[-1]
                    delete_disk(vol_name)

def print_result(domain):
    # Get domain object xml info
    domain_xml = domain.XMLDesc(0)

    if args.create:
        print("Created virtual machines details")
    elif args.delete:
        print("Below virtual machines will be removed")
    
    print("Name:\t" + ET.XML(domain_xml).find("name").text)
    print("UUID:\t" + domain.UUIDString())
    if args.create:
        print("Mac1:\t" + ET.XML(domain_xml).find(".//interface")[0].attrib['address'])
    print()

if __name__ == "__main__": 
    global args
    args = menu()

    machines_config = yaml.safe_load(open("machines.yaml","r"))
    
    global pool
    pool_name = machines_config['pool_name']

    for machine_groups in machines_config['machines']:
        machine_specs = {}
        machine_specs['vcpu'] = machines_config['machines'][machine_groups]['vcpu']
        machine_specs['ram'] = machines_config['machines'][machine_groups]['ram']
        machine_specs['disk'] = machines_config['machines'][machine_groups]['disk']
        machine_specs['nic'] = machines_config['machines'][machine_groups]['nic']
        for machine in machines_config['machines'][machine_groups]['name']:
            if args.create:
                create_domain(machine,machine_specs)
            if args.delete:
                delete_domain(machine)
    
    # Close libvirt connection
    conn.close()