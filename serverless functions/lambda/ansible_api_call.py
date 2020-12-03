import json
import boto3
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import base64

def lambda_handler(event, context):
    # print(json.dumps(event))

    secret_name = "ansibleserver.com-admin"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    # print(secret['username'])

    credential = secret['username'] + ":" + secret['password']

    encodedBytes = base64.b64encode(credential.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    # print(encodedStr)

    # Send API request to Ansible Tower
    req = Request("https://ansibleserver.com/api/v2/job_templates/32/launch/", headers={"Content-Type": "application/json", "Authorization": "Basic {}".format(encodedStr)}, method='POST')
    try:
        response = urlopen(req)
        response.read()
        print("API Call Sent to Ansible Tower")
    except HTTPError as e:
        print('Request failed: {e.code} {e.reason}')
    except URLError as e:
        print('Request failed: {e.code} {e.reason}')

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
