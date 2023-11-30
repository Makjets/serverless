import base64
import json
import requests
import os
import boto3
from botocore.exceptions import ClientError
from google.cloud import storage
import re
from datetime import datetime


def create_path(aggregated_info):
    # Extract information
    assignment_name = aggregated_info['assignment_name']
    account_email = aggregated_info['account_email']
    first_name = aggregated_info['account_first_name']
    last_name = aggregated_info['account_last_name']
    attempts = aggregated_info['attempts']

    # Remove special characters, convert to lowercase, and replace spaces
    clean_assignment_name = re.sub(r'[^a-zA-Z0-9\s]', '', assignment_name).lower().replace(' ', '_')
    clean_email = re.sub(r'[^a-zA-Z0-9\s]', '', account_email).lower().replace(' ', '_')
    clean_first_name = re.sub(r'[^a-zA-Z0-9\s]', '', first_name).lower().replace(' ', '_')
    clean_last_name = re.sub(r'[^a-zA-Z0-9\s]', '', last_name).lower().replace(' ', '_')

    # Create the path
    path = f"{clean_assignment_name}/{clean_email}/{clean_first_name}_{clean_last_name}_{attempts}.zip"

    return path

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


def download_file(url, destination):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Check if the content length is 0 (0-byte payload)
        if 'Content-Length' in response.headers and int(response.headers['Content-Length']) == 0:
            raise ValueError("Download failed. The file has a 0-byte payload.")
        
        if len(response.content) == 0:
            raise ValueError("Download failed. The file has no content.")

        # Check if the content type indicates a downloadable file
        content_type = response.headers.get('Content-Type', '')
        if 'application' not in content_type and 'zip' not in content_type:
            raise ValueError("Download failed. The URL does not point to a downloadable file.")

        with open(destination, 'wb') as file:
            file.write(response.content)
        
        return True, None  # Success, no failure reason
    except requests.exceptions.RequestException as e:
        return False, f"Download failed: Invalid URL or network issues."
    except ValueError as e:
        return False, str(e)

def send_email(email, aggregated_info, status, error_message):

    SENDER = os.environ['SENDER_EMAIL']
    RECIPIENT = email
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    # SUBJECT = "Your Submission for "+ aggregated_info['assignment_name'] + " has been Successful" if status == "success" else "Your Submission for "+ aggregated_info['assignment_name'] + " has Failed"
    SUBJECT = "Submission Status for " + aggregated_info['assignment_name']
    # Assuming status indicates the submission status ('success' or 'fail')

    # Convert the timestamp to a datetime object
    timestamp = datetime.strptime(aggregated_info['submission_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")

    # Convert to a user-friendly format
    user_friendly_format = timestamp.strftime("%d %B %Y %I:%M %p")

    if status == 'success':
        BODY_TEXT = (f"Hi {aggregated_info['account_first_name']} {aggregated_info['account_last_name']},\r\n"
                        f"Congratulations! Your submission for the '{aggregated_info['assignment_name']}' assignment "
                        f"has been successful.\r\n"
                        f"Here are the details of your submission:\r\n"
                        f"Submitted URL: {aggregated_info['submission_url']}\r\n"
                        f"GCP Path: {aggregated_info['gcp_path']}\r\n"
                        f"Submission Updated Date: {user_friendly_format}\r\n"
                        f"Attempts used: {aggregated_info['attempts']}\r\n\n"
                        f"Best Of Luck!\n"
                        f"CSYE6225 Team"
                        )

        BODY_HTML = f"""<html>
        <head></head>
        <body>
            <p>Hi {aggregated_info['account_first_name']} {aggregated_info['account_last_name']},</p>
            <p>Your submission for the '{aggregated_info['assignment_name']}' assignment has been successful.</p>
            <p>Here are the details of your submission:</p>
            <ul>
                <li>GCP Path: {aggregated_info['gcp_path']}</li>
                <li>Submission Updated Date: {user_friendly_format}</li>
                <li>Attempts used: {aggregated_info['attempts']}</li>
            </ul>
            <p>Sincerely,<br>Makarand Madhavi<br>CSYE6225 Teaching Assistant</p>
        </body>
        </html>
        """
    else:
        BODY_TEXT = (f"Hi {aggregated_info['account_first_name']} {aggregated_info['account_last_name']},\r\n"
                        f"We regret to inform you that your submission for the '{aggregated_info['assignment_name']}' assignment "
                        f"has failed due to the following reason:\r\n"
                        f"{error_message}\r\n"
                        "Please review your submission and try again.\r\n"
                        f"Here are the details of your submission:\r\n"
                        f"Submission Updated Date: {aggregated_info['submission_updated']}\r\n"
                        f"Attempts used: {aggregated_info['attempts']}\r\n\n"
                        f"Best Of Luck!\n"
                        f"CSYE6225 Team"
                        )

        BODY_HTML = f"""<html>
        <head></head>
        <body>
            <p>Hi {aggregated_info['account_first_name']} {aggregated_info['account_last_name']},</p>
            <p>We regret to inform you that your submission for the '{aggregated_info['assignment_name']}' assignment has failed due to the following reason:</p>
            <p>{error_message}</p>
            <p>Please review your submission and try again.</p>
            <p>Here are the details of your submission:</p>
            <ul>
                <li>Submission Updated Date: {user_friendly_format}</li>
                <li>Attempts used: {aggregated_info['attempts']}</li>
            </ul>
            <p>Sincerely,<br>Makarand Madhavi<br>CSYE6225 Teaching Assistant</p>
        </body>
        </html>
        """

          

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    print(RECIPIENT)
    print(SENDER)
    print(SUBJECT)
    print(BODY_HTML)
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            ReplyToAddresses=[
                SENDER,
            ],
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
        
    except ClientError as e:
        print(e.response)
        return "Mail delivery Failed", f"Email failed to send: {e.response['Error']['Message']}", BODY_TEXT
    except Exception as e:
        print(e)
        return "Mail delivery Failed", f"Email failed to send: {e}", BODY_TEXT
    else:
        print("Email sent! Message ID: "+response['MessageId'])
        return "Email Sent Successfully", None, BODY_TEXT  # Success, no failure reason

def insert_email_status(email, aggregated_info, status, error_message,body_text):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    response = table.put_item(
        Item={
            'Id': aggregated_info['submission_id'],
            'body_text': body_text,
            'recipient': aggregated_info['account_email'],
            'attempts': aggregated_info['attempts'],
            'status': status,
            'error_message': error_message
        }
    )
    return response

def lambda_handler(event, context):
    # Extracting relevant information from the event object
    submission_info = json.loads(event['Records'][0]['Sns']['Message'])['submission']
    assignment_info = json.loads(event['Records'][0]['Sns']['Message'])['assignment']
    account_info = json.loads(event['Records'][0]['Sns']['Message'])['account']
    attempts = json.loads(event['Records'][0]['Sns']['Message'])['attempts']

    # Aggregate information into a single dictionary with code-friendly keys
    aggregated_info = {
        'assignment_name': assignment_info['name'],
        'assignment_id': assignment_info['id'],
        'submission_id': submission_info['id'],
        'submission_url': submission_info['submission_url'],
        'submission_updated': submission_info['submission_date'],
        'account_first_name': account_info['first_name'],
        'account_last_name': account_info['last_name'],
        'account_email': account_info['email'],
        'attempts': attempts
    }

    destination = create_path(aggregated_info)
    # Printing the aggregated information
    print(aggregated_info)
    tmp_path = '/tmp/' + destination.replace('/', '_')
    aggregated_info['gcp_path'] = destination
    # Downloading the file specified in the submission_url
    success, failure_reason = download_file(submission_info['submission_url'], tmp_path)
   
    if success:
        status = "success"
        error_message = None
        upload_blob('makjets_demo', tmp_path, destination)
        print('File downloaded and uploaded successfully.')

    else:
        status = "fail"
        error_message = f"{failure_reason}"
        print(error_message)

    # Assuming send_email is a function that sends an email with the specified parameters
    status, error, body_text = send_email(aggregated_info['account_email'], aggregated_info, status, error_message)
    insert_email_status(aggregated_info['account_email'], aggregated_info, status, error,body_text)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
