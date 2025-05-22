# Getting Started

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Pre-configured hosts with authorized SSH keys and usernames ready for Ansible configuration.
- Ensure that the SSH keys are properly distributed and that you can access the hosts via SSH without a password prompt.
- Verify that the necessary users on the hosts have sufficient privileges for the intended configuration tasks.

Note: All of this can be achieved using tools like **Vagrant** and **Terraform** or it can be done manually.

## Getting Started

Follow these steps to get the project up and running:

1. **Clone the Repository**  
The first step is to clone this repository to your local machine. You can do this with the following command:

```bash
git clone git@gitlab.fh-ooe.at:P41540/2024-streamlined-red-teaming-mpr3.git
```

After cloning the repository, navigate to the newly created project folder.

---

2. **Update the Inventory File**  
Edit the `inventory.yaml` file to define your hosts. Für jede Hostgruppe gibst du dabei IP, Benutzer und Rollen an.

Example `inventory.yaml` structure:
```yaml
all:
  children:
    redteam:
      children:
        sliver:
          hosts:
            sliver_backend
        redirector:
          hosts:
            redirector_backend
        evilgophish:
          hosts:
            evilgophish_backend
        veildrop:
          hosts:
            veildrop_backend
        ghostwriter:
          hosts:
            ghostwriter_backend

  vars:
    ansible_user: slrt
    ansible_become: true

  hosts:
    sliver_backend:
      ansible_host: 192.168.0.206
    redirector_backend:
      ansible_host: 192.168.0.205
    evilgophish_backend:
      ansible_host: 192.168.0.203
    veildrop_backend:
      ansible_host: 192.168.0.204
    ghostwriter_backend:
      ansible_host: 192.168.0.207
```

---

3. **Secure Sensitive Data Using Ansible Vault**  
Creating an Ansible Vault helps to keep credentials and keypaths secure:

```bash
mkdir -p group_vars/all
ansible-vault create group_vars/all/vault.yml
```

After setting a vault password, add these lines to the vault file. Make sure to use your actual keypath and sudo password for the remote machine:

```yaml
ansible_ssh_private_key_file: /home/<local_user>/.ssh/slrt_deployment_id
ansible_sudo_pass: <your_sudo_password>
```

Use the following command to edit the vault:

```bash
ansible-vault edit group_vars/all/vault.yml
```

---

4. **Configure Role-Specific Variables**

Each role can have its own configuration settings in the vars/main.yaml file. Edit these files to define any role-specific settings, such as paths or additional parameters.

Example _vars/main.yaml_ for a Sliver C2 Server role:

```yaml
sliver_version_num: "1.5.42"
operator_name: "wasp"
sliver_lhost: "192.168.0.206"
operator_config_file_loc: "/home/slrt/sliver.cfg"
multiplayer_users:
  - { name: "bee", config_path: "/opt/sliver/bee.cfg" }
  - { name: "bug", config_path: "/opt/sliver/bug.cfg" }
```

For example, as you can see, a specific version number is set at the top of the file. If a more comprehensive explaination of the defined variables is needed, take a look at the wiki subpages for the specific roles.

---

5. **Running a specific deploy script (Sliver):**  
Once the inventory and variables are configured as needed, execute the Ansible playbook:

```bash
ansible-playbook -i inventory.yaml deploy-sliver.yaml --ask-vault-pass
```

---

6. **Running all deploy scripts at once:**  
You can also deploy the whole infrastructure at once by using the `deploy-all.yaml` playbook:

```bash
ansible-playbook -i inventory.yml deploy_all.yml --ask-vault-pass
```

---

### .gitignore Recommendation

To avoid accidentally committing secrets stored elsewhere in the project:

```gitignore
# Inventories with sensitive info
inventories/**/group_vars/all/vault.yml

# SSH private keys
*.pem
*.key
*.id_rsa
*.id_ed25519
```
