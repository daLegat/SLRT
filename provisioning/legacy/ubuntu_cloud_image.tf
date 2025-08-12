resource "proxmox_virtual_environment_file" "ubuntu_cloud_image" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = "pve"

  source_file {
    # you may download this image locally on your workstation and then use the local path instead of the remote URL
    path      = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"

    # you may also use the SHA256 checksum of the image to verify its integrity
    checksum = "1d82c1db56e7e55e75344f1ff875b51706efe171ff55299542c29abba3a20823"
  }
}

