# Redirector Deployment

This page details the Ansible playbook for deploying the Redirector Service. The playbook configures Nginx for conditional redirections based on specific criteria and ensures the Redirector service is operational.

For detailed information about Nginx, please refere to the [official documentation](https://nginx.org/en/docs/).

## Required Variables

The following variables must be set in the `vars/main.yaml` file for successful deployment. Customize these according to your environment:

```yaml
# Hostname of the redirector
redirector_hostname: "slrt_redirector.com"

# Target backend server details
backend_host: "192.168.0.207"
backend_protocol: "https"

# Redirection conditions
user_agent: "SpecialAgent"
url_token: "secretkey123"

# Path to the legit website template
legit_site_template_path: "/var/www/html/templates/legit_site.html"
```

## Deployment Instructions

**1. Customize the `vars/main.yaml` file with your specific configurations as described above.**

**2. Run the Ansible playbook:**

```shell
ansible-playbook -i <inventory_file> deploy_redirector.yaml
```

**3. Verify the Redirector service is running:**
Connect to your remote machine and ensure Nginx is configured correctly and running:

```shell
systemctl status nginx
```

## Notes

- Ensure the target machine has internet access to install dependencies.
- Verify the Nginx configuration syntax before restarting the service:
  ```shell
  nginx -t
  ```

## Playbook Tasks Breakdown

### 1. Install Dependencies
```yaml
- name: Install dependencies
  apt:
    name: nginx
    state: present
    update_cache: yes
```

This task installs Nginx on the target system to handle HTTP redirections.

### 2. Deploy Legit Site
```yaml
- name: Deploy legit site
  copy:
    src: files/legit_site.html
    dest: "{{ legit_site_template_path }}"
    owner: www-data
    group: www-data
    mode: "0644"
```

This task deploys the legitimate website template to the specified location.

### 3. Configure Nginx Redirector
```yaml
- name: Deploy Nginx configuration
  template:
    src: templates/nginx_redirector.conf.j2
    dest: /etc/nginx/sites-available/redirector.conf
    owner: root
    group: root
    mode: "0644"
```

Deploys the Nginx configuration template with the specified redirection logic.

### 4. Enable Redirector Configuration
```yaml
- name: Enable Nginx redirector configuration
  file:
    src: /etc/nginx/sites-available/redirector.conf
    dest: /etc/nginx/sites-enabled/redirector.conf
    state: link
```

Enables the Nginx configuration by creating a symbolic link in the `sites-enabled` directory.

### 5. Restart Nginx
```yaml
- name: Restart Nginx service
  systemd:
    name: nginx
    state: restarted
    enabled: true
```

Restarts the Nginx service to apply the changes and ensures it starts on system boot.

## Nginx Configuration Template

Below is the Nginx configuration template (`nginx_redirector.conf.j2`):

```nginx
server {
    listen 80;
    server_name {{ redirector_hostname }};

    set $redir 0;

    # Condition 1: Check User-Agent
    if ($http_user_agent ~* "{{ user_agent }}") {
        set $redir 1;
    }

    # Condition 2: Check token in URL
    if ($arg_token = "{{ url_token }}") {
        set $redir 1;
    }

    location / {
        # Redirect to backend if any condition is met
        if ($redir = 1) {
            return 302 {{ backend_protocol }}://{{ backend_host }}/;
        }

        # Serve the legit site if no condition is met
        root /var/www/html/templates;
        index legit_site.html;
    }
}
```

This template defines the redirection logic and ensures the legitimate page is displayed when no conditions are met.

## Legitimate Website Template

Below is the content of the legitimate website template (`legit_site.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome to our Website!</h1>
    <p>This is a legitimate page, nothing shady to see here.</p>
</body>
</html>
```

This simple HTML page is served when none of the redirection conditions are met.