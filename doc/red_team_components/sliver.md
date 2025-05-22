# Sliver Deployment

This page details the Ansible playbook for deploying the Sliver C2 Server. The playbook ensures the Sliver binary is installed, necessary configurations are generated, and the Sliver service is enabled and started.

For detailed information about Sliver, please refere to the [official documentation](https://github.com/BishopFox/sliver).


## Required Variables

The following variables must be set in the `vars/main.yaml` file for successful deployment. Customize these according to your environment:

``` yaml
# Sliver version to download
sliver_version_num: "1.5.42"

# Local (server) Operator configuration details
operator_name: "wasp"
sliver_lhost: "192.168.0.206"
operator_config_file_loc: "/home/slrt/sliver.cfg"

# Multiplayer users and their configuration files
multiplayer_users:
  - { name: "player01", config_path: "/opt/sliver/player01.cfg" }
  - { name: "player02", config_path: "/opt/sliver/player02.cfg" }

```

Note: You can create as many multiplayer users as you need. Just simply add more in de described format.


## Deployment Instructions

**1. Customize the `vars/main.yaml` file with your specific configurations as described above.**

**2. Run the Ansible playbook:**

``` shell
ansible-playbook -i <inventory_file> deploy_sliver.yaml

```

**3. Verify the Sliver service is running:**
Connect to your remote machine and run the following command to make sure the Sliver server is up and running:

``` shell
systemctl status sliver

```

## Notes
- Ensure the target machine has internet access to download the Sliver binary.
- The fetched multiplayer user configurations will be stored locally in `./output/sliver/player_configs/`. Use these in combination with the Sliver client to connect to your newly created sliver server.
- Update the sliver_version_num variable as needed to deploy newer versions of Sliver.


## Playbook Tasks Breakdown
Below is a breakdown of the tasks in the Ansible playbook:

###  1. Install Dependencies
``` yaml
- name: Install dependencies
  apt:
    name: mingw-w64
    state: present
    update_cache: yes

```

This task ensures the required dependencies (e.g., mingw-w64) are installed on the target system.

### 2. Create Sliver Directory
``` yaml
- name: Create Sliver directory
  file:
    path: /opt/sliver
    state: directory
    mode: "0755"

```

This creates the directory /opt/sliver with the appropriate permissions.

### 3. Download Sliver Binary
``` yaml
- name: Generate operator config
  command: "/opt/sliver/sliver operator -l {{ sliver_lhost}} -n {{ operator_name }} -s {{ operator_config_file_loc }}"
  args:
    creates: "{{ operator_config_file_loc }}"

```

Downloads the Sliver binary for the specified version.

### 4. Generate Operator Configuration
``` yaml
- name: Generate operator config
  command: "/opt/sliver/sliver operator -l {{ sliver_lhost}} -n {{ operator_name }} -s {{ operator_config_file_loc }}"
  args:
    creates: "{{ operator_config_file_loc }}"

```

Generates an operator configuration file with the specified operator name, listener host, and save location.

### 5. Create Multiplayer Users
``` yaml
- name: Create multiplayer users
  shell: "/opt/sliver/sliver operator --name {{ item.name }} --lhost {{ sliver_lhost }} --save {{ item.config_path }}"
  loop: "{{ multiplayer_users }}"
  args:
    executable: /bin/bash

```

Loops through the multiplayer_users list to create additional operators with their configuration files.

### 6. Fetch Player Configurations
``` yaml
- name: Copy generated player configs to local machine
  fetch:
    src: "{{ item.config_path }}"
    dest: "./output/sliver/player_configs/{{ item.name }}.cfg"
    flat: yes
  loop: "{{ multiplayer_users }}"

```

Copies the configuration files of multiplayer users from the target machine to the local machine for storage.

### 7. Deploy Systemd Service
``` yaml
- name: Copy systemd service file
  template:
    src: sliver.service.j2
    dest: /etc/systemd/system/sliver.service

```

Deploys a systemd service file for Sliver using the provided template.

### 8. Enable and Start Sliver Service
``` yaml
- name: Enable and start Sliver service
  systemd:
    name: sliver
    state: started
    enabled: true

```

Enables and starts the Sliver service to ensure it runs on system boot.

### Systemd Template
Below is the template for the Sliver systemd service file:

```
[Unit]
Description=Sliver C2 Server

[Service]
ExecStart=/opt/sliver/sliver daemon

[Install]
WantedBy=multi-user.target

```

This template ensures the Sliver daemon starts and remains active as a system service.