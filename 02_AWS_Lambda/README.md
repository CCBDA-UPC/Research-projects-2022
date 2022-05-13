
# CCBDA – Research Project 2022
## :beginner: About
The goal of this project is to illustrate the steps to create an automatic file classification system within an S3 bucket.

To achieve this, Lambda functions are used that extract the contents of a file as soon as it is uploaded to an S3 bucket and to classify it.
After classification, the URI of the file in the S3 bucket will be associated to the label and stored in an Amazon DynamoDB table.

In this specific implementation, we will use the Google Cloud API to categorize `.txt` documents. 

### Overview of the tasks
1. Creation of an S3 bucket to store the documents to be classified.
2. Definition of a Lambda function to react to uploads of documents in the S3 bucket.
3. Creation of a Lambda function that calls the Google Cloud API to perform the categorization of the document.
4. Creation of a DynamoDB table that will contain the categorization of each file that gets uploaded to the S3 bucket.
5. Implementation of an endpoint to access the content of the DynamoDB table from a URL, without the need of being logged as the "root-user", for instance, from the AWS Console. 

## :star2: Authors

**Creators**
- [![VINCENZO RICCIO](https://i.stack.imgur.com/gVE0j.png) VINCENZO RICCIO](https://www.linkedin.com/in/viriccio) <vincenzo.riccio@estudiantat.upc.edu>
- [![EMANUELE TRIUZZI](https://i.stack.imgur.com/gVE0j.png) EMANUELE TRIUZZI](https://www.linkedin.com/in/etriuzzi) <emanuele.triuzzi@estudiantat.upc.edu>

**Validators**
- [![POL GARCIA RECASENS](https://i.stack.imgur.com/gVE0j.png) POL GARCIA RECASENS](https://www.linkedin.com/in/pol-garcia-recasens-854438168) <pol.garcia.recasens@estudiantat.upc.edu>
- [![RODRIGO ARIAN HUAPAYA](https://i.stack.imgur.com/gVE0j.png) RODRIGO ARIAN HUAPAYA SIERRA](https://www.linkedin.com/in/arian-huapaya) <rodrigo.arian.huapaya@estudiantat.upc.edu>


## :file_cabinet: Task 1 – Create an S3 bucket
Amazon Simple Storage Service (Amazon S3) is an object storage service that offers scalability, data availability, security, and performance.
The first step for this project is to create an S3 bucket which will contain the files that must be classified. The steps required to do so are:

1. Go to the [Amazon S3 console](https://s3.console.aws.amazon.com/s3/buckets?region=eu-west-1). From this page it's possible to see the buckets (file containers) currently available in the logged account.

<img width="1383" alt="Screenshot 2022-05-07 at 12 37 05" src="https://user-images.githubusercontent.com/60050299/167250807-1c926338-76b1-4b75-945a-87d96ce597c9.png">

2. From that page, create a new bucket by clicking on the "Create bucket" button or by clicking [this link](https://s3.console.aws.amazon.com/s3/bucket/create?region=eu-west-1), beware that these URLs specify as region `eu-west-1`, Europe (Ireland).
In this page, fill the creation form fields with these parameters:
    - **Bucket name**: it can be whatever, but it has to be unique. For the following steps, the example bucket name is "ccbda-databucket".
    - **Region**: as before, it will be `eu-west-1`, but it can be any, based on the location
    - **Object Ownership**: Select `ACLs disabled`, this way all objects in this bucket are owned by the account creating the bucket.
    - **Block Public Access settings for this bucket**: check the `Block all public access` checkbox, since for this tutorial we are using a private bucket and public access is not needed.
    - Keep the other options in their default state, add tags for tracking purposes (e.g., `Project: ccbda`), and click on the **Create bucket** button.

![img](images/task1/bucketCreated.png)

From now on, files can be uploaded and stored in the just created bucket.

## :zap: Task 2 – Create a Lambda function triggered to file uploads on the S3 bucket
The goal of this task is to expand the behavior of a file upload on an S3 bucket by triggering a procedure that performs the classification of the file uploaded.
AWS Lambda allows to run code without provisioning or managing infrastructure. The idea is to simply write and upload the code and specify which event triggers the execution of that code.
In order to perform classification of the files uploaded, the code must be executed each time a file is uploaded to the bucket.

To do so, we create and link a custom Lambda function to the event of uploading a file to our S3 bucket:
1. Open the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1) and press on the "Create function" button
<img width="1010" alt="Screenshot 2022-05-09 at 11 53 24" src="https://user-images.githubusercontent.com/60050299/167386079-10656461-9e93-4915-9bad-bb8258f1c180.png">

2. Select "Use a blueprint" as option to create the Lambda function and select "s3-get-object-python" as blueprint.
![img](images/task2/lambdaFromBlueprint.png)

3. Click on the "Configure" button on the bottom of the page to continue with the creation of the Lambda function. 
    In this page, fill the creation form fields with these parameters. 
    In the **Basic information** section specify:
    -  **Function name**: it can be whatever and it has not to be unique. For the following steps, the example name is "s3-upload-handler".
    -  **Execution role**: it specifies the role that defines the permissions of your function. It's possible to create a new role with the minimum number of permissions by selecting the option "Create a new role from AWS policy templates", alternatively, it is possible to choose an already existent role. 
    -  **Role name**: choose a name for the role (e.g., "s3-upload-handler-role") 
    -  **Policy template**: add the "Amazon S3 object read-only permissions" policy template (the only required for our goal). You can customize permissions if you want to increase the functionality of the function.
    In the **S3 trigger** section specify:
    - **Bucket**: choose the s3 bucket created before (for our example, "ccbda-datastorage") 
    - **Event type**: be sure that "All object create events" is selected as option in order to react to every kind of file upload on the bucket
    
The lambda configuration screen should look like the picture below:
![img](images/task2/lambdaConfig.png)

4. Leave the other sections' fields as they are and click on "Create function".

After clicking the button, you will be redirected on the following page of the AWS Lambda console:
![img](images/task2/lambdaCreated.png)
If not, from [this link](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1) click "Functions", and then click the Lambda function's link `s3-upload-handler`.

Enter the **Code** section of this Lambda overview page and replace the default `lambda_handler` function with the following one:
```python
def lambda_handler(event, context):
   # Get the name of the bucket and of the file which triggered the event from the request
   bucket = event['Records'][0]['s3']['bucket']['name']
   key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
   url = "https://"+bucket+".s3.eu-west-1.amazonaws.com/"+key
   try:
      # Get the file which triggered the event
      response = s3.get_object(Bucket=bucket, Key=key)
      contentType = response['ContentType']
      if contentType == "text/plain":
         body = response['Body']
         content = body.read().decode("utf-8")
         print("Content of the file is:\n", content)
         return json.dumps({"content":content, "url":url})
      else:
         print("FILE NOT SUPPORTED")
         raise Exception("FILE NOT SUPPORTED")
   except Exception as e:
      print(e)
      print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
      raise e
```

As you see, for a simple `.txt` file the filetype is "text/plain", which allows to retrieve its content simply with the command `body.read().decode("utf-8")`, which reads the body of the request and decode it. 
After updating the code as described before, deploy it with the "Deploy" button, as shown in the following picture.

<img width="1248" alt="Screenshot 2022-05-09 at 13 23 59" src="https://user-images.githubusercontent.com/60050299/167400343-3039af05-1d1e-483a-b163-e58f11e7e32e.png">

### Test the workflow up to this task
Now it's time to test the workflow we obtained so far.
1. Upload a simple text file (e.g., a `.txt`) to the S3 bucket created in Task 1. To do so, we will use the [AWS S3 Console](https://s3.console.aws.amazon.com/s3/buckets?region=eu-west-1), but it's possible to upload the document also by [synchronizing a folder on your computer with the S3 bucket](https://gmusumeci.medium.com/how-to-sync-aws-s3-buckets-with-local-folders-96bf5fe107bc), or also by [using the AWS CLI](https://codingsight.com/upload-files-to-aws-s3-with-the-aws-cli/). 
2. In the AWS S3 Console, you will see a page as the following from which you can click "Upload", and then "Upload file", to insert the `.txt` file in the bucket, confirm with the "Upload" button:

    ![img](images/task2/s3Upload.png)
   
    *Pay attention to the file type: it must be "text/plain" in order to be supported. You can also use the [sample@@@@@file](http://www.google.com) provided with this tutorial.*
3. Go to the [AWS Lambda console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions) and, inside our function interface, open the **Monitor** section of the Lambda function and click on "View logs in CloudWatch"
4. Select the latest log stream and you will see the result of the lambda execution
   
   <img width="1075" alt="Screenshot 2022-05-09 at 13 42 45" src="https://user-images.githubusercontent.com/60050299/167403042-66a38ec3-5297-44b7-a3e2-3409582b6ed3.png">
   
   ![img](images/task2/lambdaExecuted.png)

This ensures that the upload event on the S3 bucket triggers the Lambda function just created is working correctly and that the file is read properly.

We can so proceed with the tutorial by implementing the API call to categorize the document.

## :cloud: Task 3 – Use the Google Cloud API to categorize the document
With this task, we will implement a Lambda function that calls the Google Cloud API to categorize the document uploaded on the S3 bucket. 

First, you have to sign up to Google Cloud, where you can request a credit of 300$ to spend on the services they offer. Use the [Google Cloud Console](https://console.cloud.google.com/) to sign up, then set up the Natural Language API following the [official Quick-Start Guide](https://cloud.google.com/natural-language/docs/setup).

Get your API key from the Google Cloud Console and then move again to the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1) to create the Lambda function in charge of classifying the document uploaded to the S3 bucket.

To do so, it is needed to:

1. Create `.zip` file containing the `request` package as it is not included in the standard AWS libraries. It will be used to add a layer to the lambda function with the needed module. To do so, we first download the package into a folder and compress it as a zip file. 

```bash
mkdir python/
python3.8 -m pip install requests -t python/
zip -r package.zip python/
```

Alternatively, it's possible to download the zipped file `package.zip` from this repository, which contains the `requests` package in its `2.27.1` version.
    
2. Go to the [AWS Lambda console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/layers) in the Layer page and click on the "Create layer" button.

<img width="1248" alt="Screenshot 2022-05-09 at 17 21 07" src="https://user-images.githubusercontent.com/60050299/167442696-3557f479-2ea0-48eb-b3ba-bc8993f9839c.png">


3. Fill the form as in the picture below, specifying:
    - **Name**: "requests", since the `.zip` file contains this package
    - **Upload a .zip file** option. Upload the just created/downloaded `.zip` file called `requests.zip`.
    - **Compatible runtimes:** "Python 3.8"

![img](images/task3/creation_layer.png)

4. Click the "Create layer" button.
5. To continue with our goal, we will require another Lambda function that includes the layer `requests`. We need this package because we will perform HTTP requests to the Google Cloud API that, given some text, will classify it and return a category, needed for our goal.
    To create the lambda function and include the layer with the requests package, go in the [AWS Lambda console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions), in the "Functions" sections press the "Create function" button. Specify:
     - **Author from scratch**: in this case, we're not using an AWS blueprint.
     - **Function name**: can be whatever, for this tutorial, we will call it "GoogleCloudClassifier"
     - **Runtime**: Python 3.8, the same as the "requests" Layer just created
6. Keep the rest of the fields as they are and press the "Create function" button.

![img](images/task3/lambdacreation.png)

7. In the now showed page, scroll down and, in the "Layers" section, press the "Add a layer" button.

<img width="1244" alt="Screenshot 2022-05-09 at 17 17 54" src="https://user-images.githubusercontent.com/60050299/167446701-046f57fc-1bf7-4208-8343-8c77f0024573.png">

8. As shown in the following picture, choose "Custom layers" as **layer source** and the `requests` layer from the dropdown menu.

9. Press, then the "Add" button. The "Layers" section of the Lambda function's dashboard should appear as in the following picture:

![img](images/task3/layer2.png)

10. Specify the code of the Lambda function in the "Code source" section of the same dashboard page. Insert the code below:

```python
import json
import requests

def sample_classify_text(text_content):
    google_cloud_key = 'AIzaSyDbdo62MbGPxOwexuqZN3RLvaGUJyMqbtY'
    url = f'https://language.googleapis.com/v1/documents:classifyText?key={google_cloud_key}'
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
```

It is worth noting that we can not work with the `google-cloud-language` library for python since the package is not included in the standard AWS library and we could not add it to the layer as it has some native dependencies that can't be compiled in local.

One solution for this is creating a docker container with all the dependencies but for the sake of simplicity of this laboratory session, we have decided to stick with the easiest solution that consists in calling the Google API using the `requests` library to make simple HTTP requests to the API.

### Connection with Task 2
The "GoogleCloudClassifier" function must be called after the first Lambda function created, "s3-upload-handler", which will extract the text from the document.
To do so:
1. Open the dashboard of the "s3-upload-handler" function using the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1).
2. Once there, click on the "Add destination" button, specifying what happens after the invocation of the "GoogleCloudClassifier" function. Specify the following values for the fields:
     - **Source**: Asynchronous invocation
     - **Condition**: On success. We want to put results in the DynamoDB table only if the execution does not fail
     - **Destination type**: Lambda function
     - **Destination**: Select the "GoogleCloudClassifier" Lambda function

<img width="806" alt="Screenshot 2022-05-09 at 18 52 58" src="https://user-images.githubusercontent.com/60050299/167459195-5dc45fcb-92d2-4868-b8c9-8783186a1cc6.png">

3. Click on the "Save" button.

<img width="987" alt="Screenshot 2022-05-09 at 18 53 43" src="https://user-images.githubusercontent.com/60050299/167459310-5a4934f9-a688-4b4e-b82a-f697462d7d7f.png">


## 🗳️ Task 4 – Upload the URL and its topic to a DynamoDB table
The result of the Lambda function just created will contain the categorization of the document just uploaded on the S3 bucket. This result will be stored in a DynamoDB table. The steps required consists in:

1. First of all we must create the DynamoDB table, which will store the results of the API calls. To do so we open the [AWS DynamoDB Console](https://eu-west-1.console.aws.amazon.com/dynamodbv2/home?region=eu-west-1#service), where we will click on the "Create table" button.

![img](images/task4/DynamoDB.png)

2. In the creation page, we fill the fields in this way (as also shown in the picture below):
    - **Table name**: can be anything, but in this case we call it "topics-table". Better if the same, otherwise the code of the next Lambda function must be adapted accordingly.
    - **Partition key**: `topic`. The partition key will allow to index the table. Set "String" as type. 

![img](images/task4/createTable.png)

3. Leave the other fields untouched and click the "Create table" button. 
4. Once the table is created, we can create the Lambda function from the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda), click "Create function" and specify the `microservice-http-endpoint` blueprint template, as shown in the following picture:

![img](images/task4/bp.png)

5. We then define the following values for the following fields:
     - **Function name**: `PutInTable`
     - **Execution role**: Create a new role from AWS policy templates.
     - **Role name**: `table-updater`

![img](images/task4/infofunct.png)

6. Before creating the function, remember to **delete the API Gateway trigger** using the "Remove button".
7. Click the "Create function" button.

We can change only after the creation of the function its code (since we opted for a blueprint template). As done for the previous task, we can change the code of the function in its dashboard in the "Code source" section of the page.

Insert the code below and click "Deploy":

```python
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
```

### Connection with Task 3
Once the "PutInTable" Lambda function is created, we have to link it to the previously created one, "GoogleCloudClassifier".
To do so:
1. Open the dashboard of the "GoogleCloudClassifier" function using the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1).
2. Once there, click on the "Add destination" button, specifying what happens after the invocation of the "GoogleCloudClassifier" function. Specify the following values for the fields:
     - **Source**: Asynchronous invocation
     - **Condition**: On success. We want to put results in the DynamoDB table only if the execution does not fail
     - **Destination type**: Lambda function
     - **Destination**: Select the PutInTable Lambda function

![img](images/task4/lambdadestination.png)
3. Click on the "Save" button.

<img width="1001" alt="Screenshot 2022-05-09 at 18 54 05" src="https://user-images.githubusercontent.com/60050299/167459405-8dca1c44-c9ba-4b11-884d-ba6ff2a82b6b.png">

### Test the workflow up to this task
And now that the pipeline is connected, we can upload a `.txt` file to our S3 bucket and check if the categorization worked correctly. To do so, as before, upload a simple text file (e.g., a `.txt`) to the S3 bucket created in Task 1, for instance, using the [AWS S3 Console](https://s3.console.aws.amazon.com/s3/buckets?region=eu-west-1).

Open the [AWS DynamoDB Console](https://eu-west-1.console.aws.amazon.com/dynamodbv2/home?region=eu-west-1#tables) and check the "Tables" page. Open the "topics-table" and click on the "Explore table items" button.

![img](images/task4/tableres.png)

By uploading more files file of a similar topic, the list grows:

![img](images/task4/tableres2.png)


## 📎 Task 5 – Get the content of DynamoDB table using AWS Lambda
Once everything is working properly, we can create an interface to access the content of the DynamoDB table, allowing anyone who calls the Lambda function to retrieve the table content containing a categorization of the files in the S3 bucket (based on their content). To do so:
1. Go to the [IAM console](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/policies) and click on the "Create policy" button.
2. In the policy creation page, go to the JSON tab and specify the following JSON document:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ReadTable",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": "TABLE_ARN"
            }
        ]
    }
    ```

   **Be careful to replace the "Resource" field with the ARN of the table created before**. To get it, go to the [AWS DynamoDB Console](https://eu-west-1.console.aws.amazon.com/dynamodbv2/home?region=eu-west-1#tables), open the *topics-table*, where in "Additional info" of the "General information" section, there will be the ARN id of the table.  
    
    Complete the policy creation specifying a name for the policy (e.g., "topics-table-policy") and clicking the "Next" buttons in the bottom of each page. 
    
    Confirm the creation of the policy with the "Create policy" button.
    
3. Go to the [IAM console](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles) and create a new role clicking on the "Create role" button.
    - Select *AWS Service* as *trusted entity*, and *Lambda* as *Use case*. Do not update the "Use cases for other AWS services" field. Proceed clicking the "Next" button.
    - In the second step you need to add the needed permissions. Search for *AWSLambdaBasicExecutionRole* (which Provides write permissions to CloudWatch Logs) and for the policy you created before, "topics-table-policy".
    - Give a name for the role, in this case, we will use "table-scan-role" and click on the "Create role" button.

4. Go to the [AWS Lambda Console](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1) and create a new Lambda function with the "From scratch" option. Follow the fields in this way:
    - **Function name**: tableScan 
    - **Runtime**: Python 3.9. 
    - In the section **Change default execution role** check *"Use an existing role"* and select the "table-scan-role" just created. 
   
<img width="1195" alt="Screenshot 2022-05-10 at 03 42 25" src="https://user-images.githubusercontent.com/60050299/167525743-07bfd654-92fa-48e9-8cbb-21ce0cd0f5c0.png">

    - Then confirm the creation by clicking on the "Create function" button.
    
5. In the "Code" section of the Lambda write the following code:
```python
import json
import boto3

dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(dynamo.scan(TableName="% TABLE NAME %")["Items"])
    }
```
6. Click the "Deploy" button to bind this code to the function. Be careful to change the *TableName* parameter with the name of the DynamoDB table created before. If the tutorial has been followed meticolously, then put "topics-table" as name.
7. Open the "Configuration" section and, under the "Function URL" category, create a function URL, selecting "NONE" as "Auth type". Click the "Save" button to create the endpoint to call the function.

<img width="811" alt="Screenshot 2022-05-10 at 03 50 25" src="https://user-images.githubusercontent.com/60050299/167526476-bddf5770-32ba-412f-a92f-5cf6dbf96b48.png">

8. Copy the "Function URL" generated by AWS for the Lambda and visit it. As a result, the content of the DynamoDB table is returned.
