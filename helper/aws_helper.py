import boto3, time
from botocore.exceptions import ClientError
from interface import Interface, implements


def get_value(dynamo_value):
    datatype_key = list(dynamo_value)[0]
    value = dynamo_value[datatype_key]

    if datatype_key == 'M':
        for item_key in value.keys():
            value.update({item_key : get_value(value[item_key])})

    return value

def convert_dynamojson_to_json(item):
    for item_key in item.keys():
        item.update({item_key : get_value(item[item_key])})
    return item

class AWS(Interface):
    def __init__(self):
        """
        Initialize AWS Service Client
        """
        pass

    def fetch_records(self,query):
        """
        Fetch Records from the AWS Service
        """
        pass
    
class DynamoDB(implements(AWS)):
    """ DynamoDB Data Types
        String: 'S'
        Number: 'N'
        Binary: 'B'
        String Set: 'SS'
        Number Set: 'NS'
        Binary Set: 'BS'
        Map: 'M'
        List: 'L'
        Null: 'NULL'
        Boolean: 'BOOL'
    """

    def __init__(self):
        self.client = boto3.client('dynamodb', region_name='us-east-2')

    def fetch_records(self,query):
        response = self.client.query(
            TableName=query['table_name'],
            AttributesToGet=query['attributes_to_get'],
            KeyConditions={
                list(query['key_condition'])[0] : {
                    'AttributeValueList': [
                        query['key_condition'][list(query['key_condition'])[0]]
                    ],
                    'ComparisonOperator' : 'EQ'
                }
            }

        )
        if response['Count'] == 1:
            response = response['Items']
            response = convert_dynamojson_to_json(response[0])
        elif response['Count'] > 1:
            response = response['Items']
            for index in range(len(response)):
                response[index] = convert_dynamojson_to_json(response[index])
        else:
            response = response['Items']
        return response

class StepFunctions(implements(AWS)):
    def __init__(self):
        self.client = boto3.client('stepfunctions', region_name='us-east-2')
        
    def fetch_records(self,query):
        try:
            response = self.client.describe_execution(
                executionArn = query
            )
            return response
        except ClientError as e:
            response = {'status' : e.response['Error']['Code'], 'name' : 'Step Function Error'}
            return response

class CloudWatchInsights(implements(AWS)):
    def __init__(self):
        self.client = boto3.client('logs', region_name='us-east-2')
        
    def fetch_records(self,query):
        try:
            response = self.client.start_query(
                logGroupName=query['logGroupName'],
                startTime=query['startTime'],
                endTime=query['endTime'],
                queryString= query['queryString'],
                limit=10
            )
            time.sleep(5)
            query_id=response['queryId']
            response = self.client.get_query_results(
                queryId=query_id
            )
            return response
        except ClientError as e:
            response = {'status' : e.response['Error']['Code'], 'name' : 'Step Function Error'}
            return response 