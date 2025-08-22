
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

INSERT INTO `pve_vms` (`vmid`, `name`, `IP_address`, `Gateway`, `VCPUs`, `DNS-server`, `ssh_key`, `username`, `RAM`, `Disksize`, `environmentid`) VALUES
(1,	'test-vm',	'10.40.20.101',	'10.40.20.1',	1,	'1.1.1.1',	'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGRZjFI7E3Mocwk/Fp70mQMjcy0wtPBJz15QWcPiPqMp seel3@nerv',	'slrt',	512,	10,	1);
