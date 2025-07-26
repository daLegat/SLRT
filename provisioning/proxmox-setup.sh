# Create the user
pveum user add terraform@pve
# Create a role for the user above
pveum role add Terraform -privs "Datastore.Allocate Datastore.AllocateSpace Datastore.AllocateTemplate Datastore.Audit Pool.Allocate Sys.Audit Sys.Console Sys.Modify SDN.Use VM.Allocate VM.Audit VM.Clone VM.Config.CDROM VM.Config.Cloudinit VM.Config.CPU VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.Migrate VM.Monitor VM.PowerMgmt User.Modify"
# Assign the terraform user to the above role
pveum aclmod / -user terraform@pve -role Terraform
# Create the token


# Grep the token from the output
TOKEN=$(pveum user token add terraform@pve provider --privsep=0 | grep '^│ value' | awk -F '│' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')

echo $TOKEN > pve-token.txt