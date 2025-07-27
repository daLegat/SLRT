variable "proxmox_api_endpoint" {
  type = string
  description = "Proxmox cluster API endpoint https://pve.test.local:8006"
}

variable "proxmox_api_token" {
  type = string
  description = "Proxmox API token bpg proxmox provider with ID and token"
}

variable "proxmox_ip" {
  type = string
  description = "IP of the proxmox server"
}

variable "proxmox_hostname" {
  type = string
  description = "the hostname of the proxmox server"
}

variable "network_device"{
  type = string
  description = "the network device that should bes assigned to the virtual machine"
}

variable "vlan_id"{
  type = string
  description = "vlan that the infrastructure should be deployed to"
}

variable "datastore" {
  type = string
  description = "the name of the datastore the vm should be deployed to"
}

