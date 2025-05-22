If you want to add your own roles to the project, follow these steps to create and integrate a new role.

## Creating Your Own Roles

If you want to add your own roles or red team components to the project, follow the steps below to create and integrate a new role.
You can also find a template role directory in the source directory of this project, which you can adapt to your needs.

1. **Create the Role Structure**  
   Use the following directory structure as a template for your role. Replace `your_service` with the name of your role:

   ```
   roles/
   └── your_service/
       ├── tasks/
       │   └── main.yaml
       ├── handlers/
       │   └── main.yaml
       ├── vars/
       │   └── main.yaml
       └── templates/
           └── example_config.j2
   ```

2. **Define Tasks**  
   In `roles/your_service/tasks/main.yaml`, define the tasks required to configure your service. Example:

   ```yaml
   ---
   - name: Install necessary packages
     apt:
       name: "{{ your_service_packages }}"
       state: present
     become: yes

   - name: Deploy configuration file
     template:
       src: your_config.j2
       dest: /opt/your_service/config.yaml
       owner: root
       group: root
       mode: '0644'
   ```

3. **Set Default Variables**  
   Use `roles/your_service/defaults/main.yaml` to set default variables for your role:

   ```yaml
   your_service_packages:
     - nginx
     - curl
     - python3
   ```

4. **Define Role Variables**  
   Customize variables in `roles/your_service/vars/main.yaml`. These will override defaults if specified:

   ```yaml
   ---
   your_service_config_path: /opt/your_service/config.yaml
   ```

5. **Add Templates or Files**  
   Place configuration templates in the `templates/` directory. For example, `roles/your_service/templates/example_config.j2`:

   ```yaml
   server:
     host: "{{ ansible_host }}"
     port: 8080
   logging:
     level: info
   ```

6. **Include Handlers**  
   In `roles/your_service/handlers/main.yaml`, define any handlers for tasks that require reloading services:

   ```yaml
   ---
   - name: Restart your_service
     service:
       name: your_service
       state: restarted
   ```

7. **Add your Host to the Inventory**
   The next step is to define your remote machine in the `inventory.yaml`. For Ansible to work, you need to specify the required connection details like shown below:

    ``` yaml
    all:
      hosts:
        your_service_host:
          ansible_host: 192.168.0.67
          ansible_user: slrt
          ansible_ssh_private_key_file: /home/<local_user>/.ssh/slrt_deployment_id
          ansible_become: true
          ansible_sudo_pass: <password>
    ```

8. **Integrate the Role in the Playbook**  
   Add the role to your playbook (`deployment-your_service.yaml`):

   ```yaml
   ---
   - hosts: your_service_host
     roles:
       - your_service
   ```

9. **Test the Role**  
   Run your playbook to ensure your new role is working as expected:
   ```bash
   ansible-playbook -i inventory.yaml deployment-your_service.yaml
   ```