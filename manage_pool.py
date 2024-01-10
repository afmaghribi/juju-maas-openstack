#!/usr/bin/python3
import libvirt
import urllib3
import xml.etree.ElementTree as ET
from pathlib import Path
import sys,os
import argparse
from tqdm import tqdm

# Connect to local qemu
try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError as e:
    print(repr(e),file=sys.stderr)
    exit(1)

http = urllib3.PoolManager()

def menu():
    parser = argparse.ArgumentParser(description='Create libvirt pool and download cloudimage')
    # action = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-c", "--create", help='Create libvirt pool',action="store_true")
    parser.add_argument("-d", "--delete", help='Delete libvirt pool',action="store_true")
    parser.add_argument("-g", "--download", help='Download cloudimage to pool',action="store_true",default=False)
    parser.add_argument("-f", "--force", help='Force delete unempty pool path',action="store_true",default=False)

    return parser.parse_args()

def print_result(pool):
    # Pool xml to get pool 
    pool_xml = ET.XML(pool.XMLDesc(0))
    pool_name = pool_xml[0].text
    pool_path = pool_xml.find("target")[0].text

    if args.create:
        print("Created pool details")
    if args.delete:
        print("Deleted pool details")

    print("Name:\t" + pool_name)
    print("Path:\t" + pool_path)

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

def create_pool():
    # Set pool name
    pool_name = os.getcwd().split("/")[-1] + "_pool_images" # current directory name

    pool_path = os.getcwd() + "/" + pool_name
    if not os.path.isdir(pool_path):
        os.makedirs(pool_path)

    # Generate volume xml
    pool_xml = generate_pool_xml(pool_name,pool_path)

    # create a new persistent storage pool
    pool = conn.storagePoolDefineXML(pool_xml, 0)
    if pool == None:
       print('Failed to create StoragePool object.', file=sys.stderr)
       exit(1)
    
    pool.create()
    pool.setAutostart(1)
    
    print_result(pool)

    return pool_path

def delete_pool():
    # Set pool name
    pool_name = os.getcwd().split("/")[-1] + "_pool_images" # current directory name

    # Get pool object
    pool = conn.storagePoolLookupByName(pool_name)

    # Get pool object xml info
    pool_xml = ET.XML(pool.XMLDesc(0))
    pool_path = pool_xml.find("target")[0].text

    print_result(pool)
    
    if os.path.isdir(pool_path):
        if args.force:
            for file in os.listdir(pool_path):
                os.remove(pool_path+"/"+file)
        os.removedirs(pool_path)

    # Delete pool
    pool.destroy()
    pool.undefine()

def downloader(url, resume_byte_pos=None):
    file = Path(".") / url.split('/')[-1]
    
    resp = http.request("HEAD",url)
    file_size = int(resp.headers['Content-Length'])

    resume_header = ({'Range': f'bytes={resume_byte_pos}-'} if resume_byte_pos else None)
    
    r = http.request("GET", url, preload_content=False, headers=resume_header)
    block_size = 1024
    initial_pos = resume_byte_pos if resume_byte_pos else 0
    mode = 'ab' if resume_byte_pos else 'wb'
    file = Path(".") / url.split('/')[-1]
    with open(file, mode) as f:
        with tqdm(total=file_size, unit='B',
                  unit_scale=True, unit_divisor=1024,
                  desc=file.name, initial=int(initial_pos),
                  ascii=True, miniters=1) as pbar:
            while True:
                chunk = r.read(32 * block_size)
                if not chunk:
                    break
                f.write(chunk)
                pbar.update(len(chunk))


def download_image(url,pool_path):
    # Change current workdir
    os.chdir(pool_path)
    file = Path(".") / url.split('/')[-1]

    # Get size
    resp = http.request("HEAD",url)
    file_size_online= int(resp.headers['Content-Length'])

    # Get filesize of online and offline file
    if file.exists():
        print("Nothing to download")
        file_size_offline = file.stat().st_size

        if file_size_online != file_size_offline:
            print(f'File {file} is incomplete. Resume download.')
            downloader(url, file_size_offline)
        else:
            print(f'File {file} is complete. Skip download.')
            pass
    else:
        print(f'File {file} does not exist. Start download.')
        downloader(url)

if __name__ == "__main__": 
    global args
    args = menu()

    image_repo_url = "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"

    if args.create:
        create_pool()
    if args.download:
        pool_path = os.getcwd() + "/" + os.getcwd().split("/")[-1] + "_pool_images"
        download_image(image_repo_url,pool_path)
    if args.delete:
        delete_pool()
    
    # Close libvirt connection
    conn.close()