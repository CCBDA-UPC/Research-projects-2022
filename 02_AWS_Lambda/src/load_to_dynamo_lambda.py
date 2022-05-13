import boto3

def lambda_handler(event, context):
    topic = event['responsePayload']['label'][1:]
    url = event['responsePayload']['url']
    
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('topics-table')
    
    table.update_item(
        Key={
            'topic': topic
        },
        UpdateExpression='SET #URLs = list_append(if_not_exists(#URLs, :empty_list), :t)' ,
        ExpressionAttributeNames={
            '#URLs': 'URLs',
        },
        ExpressionAttributeValues={
            ':t': [url],
            ':empty_list': []
        }
    )
    return {
        'statusCode': 200
        
    }
