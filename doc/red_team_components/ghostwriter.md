# Ghostwriter Deployment

This page details the Ansible playbook for deploying the Ghostwriter platform. The playbook ensures Docker is installed and configured, Ghostwriter is cloned and set up, and all necessary configurations are applied.

For detailed information about Sliver, please refere to the [official documentation](https://github.com/GhostManager/Ghostwriter).


## Required Variables

The following variables must be set in the `vars/main.yaml` file for successful deployment. Customize these according to your environment:

```yaml
# External IP address for the server
external_ip: "{{ hostvars[inventory_hostname].ansible_host }}"

# Ghostwriter repository details
ghostwriter_repo_url: "https://github.com/GhostManager/Ghostwriter.git"
ghostwriter_cli_version: "v4.3.9"
ghostwriter_cli_url: "https://github.com/GhostManager/Ghostwriter_CLI/releases/download/{{ ghostwriter_cli_version }}/ghostwriter-cli-linux"

# Installation directories
ghostwriter_install_dir: "/opt/ghostwriter"
ghostwriter_cli_path: "/usr/local/bin/ghostwriter-cli"

# TLS Certificate details
ghostwriter_cert_dir: "/etc/ghostwriter/certs"
```

## Deployment Instructions

**1. Customize the `vars/main.yaml` file with your specific configurations as described above.**

**2. Run the Ansible playbook:**

```shell
ansible-playbook -i <inventory_file> deploy_ghostwriter.yaml
```

**3. Verify the Docker service is running:**

```shell
systemctl status docker
```

**4. Access the Ghostwriter web interface:**

Use the server's external IP in your browser to connect to Ghostwriter after setup. Example: `https://<external_ip>`.

---

## Notes

- Ensure the target machine has internet access to download Docker and Ghostwriter dependencies.
- The fetched admin password will be stored locally in `./output/ghostwriter/admin_password.txt`. Keep it secure.
- Update the `ghostwriter_cli_version` variable as needed to deploy newer versions of Ghostwriter.

---

## Playbook Tasks Breakdown

### 1. Install GPG Package (Debian)
```yaml
- name: Install gpg package (Debian)
  apt:
    name: gpg
    state: present
  when: ansible_facts.os_family == 'Debian'
```
Ensures the GPG package is installed on Debian-based systems.

### 2. Add Docker's Official GPG Key
```yaml
- name: Add Docker's official GPG key
  apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    state: present
  when: ansible_facts.os_family == 'Debian'
```
Adds Docker's GPG key for package signing.

### 3. Update apt Cache
```yaml
- name: Update apt cache
  apt:
    update_cache: yes
  when: ansible_facts.os_family == 'Debian'
```
Updates the package index on Debian systems.

### 4. Set Up Docker Repository (Debian)
```yaml
- name: Set up the Docker repository
  apt_repository:
    repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present
  when: ansible_facts.os_family == 'Debian'
```
Adds Docker's official repository on Debian-based systems.

### 5. Set Up Docker Repository (RedHat)
```yaml
- name: Add Docker's official repository
  yum_repository:
    name: docker
    description: Docker Repository
    baseurl: https://download.docker.com/linux/centos/7/x86_64/stable
    gpgcheck: yes
    gpgkey: https://download.docker.com/linux/centos/gpg
    enabled: yes
  when: ansible_facts.os_family == 'RedHat'
```
Adds Docker's official repository for RedHat-based systems.

### 6. Install Docker and Compose Plugin (Debian)
```yaml
- name: Install Docker and Compose Plugin (Debian)
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-compose-plugin
    state: present
  when: ansible_facts.os_family == 'Debian'
```
Installs Docker CE and Compose plugin on Debian systems.

### 7. Install Docker and Compose Plugin (RedHat)
```yaml
- name: Install Docker and Compose Plugin (RedHat)
  yum:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-compose-plugin
    state: present
  when: ansible_facts.os_family == 'RedHat'
```
Installs Docker CE and Compose plugin on RedHat systems.

### 8. Start Docker Service
```yaml
- name: Start Docker service
  service:
    name: docker
    state: started
    enabled: true
```
Starts and enables the Docker service.

### 9. Verify Docker Daemon is Running
```yaml
- name: Verify Docker daemon is running
  shell: |
    systemctl is-active docker
  register: docker_status
  failed_when: docker_status.rc != 0
  changed_when: false
  ignore_errors: true
```
Ensures the Docker daemon is active.

### 10. Restart Docker Service if Necessary
```yaml
- name: Restart Docker service if necessary
  service:
    name: docker
    state: restarted
  when: docker_status.rc != 0
```
Restarts the Docker service if it's not running.

### 11. Clone Ghostwriter Repository
```yaml
- name: Clone Ghostwriter repository
  git:
    repo: "{{ ghostwriter_repo_url }}"
    dest: "{{ ghostwriter_install_dir }}"
    force: yes
```
Clones the Ghostwriter repository into the specified directory.

### 12. Ensure .env File Exists
```yaml
- name: Ensure .env file exists
  file:
    path: "{{ ghostwriter_install_dir }}/.env"
    state: touch
    mode: "0644"
```
Creates the `.env` file if it does not exist.

### 13. Add External IP to Allowed Hosts
```yaml
- name: Add external IP to allowed hosts
  lineinfile:
    path: "{{ ghostwriter_install_dir }}/.env"
    regexp: "^ALLOWED_HOSTS"
    line: "ALLOWED_HOSTS=127.0.0.1,localhost,{{ external_ip }}"
```
Adds the external IP to allowed hosts to allow incomming connections.

### 14. Add Wildcard to DJANGO_ALLOWED_HOSTS
```yaml
- name: Add wildcard to DJANGO_ALLOWED_HOSTS
  lineinfile:
    path: "{{ ghostwriter_install_dir }}/.env"
    regexp: "^DJANGO_ALLOWED_HOSTS"
    line: "DJANGO_ALLOWED_HOSTS=*"
    state: present
```
Adds a wildcard entry for `DJANGO_ALLOWED_HOSTS`. This is needed for accessing the Ghostwriter dashboard later.

### 15. Install Ghostwriter
```yaml
- name: Install Ghostwriter via CLI script
  command: "{{ ghostwriter_install_dir }}/ghostwriter-cli-linux install"
  args:
    chdir: "{{ ghostwriter_install_dir }}"
  become: yes
```
Installs Ghostwriter using the provided CLI script.

### 16. Restart All Containers
```yaml
- name: Restart all containers after installation
  command: "{{ ghostwriter_install_dir }}/ghostwriter-cli-linux containers restart"
  args:
    chdir: "{{ ghostwriter_install_dir }}"
  become: yes
```
Restarts all Ghostwriter containers after the installation script is run.

### 17. Fetch Admin Password
```yaml
- name: Get admin password from Ghostwriter host
  shell: "./ghostwriter-cli-linux config get admin_password"
  args:
    chdir: "{{ ghostwriter_install_dir }}"
  register: admin_password_result
  become: yes

- name: Ensure output directory exists
  file:
    path: "./output"
    state: directory
    mode: "0755"

- name: Save admin password to a temporary file on the remote host
  copy:
    content: "{{ admin_password_result.stdout }}"
    dest: "/tmp/admin_password.txt"
    mode: "0644"
  become: yes

- name: Fetch the admin password to the local machine
  fetch:
    src: "/tmp/admin_password.txt"
    dest: "./output/ghostwriter/admin_password.txt"
    flat: yes
```
Retrieves and stores the admin password locally, so you can login in to your newly created Ghostwriter instance.

---

## System Configuration

Below is the server configuration `config.yml.j2` for Ghostwriter, including TLS settings:

```yaml
server:
  listen: ":443"
  tls:
    cert: "{{ ghostwriter_cert_dir }}/cert.pem"
    key: "{{ ghostwriter_cert_dir }}/key.pem"
  allowed_hosts:
    - "localhost"
    - "127.0.0.1"
    - "{{ external_ip }}"
```
This configuration ensures Ghostwriter runs securely on HTTPS using the provided key and certificate. The external IP Address is also written into the allowed hosts, so that Ghostwriter is reachable from the outside network.

---