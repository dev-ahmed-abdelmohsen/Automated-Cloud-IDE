import boto3
import time
import os
import subprocess
import sys
import shutil

REGION = 'us-east-1'
TEMPLATE_NAME = 'ExpoDevTemplate'
INSTANCE_NAME = 'ExpoDev'
VOLUME_ID = 'vol-03e00b448d1d656f9' 
SSH_HOST = 'awsexpo'

def launch_vscode_detached(folder_uri: str) -> subprocess.Popen | None:
    code_cmd = shutil.which("code")
    if not code_cmd:
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\bin\code",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                code_cmd = p
                break

    if not code_cmd:
        print(" ERROR: Could not find VS Code executable.")
        return None

    ext = os.path.splitext(code_cmd)[1].lower()
    if ext in ('.cmd', '.bat'):
        args = ['cmd', '/c', code_cmd, '--folder-uri', folder_uri]
        use_shell = False
    else:
        args = [code_cmd, '--folder-uri', folder_uri]
        use_shell = False

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 1  

    flags = (
        0x00000008 |         
        0x00000200 |         
        0x01000000          
    )

    try:
        process = subprocess.Popen(
            args,
            startupinfo=startupinfo,
            creationflags=flags,
            close_fds=True,            
            shell=use_shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        return process
    except Exception as e:
        print(f" Failed to launch VS Code: {e}")
        return None

if __name__ == "__main__":
    print(" Starting AWS Automated Dev Environment...")

    ec2 = boto3.client('ec2', region_name=REGION)

    print(" Checking Volume status...")
    try:
        vol_response = ec2.describe_volumes(VolumeIds=[VOLUME_ID])
        vol_state = vol_response['Volumes'][0]['State']
        if vol_state != 'available':
            print(f" ERROR: Volume {VOLUME_ID} is currently '{vol_state}'. It must be 'available' before starting.")
            sys.exit(1)
        print(" Volume is available and ready.")
    except Exception as e:
        print(f" ERROR: Could not read volume status. Details: {e}")
        sys.exit(1)

    print(" Checking for existing instances...")
    instances_response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [INSTANCE_NAME]},
            {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'shutting-down', 'stopping']}
        ]
    )
    active_instances = [i for r in instances_response['Reservations'] for i in r['Instances']]

    if active_instances:
        state = active_instances[0]['State']['Name']
        print(f" ERROR: Found an instance named '{INSTANCE_NAME}' currently in '{state}' state.")
        sys.exit(1)
    print(" No conflicting instances found. Path is clear!")

    print(f" Launching Spot Instance from template '{TEMPLATE_NAME}'...")
    response = ec2.run_instances(
        LaunchTemplate={'LaunchTemplateName': TEMPLATE_NAME, 'Version': '$Default'},
        MinCount=1, MaxCount=1
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f" Waiting for instance {instance_id} to be running...")

    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    instance_info = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f" Instance is UP! Public IP: {public_ip}")

    print(f" Attaching 20GB Volume ({VOLUME_ID})...")
    ec2.attach_volume(VolumeId=VOLUME_ID, InstanceId=instance_id, Device='/dev/sdf')

    print(" Updating ~/.ssh/config...")
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    with open(ssh_config_path, 'r') as file:
        lines = file.readlines()
    with open(ssh_config_path, 'w') as file:
        in_target_host = False
        for line in lines:
            if line.strip().startswith(f"Host {SSH_HOST}"):
                in_target_host = True
                file.write(line)
            elif in_target_host and line.strip().startswith("HostName"):
                file.write(f"    HostName {public_ip}\n")
                in_target_host = False 
            else:
                file.write(line)
    print(" SSH config updated perfectly!")

    print(" Waiting 15 seconds for Linux boot and Drive Auto-Mount...")
    time.sleep(15)

    print(" Launching VS Code directly to /workspace...")
    folder_uri = f"vscode-remote://ssh-remote+{SSH_HOST}/workspace"
    launch_vscode_detached(folder_uri)

    print(" All done! Happy Coding, Ahmed!")