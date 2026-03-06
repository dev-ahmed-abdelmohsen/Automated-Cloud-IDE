import boto3

REGION = 'us-east-1'
INSTANCE_NAME = 'ExpoDev'

print(" Stopping AWS Automated Dev Environment...")

ec2 = boto3.client('ec2', region_name=REGION)

response = ec2.describe_instances(
    Filters=[
        {'Name': 'tag:Name', 'Values': [INSTANCE_NAME]},
        {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
    ]
)

instances = [i for r in response['Reservations'] for i in r['Instances']]

if not instances:
    print(f" No running instances found with name '{INSTANCE_NAME}'. You are safe from billing!")
else:
    instance_id = instances[0]['InstanceId']
    print(f" Found running instance: {instance_id}")
    
    print(" Terminating instance to stop billing...")
    ec2.terminate_instances(InstanceIds=[instance_id])
    
    print(" Termination request sent! The 20GB volume will safely detach itself.")
    print(" Billing stopped. See you next time, Ahmed!")