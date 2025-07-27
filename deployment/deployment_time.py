import time
import statistics
import subprocess
import urllib3
from proxmoxer import ProxmoxAPI
import datetime

# Disable SSL warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Configuration ===
proxmox_host = '10.40.10.2'             # Proxmox host IP address
proxmox_node = 'pve01'                    # Node name within Proxmox
containers = [301, 302, 303, 304, 307]     # List of container IDs to be managed
snapshot_name = 'clean'                    # Snapshot name to roll back to
runs = 1                                   # Number of test runs
inventory_file = 'SLRT/inventory.yaml'          # Path to the Ansible inventory file
playbook_file = 'SLRT/deploy-all.yaml'          # Path to the Ansible playbook


# === Authentication ===
proxmox = ProxmoxAPI(
    proxmox_host,
    user='slrt@pam',
    token_name='slrt',
    token_value='d50ef2db-fdc7-42be-b9dd-76a1e3361703',
    verify_ssl=False
)

# List to hold the duration of each Ansible run
runtimes = []

def check_deploy_success(result):
    """
    Checks if the Ansible deployment was completely successful.
    Analyzes the return code and the PLAY RECAP from the Ansible output.

    Args:
        result (subprocess.CompletedProcess): The result object returned by subprocess.run().

    Returns:
        bool: True if the deployment was successful, False otherwise.
    """
    print("\nDeployment Ergebnis:")

     # If Ansible exited with an error, display the output
    if result.returncode != 0:
        print("Fehler: Ansible hat mit einem Fehlercode beendet.")
        print(result.stdout)
    else:
        print("Ansible hat mit Exit-Code 0 beendet.")

    # Extract lines related to PLAY RECAP
    recap_lines = [line for line in result.stdout.splitlines() if "PLAY RECAP" in line or " :" in line]
    all_ok = True

    # Analyze the PLAY RECAP for failed or unreachable hosts
    for line in recap_lines:
        if "failed=" in line or "unreachable=" in line:
            parts = line.strip().split()
            for part in parts:
                if part.startswith("failed=") or part.startswith("unreachable="):
                    key, val = part.split("=")
                    if int(val) != 0:
                        all_ok = False

    # Display summary based on the analysis
    if all_ok:
        print("Alle Hosts/Rollen wurden erfolgreich deployed (kein `failed`, kein `unreachable`).")
    else:
        print("Mindestens ein Host/Rolle hat Fehler oder war unreachable.")
        print("\nRelevante Auszüge aus PLAY RECAP:")
        for line in recap_lines:
            print(line)

    return all_ok


# === Main Deployment Loop ===
for i in range(runs):
    print(f"\nRUN {i+1}/{runs}")

    # --- Snapshot Rollback and Start ---
    for ctid in containers:
        print(f"Restoring snapshot '{snapshot_name}' for CT '{ctid}'")

        # Attempt to stop the container if it is running
        try:
            ct_status = proxmox.nodes(proxmox_node).lxc(ctid).status.current.get()
            if ct_status["status"] == "running":
                print(f"Stopping CT {ctid} before rollback...")
                proxmox.nodes(proxmox_node).lxc(ctid).status.stop.post()
                time.sleep(10)
        except Exception as e:
            print(f"Could not check/stop CT {ctid}: {e}")

        # Roll back the container to the snapshot
        proxmox.nodes(proxmox_node).lxc(ctid).snapshot(snapshot_name).rollback.post()
        print(f"Rolled back CT {ctid} to snapshot '{snapshot_name}'")
        time.sleep(10)

        # Check if the container needs to be started
        ct_status = proxmox.nodes(proxmox_node).lxc(ctid).status.current.get()
        if ct_status["status"] != "running":
            print(f"Starting CT {ctid}")
            proxmox.nodes(proxmox_node).lxc(ctid).status.start.post()
        else:
            print(f"CT {ctid} is already running — skipping start.")
        time.sleep(10)

    # --- Run Ansible Playbook + Measure Time ---
    time.sleep(60) # Wait before running the playbook to allow containers to boot
    print("Running Ansible Playbook...")

    # Start time measurement
    deployment_start = time.time()
    start = time.time()

    # Execute the Ansible Playbook
    result = subprocess.run(
        ["ansible-playbook", "-i", inventory_file, playbook_file, "--ask-vault-pass"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check the success of the deployment
    success = check_deploy_success(result)
    if not success:
        print("Deployment war nicht erfolgreich – bitte prüfen.")
        exit()

    # Measure end time and calculate duration
    end = time.time()
    duration = round(end - start, 2)
    runtimes.append(duration)

    print(f"Run {i+1} done in {duration} seconds")

deployment_end = time.time()
# --- Deployment Statistics ---
print("\nLaufzeit-Statistik:")
print(f"- Runs: {runs}")
print(f"- Einzelzeiten: {runtimes}")
print(f"- Min: {min(runtimes)}s, Max: {max(runtimes)}s, Schnitt: {round(statistics.mean(runtimes), 2)}s")
# Display the start and end time of the entire deployment
zeitpunkt_start = datetime.datetime.fromtimestamp(deployment_start).strftime("%Y-%m-%d %H:%M:%S")
zeitpunkt_ende = datetime.datetime.fromtimestamp(deployment_end).strftime("%Y-%m-%d %H:%M:%S")
print(f"Startzeit: {zeitpunkt_start}, Endzeit: {zeitpunkt_ende}")
