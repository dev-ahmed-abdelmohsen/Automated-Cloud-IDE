import boto3

def get_ec2_state(instance_name="ExpoDev"):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [instance_name]},
                {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
            ]
        )
        if response['Reservations']:
            instances = [i for r in response['Reservations'] for i in r['Instances']]
            instances.sort(key=lambda x: x.get('LaunchTime', ''), reverse=True)
            latest = instances[0]
            
            state = latest['State']['Name'].upper()
            ip = latest.get('PublicIpAddress', 'No IP Yet')
            return f"State: {state} | IP: {ip}"
        return "NOT FOUND"
    except Exception as e:
        return f"Error: {str(e)[:30]}..."

def get_ebs_state(volume_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_volumes(VolumeIds=[volume_id])
        if response['Volumes']:
            state = response['Volumes'][0]['State'].upper()
            return f"State: {state}"
        return "NOT FOUND"
    except Exception as e:
        return f"Error: {str(e)[:30]}..."