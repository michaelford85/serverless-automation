import json
import boto3

def lambda_handler(event, context):
    print(event['vpc_name'])
    thevpc_name = event['vpc_name']
    print(thevpc_name)
    ec2 = boto3.resource('ec2', region_name='us-east-1')

    # create VPC
    vpc = ec2.create_vpc(CidrBlock='10.1.0.0/16')

    # assign a name to our VPC

    # vpc.create_tags(Tags=[{"Key": "Name", "Value": "my_vpc"}])
    vpc.create_tags(Tags=[{"Key": "Name", "Value": thevpc_name}])
    vpc.wait_until_available()

    # create then attach internet gateway
    ig_name = event['vpc_name'] + "_ig"
    ig = ec2.create_internet_gateway()
    ig.create_tags(Tags=[{"Key": "Name", "Value": ig_name}])
    vpc.attach_internet_gateway(InternetGatewayId=ig.id)
    print(ig.id)

    # create a route table and a public route
    route_table = vpc.create_route_table()
    route = route_table.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=ig.id
    )
    print(route_table.id)

    # create subnet
    subnet = ec2.create_subnet(CidrBlock='10.1.1.0/24', VpcId=vpc.id)
    print(subnet.id)

    # associate the route table with the subnet
    route_table.associate_with_subnet(SubnetId=subnet.id)

    # Create sec group
    sg_name = event['vpc_name'] + "_sg"
    sec_group = ec2.create_security_group(
        GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
    sec_group.authorize_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='icmp',
        FromPort=-1,
        ToPort=-1
    )
    sec_group.create_tags(Tags=[{"Key": "Name", "Value": sg_name}])
    print(sec_group.id)

    print("creating ec2 instances")
    instance_name = event['vpc_name'] + "_instance"
    thenum_instances = int(event['num_instances'])
    the_instances = ec2.create_instances(
        ImageId = "ami-096fda3c22c1c990a",
        MinCount = thenum_instances,
        MaxCount = thenum_instances,
        # KeyName = instance['key'],
        # SecurityGroupIds = sec_group.id,
        SecurityGroupIds=[
        sec_group.id,
        ],
        InstanceType = "t2.small",
        SubnetId = subnet.id,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    },
                ]
            }
        ]
    )


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
