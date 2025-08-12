# Create the user
pveum user add provisioner@pve
# Create a role for the user above
pveum role add provisioner -privs "Datastore.Allocate Datastore.AllocateSpace Datastore.AllocateTemplate Datastore.Audit Pool.Allocate Sys.Audit Sys.Console Sys.Modify SDN.Use VM.Allocate VM.Audit VM.Clone VM.Config.CDROM VM.Config.Cloudinit VM.Config.CPU VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.Migrate VM.Monitor VM.PowerMgmt User.Modify"
# Assign the provisioner user to the above role
pveum aclmod / -user provisioner@pve -role provisioner
# Create the token


# Grep the token from the output
TOKEN=$(pveum user token add provisioner@pve provider --privsep=0 | grep '^│ value' | awk -F '│' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')

echo $TOKEN > pve-token.txt