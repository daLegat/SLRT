from proxmoxer import ProxmoxAPI
import configparser
import logging
import os
from datetime import datetime
import paramiko

#import pulumi
#import pulumi_proxmoxve as proxmox

    
def create_cloudinit():
    VM_ID = 9999
    VM_NAME = "ubuntu-cloudinit-template"
    NODE = conf.get('PVE','PVE_NODE')
    ISO_STORAGE = conf.get('PVE','PVE_STORAGE_IMAGES')
    VM_STORAGE = conf.get('PVE','PVE_STORAGE_VMS')
    BRIDGE = conf.get('PVE','PVE_BRIDGE')
    IMAGE_PATH = "/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img"
    sourceURL = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"

    proxmox.nodes(NODE).storage(ISO_STORAGE)("download-url").post(url=sourceURL, content="iso", filename="noble-server-cloudimg-amd64.img")


    print("Import disk")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(conf.get('PVE','PVE_HOST'), username=conf.get('PVE','PVE_USER') , password=conf.get('PVE','PVE_PASS'))
    command = f"qm importdisk {VM_ID} {IMAGE_PATH} {VM_STORAGE}"
    ssh.exec_command(command)
    ssh.close()


    print("\n")
    print("\n")
    

    print("Create VM")
    
    # Step 3: Create the VM
    proxmox.nodes(NODE).qemu.post(
        vmid=VM_ID,
        name=VM_NAME,
        memory=2048,
        cores=2,
        sockets=1,
        net0=f"virtio,bridge={BRIDGE}",
        ostype='l26',
        scsihw='virtio-scsi-pci'
    )


    print("\n")
    print("\n")
 
    
    print("Attach imported disk to VM")
    
    # Step 4: Attach imported disk to VM
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        scsi0=f"{VM_STORAGE}:vm-{VM_ID}-disk-0"
    )

    print("\n")
    print("\n")
   

    print("ADd cloudinit drive")
    # Step 5: Add cloud-init drive
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        ide2=f"{VM_STORAGE}:cloudinit",
        boot='c',
        bootdisk='scsi0',
        serial0='socket',
        vga='serial0'
    )
    

    print("\n")
    print("\n")

    print("set cloudinit drive")
    # Step 6: Set cloud-init config (optional)
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        ciuser='ubuntu',
        cipassword='ubuntu',
        ipconfig0='ip=dhcp'
    )
    

    print("\n")
    print("\n")

    print("convert to template")
    # Step 7: Convert to template (optional)
    proxmox.nodes(NODE).qemu(VM_ID).template.post()

if __name__ == '__main__':
    # setup configparser
    conf = configparser.ConfigParser()
    conf.read('config.env')
    
    # setup logparser
    if not os.path.exists("logs"):
        os.mkdir("logs")

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/log_{timestamp}.log"
    fileHandler = logging.FileHandler(log_filename)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    # detect loglevel
    if conf.get('PROVISIONER','LOGLEVEL') == 'info':
        rootLogger.setLevel(logging.INFO)
    elif conf.get('PROVISIONER','LOGLEVEL') == 'error':
        rootLogger.setLevel(logging.INFO)
    else:
        rootLogger.setLevel(logging.DEBUG)



    # https://proxmoxer.github.io/docs/latest/authentication/
    # TODO: make ssh key auth possible
    proxmox = ProxmoxAPI(conf.get('PVE','PVE_HOST'), user=conf.get('PVE','PVE_USER'), password=conf.get('PVE','PVE_PASS'), backend='ssh_paramiko')
    
        
    create_cloudinit()
    
    