# 🚀 AWS Automated Cloud Dev Environment (Cost-Optimized)

A fully automated, cost-optimized Cloud Development Environment (Cloud IDE) built with **Python, Boto3, and AWS EC2 Spot Instances**. This internal tool provisions a powerful ephemeral remote workspace, attaches persistent storage, configures local SSH, and launches VS Code automatically—all with a single click from a custom Windows GUI.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![AWS Boto3](https://img.shields.io/badge/AWS-Boto3-FF9900.svg)
![Cost Optimization](https://img.shields.io/badge/Cost_Optimization-Spot_Instances-27AE60.svg)

## 💡 The Problem & The Solution

**The Problem:** Running powerful On-Demand EC2 instances for development is expensive. Furthermore, assigning an Elastic IP to maintain a static connection now incurs an hourly charge ($0.005/hr) regardless of instance state, adding unnecessary overhead for a development environment.

**The Solution:**
This project utilizes a **Stateless Compute / Persistent Storage** architecture. 
- **Compute:** Uses highly discounted **EC2 Spot Instances** (`c5a.xlarge`), saving up to 70-90% on compute costs.
- **Storage:** Keeps all project data safe on a detached **persistent 20GB EBS Volume**.
- **Networking:** Eliminates the need for Elastic IPs. The Python script dynamically fetches the ephemeral Public IP upon launch and updates the local `~/.ssh/config` file instantly.

## 🏗️ Architecture & Workflow

When the "START DEV" button is clicked on the GUI, the script triggers the following workflow:
<!-- display architecture diagram from ./architecture.png -->
![Architecture Illustration](./architecture.png)

✨ Key Features
Custom GUI Dashboard: Built with customtkinter for a sleek, dark-mode interface to manage the environment without logging into the AWS Console.

Automated Spot Provisioning: Spawns instances from an AWS Launch Template with predefined security groups and configurations.

Dynamic Volume Attachment: Automatically finds and attaches your persistent EBS volume to the newly spawned Spot Instance.

Auto-Mounting (Bash User Data): The EC2 instance is pre-configured via User Data to automatically format (if new) and mount the EBS volume to /workspace upon boot.

Local SSH Automation: Automatically rewrites the Windows ~/.ssh/config file with the instance's new ephemeral Public IP.

Detached VS Code Launch: Programmatically launches VS Code directly into the Remote SSH workspace using subprocess breakaway techniques, completely detached from the dashboard process.

One-Click Termination: A "STOP DEV" button instantly terminates the Spot instance to halt billing, safely leaving the detached EBS volume intact for the next session.

🛠️ Tech Stack & Prerequisites
Python 3.1x (Libraries: boto3, customtkinter)

AWS CLI configured with appropriate IAM permissions (ec2:RunInstances, ec2:AttachVolume, ec2:Describe*, ec2:TerminateInstances).

AWS Infrastructure setup:

An existing unattached EBS Volume (e.g., 20GB gp3).

An AWS Launch Template configured to request Spot Instances.

VS Code with the "Remote - SSH" extension installed.

📝 AWS User Data Script (Instance Preparation)
To make this work seamlessly, the Launch Template includes the following bash script to ensure the persistent volume is mounted automatically when the Spot instance boots:
```bash
#!/bin/bash
# 1. Create the mount point directory
mkdir -p /workspace

# 2. Add the volume to /etc/fstab using its UUID so it survives reboots
# (Replace UUID with your actual volume UUID)
if ! grep -q "YOUR-VOLUME-UUID-HERE" /etc/fstab; then
  echo "UUID=YOUR-VOLUME-UUID-HERE  /workspace  ext4  defaults,nofail  0  2" >> /etc/fstab
fi

systemctl daemon-reload
chown -R ubuntu:ubuntu /workspace

# 3. Add auto-mount and directory change to bashrc for SSH sessions
if ! grep -q "sudo mount -a" /home/ubuntu/.bashrc; then
  echo "sudo mount -a 2>/dev/null" >> /home/ubuntu/.bashrc
  echo "cd /workspace" >> /home/ubuntu/.bashrc
fi
```
🚀 Installation & Usage
Clone this repository.

Install requirements: pip install boto3 customtkinter

Update the VOLUME_ID and TEMPLATE_NAME variables in the scripts with your AWS resource IDs.

Run python ExpoCloud-Dashboard.py to open the GUI.

(Optional) Convert to a standalone executable using auto-py-to-exe for a true desktop app experience.

Author: Ahmed Abd Elmohsen

Portfolio: ([ahmed-abd-elmohsen.tech](https://www.ahmed-abd-elmohsen.tech))

LinkedIn: Connect with me ([LinkedIn](https://www.linkedin.com/in/dev-ahmed-abdelmohsen/))