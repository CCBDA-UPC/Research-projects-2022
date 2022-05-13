import json
import requests

def sample_classify_text(text_content):
    key = 'AIzaSyDbdo62MbGPxOwexuqZN3RLvaGUJyMqbtY'
    url = f'https://language.googleapis.com/v1/documents:classifyText?key={key}'
    data = { 
       "document": {
          "type":"PLAIN_TEXT",
          "content": text_content
       }
    }
    response = requests.post(url, headers={"Content-Type" : "application/json"}, data=json.dumps(data))

    try:
        category = json.loads(response.content.decode('utf-8'))['categories'][0]
        print(u"Category name: {}".format(category['name']))
        print(u"Confidence: {}".format(category['confidence']))
        return category['name']
    except:
        return 'unknown'
    

def lambda_handler(event, context):
    events = json.loads(event['responsePayload'])

    request_data = events['content']
    url = events['url']
    label = sample_classify_text(request_data)

    return {
        'statusCode': 200,
        'label': label,
        'url': url
    }