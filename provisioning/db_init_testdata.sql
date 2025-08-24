SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

USE `slrt`;

SET NAMES utf8mb4;



INSERT INTO `environment_users` (`userid`, `username`, `password`, `environmentid`) VALUES
(1,	'root',	'Gi5c4hGSZ4EisLdNJE5E',	1);

INSERT INTO `pve_environment` (`idenvironments`, `name`, `hostname`, `ip`, `port`, `datastore_VMs`, `vbridge`, `datastore_ISO`) VALUES
(1,	'pve',	'pve.local',	'10.40.20.100',	'8006',	'local-lvm',	'vmbr0',	'local');

INSERT INTO `pve_vms` (`vmid`, `name`, `IP_address`, `CIDR`, `Gateway`, `VCPUs`, `DNS-server`, `ssh_key`, `password`, `username`, `RAM`, `Disksize`, `environmentid`) VALUES
(100,	'test-vm',	'10.40.20.101',	24,	'10.40.20.1',	1,	'1.1.1.1',	'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMjca0fXkgJM7h+ecRJW50S9uxZXRtrh0C8LPS64BQlOtrMKk5DhEgXkOyfZss8gsYE0maJUfK6jwK4oS0vRHIMCbkXM9fM571fuIFgV1XRCC/t5Arj/MRfxU8pMrxRBaaOKchqR+9rodGtPeTgZihSbLTZpV1Zmka1nTCCCA4tWPIOJyXW3jUatSVaByM+n00WbH1qJ8br0G9uAcEuIlJqBoobXveskNU4JPY+WkGgEPXVkaLuAnA8a5/wlE+nPY0+settPC6omafD7Tl1zD7tH0Vr6d6NHrWGD4He8+rmx0/z5hVMaOFVrKifuXM+dIClgVaG1jRH4RDbQEKOrVT',	'Dskvh8GVPprNEtgIGp2O0fYSgdzEkhxegeeym0aWt2M',	'3WVsvmKBFOoe9Ofx3C3cbkDbNDrNmM0p47a8y46fWRw',	512,	10,	1);