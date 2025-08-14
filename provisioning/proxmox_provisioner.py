from proxmoxer import ProxmoxAPI
import configparser
import logging
import os
from datetime import datetime
import paramiko

import pulumi
import pulumi_proxmoxve as pulumi_pve
import yaml

import mariadb
#import pandas
#import sqlalchemy


def create_cloudinit():
    # Get variables from config
    VM_ID = conf.get('PVE','PVE_TEMPLATE_ID')
    VM_NAME = "ubuntu-cloudinit-template"
    NODE = conf.get('PVE','PVE_NODE')
    ISO_STORAGE = conf.get('PVE','PVE_STORAGE_IMAGES')
    VM_STORAGE = conf.get('PVE','PVE_STORAGE_VMS')
    BRIDGE = conf.get('PVE','PVE_BRIDGE')
    IMAGE_PATH = "/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img"
    sourceURL = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"

    # Download image to pve
    proxmox.nodes(NODE).storage(ISO_STORAGE)("download-url").post(url=sourceURL, content="iso", filename="noble-server-cloudimg-amd64.img")


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
        ipconfig0='ip=dhcp'
    )
    
    # Convert to template
    proxmox.nodes(NODE).qemu(VM_ID).template.post()


def load_yaml_files_from_folder(folder_path):
    yaml_files = [file for file in os.listdir(folder_path) if file.endswith(".yaml")]
    loaded_data = []

    for yaml_file in yaml_files:
        file_path = os.path.join(folder_path, yaml_file)
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
            loaded_data.append(yaml_data)

    return loaded_data


# TODO read from DB instead of yaml
def create_VMs_from_templates(parsed_data):
    for vm in parsed_data:
        disks = []
        nets = []
        ip_configs = []
        ssh_keys = []

        for v in vm:
            for vmcount in range(v['count']):
                base_resource_name=v['resource_name']
                name_counter = vmcount + 1
                base_vm_id=v['vm_id'],
                for disk_entry in v['disks']:
                    for d in disk_entry:
                        disks.append(
                            proxmox.vm.VirtualMachineDiskArgs(
                                interface=disk_entry[d]['interface'],
                                datastore_id=disk_entry[d]['datastore_id'],
                                size=disk_entry[d]['size'],
                                file_format=disk_entry[d]['file_format'],
                                cache=disk_entry[d]['cache']
                            )
                        )

                for ip_config_entry in v['cloud_init']['ip_configs']:
                    ipv4 = ip_config_entry.get('ipv4')

                    if ipv4:
                        new_address = ''
                        ip, subnet = ipv4.get('address', '').split('/')
                        new_ip = str(ipaddress.ip_address(ip) + vmcount)
                        new_address = f"{new_ip}/{subnet}"

                        ip_configs = []
                        ip_configs.append(
                            proxmox.vm.VirtualMachineInitializationIpConfigArgs(
                                ipv4=proxmox.vm.VirtualMachineInitializationIpConfigIpv4Args(
                                    address=new_address,
                                    gateway=ipv4.get('gateway', '')
                                )
                            )
                        )

                for ssk_keys_entry in v['cloud_init']['user_account']['keys']:
                    ssh_keys.append(ssk_keys_entry)

                for net_entry in v['network_devices']:
                    for n in net_entry:
                        nets.append(
                            proxmox.vm.VirtualMachineNetworkDeviceArgs(
                                bridge=net_entry[n]['bridge'],
                                model=net_entry[n]['model']
                            )
                        )

                virtual_machine = proxmox.vm.VirtualMachine(
                    vm_id=base_vm_id[0] + vmcount,
                    resource_name=f"{base_resource_name}-{name_counter}",
                    node_name=v['node_name'],
                    agent=proxmox.vm.VirtualMachineAgentArgs(
                        enabled=v['agent']['enabled'],
                        # trim=v['agent']['trim'],
                        type=v['agent']['type']
                    ),
                    bios=v['bios'],
                    cpu=proxmox.vm.VirtualMachineCpuArgs(
                        cores=v['cpu']['cores'],
                        sockets=v['cpu']['sockets']
                    ),
                    clone=proxmox.vm.VirtualMachineCloneArgs(
                        node_name=v['clone']['node_name'],
                        vm_id=v['clone']['vm_id'],
                        full=v['clone']['full'],
                    ),
                    disks=disks,
                    memory=proxmox.vm.VirtualMachineMemoryArgs(
                        dedicated=v['memory']['dedicated']
                    ),
                    name=f"{base_resource_name}-{name_counter}",
                    network_devices=nets,
                    initialization=proxmox.vm.VirtualMachineInitializationArgs(
                        type=v['cloud_init']['type'],
                        datastore_id=v['cloud_init']['datastore_id'],
                        interface=v['cloud_init']['interface'],
                        dns=proxmox.vm.VirtualMachineInitializationDnsArgs(
                            domain=v['cloud_init']['dns']['domain'],
                            server=v['cloud_init']['dns']['server']
                        ),
                        ip_configs=ip_configs,
                        user_account=proxmox.vm.VirtualMachineInitializationUserAccountArgs(
                            username=v['cloud_init']['user_account']['username'],
                            password=os.getenv("PROXMOX_USER_ACCOUNT_PASSWORD"),
                            keys=ssh_keys
                        ),
                    ),
                    on_boot=v['on_boot'],
                    reboot=v['on_boot'],
                    opts=pulumi.ResourceOptions(provider=provider,ignore_changes=v['ignore_changes']),
                )

                pulumi.export(v['name'], virtual_machine.id)












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
    # TODO: test setup, use different user for connection
    try:
        conn = mariadb.connect(
            user="slrt",
            password="nqv9t80bm34tbqß34mßutnqv3t9q",
            host="127.0.0.1",
            port=3306,
            database="slrt"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cursor = conn.cursor()

    # https://proxmoxer.github.io/docs/latest/authentication/
    proxmox = ProxmoxAPI(conf.get('PVE','PVE_HOST'), user=conf.get('PVE','PVE_USER'), password=conf.get('PVE','PVE_PASS'), backend='ssh_paramiko')
    
    
    # setup pulumi provider
    provider = pulumi_pve.Provider('proxmoxve',
                            endpoint="https://" + conf.get('PVE','PVE_HOST') + ":8006",
                            insecure=true,
                            username=conf.get('PVE','PVE_USER'),
                            password=conf.get('PVE','PVE_PASS'),
                            )
    
    # create cloudinit on pve
    create_cloudinit()
    
    # read data from yaml files
    parsed_data = load_yaml_files_from_folder("infrastructure-definitions/")
    
    # create vms from parsed data
    create_VMs_from_templates(parsed_data)