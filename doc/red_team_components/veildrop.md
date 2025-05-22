# VeilDrop Deployment

This page details the Ansible playbook for deploying the VeilDrop Service. The playbook configures a Flask-based application that serves payload files based on user-agent authentication and ensures the VeilDrop service is running.

## Required Variables
The following variables must be set in the vars/main.yaml file for successful deployment. Customize these according to your environment:

``` yaml
# Installation directory for VeilDrop
install_dir: "/opt/veildrop"

# Service name for systemd management
service_name: "veildrop"

# Python binary location
python_bin: "/usr/bin/python3"

# Allowed user-agent prefix for authentication
secret_user_agent: "SpecialAgent"

# Systemd service template file
service_template: "veildrop.service.j2"

# Index HTML template file
index_template: "index.html"

# Default payload file
payload_template: "payload.bin"
```

## Deployment Instructions

**1. Customize the vars/main.yaml file with your specific configurations as described above.**

**2. Run the Ansible playbook:**

``` shell
ansible-playbook -i <inventory_file> deploy_veildrop.yaml
```

**3. Verify the VeilDrop service is running:**

``` shell
systemctl status veildrop
```

## Notes
- Ensure Python3 and Flask are installed on the target machine.
- The payloads should be preloaded in the payload directory or transferred via scp.
- The veildrop.service systemd unit ensures the service restarts if it fails.

## Playbook Tasks Breakdown

### 1. Install Dependencies
``` yaml
- name: Install required Python packages
  apt:
    name: 
      - python3
      - python3-pip
      - python3-flask
      - python3-waitress
    state: present
  become: yes
```
This task ensures the necessary Python dependencies for VeilDrop are installed.

### 2. Create Directory and Deploy VeilDrop
``` yaml
- name: Create template directory
  file:
    path: "{{ install_dir }}/templates"
    state: directory
    mode: '0755'

- name: Copy the program to the remote
  copy:
    src: "files/"
    dest: "{{ install_dir }}"
```
Copies the main VeilDrop application script to the designated installation directory.

### 3. Deploy Index Page
``` yaml
- name: Copy the legitimate website
  copy:
    src: "templates/{{ index_template }}"
    dest: "{{ install_dir }}/templates/index.html"
```
Ensures the legitimate-looking index page is placed in the correct location.

### 4. Copy Example Payload
``` yaml
- name: Copy the example payload to the remote
  template:
    src: "files/{{ payload_template }}"
    dest: "{{ install_dir }}/payloads/{{ payload_template }}"
```
This task copies the example payload to the remote machines /payload directory.

### 5. Configure Systemd Service
``` yaml
- name: Create the Systemd service file to the remote
  template:
    src: templates/veildrop.service.j2
    dest: /etc/systemd/system/veildrop.service
    owner: root
    group: root
    mode: "0644"
```
Deploys the systemd service configuration for automatic service management.

### 6. Enable and Start VeilDrop Service
``` yaml
- name: Enable and start VeilDrop service
  systemd:
    name: veildrop
    state: started
    enabled: true
```
Ensures that the VeilDrop service starts on boot and remains active.

## Systemd Service Template
Below is the VeilDrop systemd service template (veildrop.service.j2):

``` ini
[Unit]
Description=VeilDrop Service
After=network.target

[Service]
User=root
WorkingDirectory={{ install_dir }}
ExecStart={{ python_bin }} {{ install_dir }}/veildrop.py
Restart=always

[Install]
WantedBy=multi-user.target
```
This template ensures the VeilDrop service is automatically restarted if it crashes.

## VeilDrop Application (veildrop.py)
Below is a summary of the VeilDrop application logic:
- It is a Flask-based server using Waitress for deployment.
- The user-agent header is checked for a specific prefix (SpecialAgent).
- If authentication succeeds, the requested payload is served.
- If authentication fails, a fallback index.html page is displayed.

### Example Requests:
You can run the following commands to test the payload server:

``` shell
# Valid request with an existing payload:
curl -A "SpecialAgent:payload.bin" "http://127.0.0.1:8080/"

# Invalid request with an incorrect user-agent:
curl -A "WrongAgent" "http://127.0.0.1:8080/"

# Valid user-agent with a nonexistent payload:
curl -A "SpecialAgent:nonexistent.bin" "http://127.0.0.1:8080/"

```

## Legitimate Website Template
Below is the content of the legitimate website template (index.html):

``` html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome to Our Website!</h1>
    <p>This is a legitimate page, nothing shady to see here.</p>
</body>
</html>
```

This page is shown when a user accesses the service without proper authentication. You can, however, customize this template to fit your special purpose.