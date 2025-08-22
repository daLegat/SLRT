from proxmoxer import ProxmoxAPI
import configparser
import logging
import os
from datetime import datetime
import paramiko

from pathlib import Path

import pulumi
import pulumi_proxmoxve as pulumi_pve
import yaml

import mariadb

import secrets
from Crypto.PublicKey import RSA


def create_cloudinit(pve_id):
    """create a ubuntu cloudinit and save it as a template on the proxmox host
    """    
    # Get variables from config
    pve_config = get_pve_config(pve_id)
    
    VM_ID = "9999"
    VM_NAME = "ubuntu-cloudinit-template"

    NODE = pve_config['name']
    ISO_STORAGE = pve_config['datastore_ISO']
    VM_STORAGE = pve_config['datastore_VMs']
    BRIDGE = pve_config['vbridge']
    IMAGE_PATH = "/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img"
    sourceURL = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"

    # Download image to pve
    proxmox.nodes(NODE).storage(ISO_STORAGE)("download-url").post(url=sourceURL, content="iso", filename="noble-server-cloudimg-amd64.img")

    try:
        proxmox.nodes(NODE).qemu(VM_ID).config.get()
    except:
        rootLogger.info(f"VM-template {VM_ID} not found. Creating.")
    else:
        rootLogger.info(f"VM-template {VM_ID} already exists. Skipping creation.")
        return
    
    # Import the Disk
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(conf.get('PVE','PVE_HOST'), username=conf.get('PVE','PVE_USER') , password=conf.get('PVE','PVE_PASS'))
    command = f"qm importdisk {VM_ID} {IMAGE_PATH} {VM_STORAGE}"
    ssh.exec_command(command)
    ssh.close()
    
    # Create the VM
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

    # Attach imported disk to VM
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        scsi0=f"{VM_STORAGE}:vm-{VM_ID}-disk-0"
    )

    # Add cloud-init drive
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        ide2=f"{VM_STORAGE}:cloudinit",
        boot='c',
        bootdisk='scsi0',
        serial0='socket',
        vga='serial0'
    )

    # Set cloud-init config
    proxmox.nodes(NODE).qemu(VM_ID).config.post(
        ciuser='ubuntu',
        cipassword='ubuntu',
        ipconfig0='ip=static'
    )
    
    # Convert to template
    proxmox.nodes(NODE).qemu(VM_ID).template.post()



def get_pve_vm_config(id):
    """retrieve config data as a dict for a specific vm

    Args:
        id (int): id of the desired vm

    Returns:
        dict: dict containing vm config
    """    
    config = {}
    cursor.execute("SELECT * FROM pve_vms WHERE vmid=?",(id,))
    vm_values = cursor.fetchall()[0]
    cursor.execute("SHOW COLUMNS FROM slrt.pve_vms")
    vm_keys = cursor.fetchall()
    count = 0
    for entry in vm_keys:
        config[entry[0]] = vm_values[count]
        count += 1
    return config


def get_pve_config(id):
    config = {}
    cursor.execute("SELECT * FROM pve_environment WHERE idenvironments=?",(id,))
    vm_values = cursor.fetchall()[0]
    cursor.execute("SHOW COLUMNS FROM slrt.pve_environment")
    vm_keys = cursor.fetchall()
    count = 0
    for entry in vm_keys:
        config[entry[0]] = vm_values[count]
        count += 1
    return config
    
    
def create_pve_VMs_from_template(vm_config):
    vm_password = secrets.token_urlsafe(32)
    vm_username = secrets.token_urlsafe(32)
    vm_ssh_key = RSA.generate(2048)
    vm_ssh_pubkey = vm_ssh_key.publickey().export_key(format='OpenSSH').decode()

    vm_ssh_key = vm_ssh_key.export_key(format='OpenSSH').decode()
    
    pve_config = get_pve_config(vm_config['environmentid'])

    disks = [pulumi_pve.vm.VirtualMachineDiskArgs(
            interface="ide2",
            datastore_id=pve_config['datastore_VMs'],
            size=vm_config['Disksize'],
            file_format="raw",
            cache="none"
        )]

    ip_configs = [pulumi_pve.vm.VirtualMachineInitializationIpConfigArgs(
            ipv4=pulumi_pve.vm.VirtualMachineInitializationIpConfigIpv4Args(
                address=vm_config['IP_address'],
                gateway=vm_config['Gateway']
            )
        )]
    
    net = [pulumi_pve.vm.VirtualMachineNetworkDeviceArgs(
            bridge=pve_config['vbridge'],
            model="virtio"
        )]
    
    virtual_machine = pulumi_pve.vm.VirtualMachine(
        vm_id=vm_config['vmid'],
        resource_name=vm_config['name'],
        node_name=pve_config['name'],
        agent=pulumi_pve.vm.VirtualMachineAgentArgs(
            enabled=True,
            type="virtio"
        ),
        bios="seabios",
        cpu=pulumi_pve.vm.VirtualMachineCpuArgs(
            cores=vm_config['VCPUs'],
            sockets="1"
        ),
        clone=pulumi_pve.vm.VirtualMachineCloneArgs(
            node_name=pve_config['name'],
            vm_id="9999",
            full=True,
        ),
        disks=disks,
        memory=pulumi_pve.vm.VirtualMachineMemoryArgs(
            dedicated=vm_config['RAM']
        ),

        name=pve_config['name'],
        network_devices=net,
        initialization=pulumi_pve.vm.VirtualMachineInitializationArgs(
            type="nocloud",
            datastore_id=pve_config['datastore_VMs'],
            interface="scsi0",
            dns=pulumi_pve.vm.VirtualMachineInitializationDnsArgs(
                domain="",
                servers=[vm_config['DNS-server']]
            ),
            ip_configs=ip_configs,
            user_account=pulumi_pve.vm.VirtualMachineInitializationUserAccountArgs(
                username=vm_username,
                password=vm_password,
                keys=[vm_ssh_pubkey]
            ),
        ),
        on_boot=True,
        reboot=True,
        opts=pulumi.ResourceOptions(provider=provider,ignore_changes=("disks","cdrom")),
    )
    
    # TODO: export and execute the pulumi vm
    pulumi.export('provisioning', virtual_machine.id)




    cursor.execute("SELECT * FROM pve_vms WHERE vmid = ?", (vm_config['vmid'],))


    # save credentials to database
    cursor.execute(
    "UPDATE pve_vms SET ssh_key = ?, username = ?, password = ? WHERE vmid = ?",(vm_ssh_key, vm_username, vm_password, int(vm_config['vmid'])))
    conn.commit()
    
    


if __name__ == '__main__':
    
    
    # Setup configparser
    conf = configparser.ConfigParser()
    conf.read('config.env')
    
    # Setup logparser
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

    # Detect loglevel
    if conf.get('PROVISIONER','LOGLEVEL') == 'info':
        rootLogger.setLevel(logging.INFO)
    elif conf.get('PROVISIONER','LOGLEVEL') == 'error':
        rootLogger.setLevel(logging.INFO)
    else:
        rootLogger.setLevel(logging.DEBUG)



    # connect to SQL database
    try:
        conn = mariadb.connect(
            user="slrt",
            password="slrt",
            host="127.0.0.1",
            port=3306,
            database="slrt"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
        
    cursor = conn.cursor()
    
    
    sql_script = Path("./db_init.sql").read_text()
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]

    for statement in statements:
        cursor.execute(statement)
        
    # https://proxmoxer.github.io/docs/latest/authentication/
    proxmox = ProxmoxAPI(conf.get('PVE','PVE_HOST'), user=conf.get('PVE','PVE_USER'), password=conf.get('PVE','PVE_PASS'), backend='ssh_paramiko')
    
    
    # setup pulumi provider
    # TODO: use ssh instead of http
    provider = pulumi_pve.Provider('proxmoxve',
                            endpoint="https://" + conf.get('PVE','PVE_HOST') + ":8006",
                            insecure=True,
                            username=conf.get('PVE','PVE_USER') + "@pam",
                            password=conf.get('PVE','PVE_PASS'),
                            )
    


    # create cloudinit on pve with id 1
    create_cloudinit(1)
    
    
    config = get_pve_vm_config(100)
 
    create_pve_VMs_from_template(config)