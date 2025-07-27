resource "proxmox_virtual_environment_vm" "c2" {
  count       = 1
  name        = "c2"
  description = "Managed by Terraform"
  tags        = ["terraform", "ubuntu"]

  node_name = "pve"
  vm_id     = "100"


  cpu {
    cores = 1
    type = "host"
  }

  memory {
    dedicated = 1024
  }


  agent {
    # read 'Qemu guest agent' section, change to true only when ready
    enabled = true
  }

  startup {
    order      = "3"
    up_delay   = "60"
    down_delay = "60"
  }

  disk {
    datastore_id = "raid-10-node02"
    file_id      = "local:iso/jammy-server-cloudimg-amd64.img"
    interface    = "virtio0"
    iothread     = true
    discard      = "on"
    size         = 8
    file_format  = "raw"
  }


  initialization {
    dns {
      servers = ["1.1.1.1", "8.8.8.8"]
      domain = "test.local"
    }
    ip_config {
      ipv4 {
        address = "10.40.20.150/24"
        gateway = "10.40.20.1"
      }
    }
    datastore_id = "local-lvm"

    user_data_file_id = proxmox_virtual_environment_file.ubuntu_cloud_init.id
  }

  network_device {
    bridge = "vmbr0"
    vlan_id = "20"
  }

  operating_system {
    type = "l26"
  }

  keyboard_layout = "no"

  lifecycle {
    ignore_changes = [
      network_device,
    ]
  }
}
