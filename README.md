# SLRT
SLRT (Streamlined Red Teaming) is a tool that automates the setup of red teaming environments using Configuration as Code. It enables security teams to quickly and efficiently configure and run attack simulations without manual setup steps.

SLRT relies on Ansible to deploy and configure red team tools across multiple systems. Ansible's playbooks and roles are used to define configurations, manage dependencies, and automate the deployment process. This approach ensures consistency and simplifies the setup of complex environments. It also allows to create new roles for custom Red Team tools with ease.

Currently, SLRT supports the following Red Teaming Components:
- Sliver C2 Server
- Nginx Redirector
- VeilDrop Payload Server
- Ghostwriter Red Team Collaboration Tool
- EvilGoPhish

For instructions on how to get started, please use the following link to [get started](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Getting-Started)!