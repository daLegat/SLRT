# EvilGophish Deployment

This page details the Ansible playbook for deploying the EvilGophish service. The playbook ensures all dependencies are installed, the EvilGophish repository is cloned, SSL certificates are configured, and the services are set up and started.

For detailed information about EvilGophish, please refere to the [official documentation](https://github.com/fin3ss3g0d/evilgophish).

## Required Variables

The following variables must be set in the vars/main.yaml file for successful deployment. Customize these according to your environment:

``` yaml
root_domain: "evilphisher.com"
subdomains: "login accounts"
redirect_url: "example.com"
use_live_feed: true
ssl_cert_path: "/etc/letsencrypt/live/evilphisher.com/fullchain.pem"
ssl_key_path: "/etc/letsencrypt/live/evilphisher.com/privkey.pem"
twilio_account_sid: "SID"
twilio_auth_token: "AUTHTOKEN"
twilio_phone_number: "+12345656789"
```

## Deployment Instructions

**1. Customize the `vars/main.yaml` file with your specific configurations as described above.**

**2. Run the Ansible playbook:**

``` shell
ansible-playbook -i <inventory_file> deploy_evilgophish.yaml
```

**3. Verify that the services are running:**

``` shell
systemctl status apache2
systemctl status gophish
systemctl status evilginx
```

**4. Access the EvilGophish web interface:**

Use the configured domain and subdomains in your browser. Example: https://admin.evilphisher.com. You can log in to the gophish dashboard using the default password provided in the ansible output or in the output file `/output/ghostwriter/admin_password.txt`.

---

## Notes

- Ensure the target machine has internet access to download dependencies and SSL certificates.
- The fetched admin password will be stored locally in `/output/ghostwriter/admin_password.txt`. Keep it secure.

---

## Playbook Tasks Breakdown

### 1. Install Dependencies
``` yaml
- name: Install dependencies
  apt:
    name: ["apache2", "git", "certbot", "curl", "tmux"]
    state: present
    update_cache: yes
```
Installs the required packages on the system.

### 2. Clone EvilGophish Repository
``` yaml
- name: Clone EvilGophish repo
  git:
    repo: "https://github.com/fin3ss3g0d/evilgophish.git"
    dest: "/opt/evilgophish"
    force: yes
  tags:
    - always

```
Clones the EvilGophish repository into the specified directory.

### 3. Configure Directory Permissions
``` yaml
- name: Set permissions for directory
  file: 
    path: "/opt/evilgophish"
    mode: "0755"
    recurse: yes
```
Sets the appropriate permissions for the directory.

### 4. Stop Apache Service
``` yaml
- name: Stop apache webserver
  service:
    name: apache2
    state: stopped

```
Stops the Apache service temporarily.

### 5. Generate SSL Certificates

#### 5.1 Certbot (Production)
``` yaml
- name: Generate SSl certs with Certbot
  command: certbot certonly --standalone --non-interactive -d {{ root_domain }} -d www.{{ root_domain }} --agree-tos --email someone@smth.com
  args:
    creates: /etc/letsencrypt/live/{{ root_domain }}/fullchain.pem
```
Generates SSL certificates using Certbot for production. This requires open listening ports and a valid domain for verification. Check the certbot documentation for details.

#### 5.1 Self-Signed (Testing)
``` yaml
- name: Generate self-signed SSL certificate (Test)
  command: >
    openssl req -x509 -nodes -days 365 -newkey rsa:2048
    -keyout /etc/ssl/private/evilgophish.key
    -out /etc/ssl/certs/evilgophish.crt
    -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN={{ root_domain }}"
  args:
    creates: /etc/ssl/certs/evilgophish.crt
```
Generates self-signed certificates for testing.

### 6. Run Setup Script
``` yaml
- name: Run setup script
  command: "/opt/evilgophish/setup.sh {{ root_domain }} '{{ subdomains }}' false {{ use_live_feed }} user_id"
  args:
    chdir: /opt/evilgophish
```
Runs the EvilGophish setup script with the specified parameters.

### 7. Deploy Services

#### 7.1 Gophish
``` yaml
- name: Create Service for Gophish
  template:
    src: gophish.service.j2
    dest: /etc/systemd/system/gophish.service
```
This creates the service and uses the following template:

``` ini
[Unit]
Description=Gophish Phishing Framework
After=network.target

[Service]
ExecStart=/opt/evilgophish/gophish/gophish
Restart=always
User=root
StandardOutput=append:/tmp/gophish_output.log
StandardError=append:/tmp/gophish_output.log
WorkingDirectory=/opt/evilgophish/gophish

[Install]
WantedBy=multi-user.target
```

#### 7.2 Evilginx
``` yaml
- name: Create Service for Evilginx
  template:
    src: evilginx.service.j2
    dest: /etc/systemd/system/evilginx.service
```
This creates the Evilginx service and uses the following template:

``` ini
[Unit]
Description=Evilginx3 Reverse Proxy Framework
After=network.target

[Service]
ExecStart=/opt/evilgophish/evilginx -feed -g /opt/evilgophish/gophish/gophish.db
Restart=always
User=root
WorkingDirectory=/opt/evilgophish/evilginx

[Install]
WantedBy=multi-user.target
```

### 8. Configure Reverse Proxy (Apache)

#### 8.1 Test Environment
``` yaml
- name: Configure Apache for reverse proxy (Test)
  template:
    src: apache_reverse_proxy_conf_test.j2
    dest: /etc/apache2/sites-available/evilphish.com.conf
  notify:
    - Restart Apache
```
This configures the Apache webserver with the following Apache config `/templates/apache_reverse_proxy_conf_test.j2`:

The apache_reverse_proxy_conf_test.j2 file is the configuration template for setting up a reverse proxy using Apache. It is designed to forward incoming requests to the appropriate internal services while enabling SSL for secure communication. The configuration supports a main domain ({{ root_domain }}), multiple subdomains ({{ subdomains }}), and an admin panel (admin.{{ root_domain }}).

#### 8.2 Enabling Apache modules
``` yaml
- name: Enable proxy
  command: a2enmod proxy
  tags:
    - always

- name: Enable proxy http
  command: a2enmod proxy_http
  tags:
    - always

- name: Enable SSLEngine
  command: a2enmod ssl
  tags:
    - always

```
These tasks enable the required Apache modules.

#### 8.3 Enabling Apache site
``` yaml
- name: Enable Apache site
  command: a2ensite evilphish.com.conf
  notify: Restart Apache
  tags:
    - always
```
This task enables the Apache site with the configuration in step 8.1.


### 9. Reloading System Daemon
``` yaml
- name: Reload systemd daemon
  command: systemctl daemon-reload
  tags:
    - always

```
This task makes sure the system daemon is reloaded.

### 10. Some More Apache Settings...
``` yaml
- name: Ensure Apache listens on port 3434
  lineinfile:
    path: /etc/apache2/ports.conf
    regexp: '^Listen 3434$'
    line: 'Listen 3434'
    state: present
    insertafter: '^Listen 80$'
  notify:
    - Restart Apache
  become: true
  tags:
    - always
```
By running this task, it is made sure that Apache is listening on Port 3434 for incomming connections to the Gophish dashboard.


### 11. Retrieve Admin Password
``` yaml
- name: Extract admin password from Gophish log
  shell: grep "Please login with the username admin and the password" /tmp/gophish_output.log | awk -F'password ' '{print $2}' | tr -d '"'
  register: admin_password
  become: true
  tags:
    - always

- name: Display admin password
  debug:
    msg: "Gophish Admin password is: {{ admin_password.stdout }}"
  tags:
    - always

- name: Save extracted admin password to file
  copy:
    content: "{{ admin_password.stdout }}"
    dest: /tmp/initial_admin_password.txt
    owner: root
    group: root
    mode: "0644"
  become: true
  tags:
    - always

- name: Fetch the admin password to the local machine
  fetch:
    src: /tmp/initial_admin_password.txt
    dest: ./output/evilgophish/gophish_initial_admin.txt
    flat: yes
  tags:
    - always

```
This task fetches the initial admin password from the remote and writes it to the local machine. It can be found here: `/output/evilgophish/gophish_initial_admin.txt`.

### 12. Deploying the Gophish Config
``` yaml
- name: Stop Gophish process
  shell: sudo pkill -f ./gophish
  ignore_errors: true
  become: true
  tags:
    - always

- name: Deploy Gophish config.json
  template:
    src: config.json.j2
    dest: /opt/evilgophish/gophish/config.json
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: "0644"
  tags:
    - always
```
This task is run to stop the Gophish service and deploy the Gophish configuration file. 

### 13. Enable and Start Evilginx service
``` yaml
- name: Enable and start evilginx service
  systemd:
    name: evilginx
    enabled: yes
    state: started
  tags:
    - always
```
This final task enables and starts the evilginx service on the remote host.

---

## System Configuration

Below is the Apache config file:

``` xml
<VirtualHost *:443>
    ServerName {{ root_domain }}

    SSLEngine on
    SSLProxyEngine on

    SSLProxyVerify none
    SSLProxyCheckPeerCN off
    SSLProxyCheckPeerName off
    
    SSLCertificateFile /etc/ssl/certs/evilgophish.crt
    SSLCertificateKeyFile /etc/ssl/private/evilgophish.key

    ProxyPass / https://localhost:8080/
    ProxyPassReverse / http://localhost:8080/
</VirtualHost>

{% for subdomain in subdomains.split() %}
<VirtualHost *:443>
    ServerName {{ subdomain }}.{{ root_domain }}

    SSLEngine on
    SSLProxyEngine on

    SSLProxyVerify none
    SSLProxyCheckPeerCN off
    SSLProxyCheckPeerName off

    SSLCertificateFile /etc/ssl/certs/evilgophish.crt
    SSLCertificateKeyFile /etc/ssl/private/evilgophish.key

    ProxyPass / http://localhost:8443/
    ProxyPassReverse / http://localhost:8443/
</VirtualHost>

<VirtualHost *:3434>
    ServerName admin.{{ root_domain }}

    SSLEngine on
    SSLProxyEngine on

    SSLProxyVerify none
    SSLProxyCheckPeerCN off
    SSLProxyCheckPeerName off

    SSLCertificateFile /etc/ssl/certs/evilgophish.crt
    SSLCertificateKeyFile /etc/ssl/private/evilgophish.key

    ProxyPass / https://localhost:3333/
    ProxyPassReverse / https://localhost:8080/
</VirtualHost>
{% endfor %}

```
You can adapt this Apache config to ypr specific needs:


**Domain and Subdomains:**
- Modify {{ root_domain }} and {{ subdomains }} in the variables file (main.yaml) to match your deployment requirements.

**Port Adjustments:**
- Change the ports (8080, 8443, 3333) in the proxy configuration if the internal services are running on different ports.

**SSL Certificates:**
- Update the paths for SSLCertificateFile and SSLCertificateKeyFile to use different SSL certificates if required.

**Additional Settings:**
- Adjust ProxyPass and ProxyPassReverse directives to forward requests to different internal endpoints as needed.

### Notes:
- This template dynamically creates configurations for all subdomains listed in the {{ subdomains }} variable.
- The SSL certificate paths (/etc/ssl/certs/evilgophish.crt and /etc/ssl/private/evilgophish.key) can be adjusted to match your environment.