import json
import requests
import os

def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        return True
    else:
        return False

def lambda_handler(event, context):
    # Extracting relevant information from the event object
    submission_info = json.loads(event['Records'][0]['Sns']['Message'])['submission']
    assignment_info = json.loads(event['Records'][0]['Sns']['Message'])['assignment']
    account_info = json.loads(event['Records'][0]['Sns']['Message'])['account']

    # Aggregate information into a single dictionary with code-friendly keys
    aggregated_info = {
        'assignment_name': assignment_info['name'],
        'submission_url': submission_info['submission_url'],
        'submission_updated': submission_info['submission_date'],
        'account_first_name': account_info['first_name'],
        'account_last_name': account_info['last_name'],
        'account_email': account_info['email']
    }

    # Printing the aggregated information
    print(aggregated_info)

    # Downloading the file specified in the submission_url
    download_status = download_file(submission_info['submission_url'], '/tmp/downloaded_file.zip')

    # Printing the download status
    if download_status:
        print('File downloaded successfully.')
    else:
        print('Failed to download file.')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
