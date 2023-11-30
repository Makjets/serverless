# Serverless

### Overview

This code is designed to be deployed as an AWS Lambda function. It performs the following tasks:

1. Downloads a file from a specified URL.
2. Uploads the downloaded file to Google Cloud Storage (GCS).
3. Sends an email to a specified recipient with information about the submission status.
4. Records the email status, along with other relevant information, in an Amazon DynamoDB table.

### Setup

#### 1. Install Dependencies

Before deploying the Lambda function, you need to install the required Python dependencies. You can use the following command:

```bash
pip install --target ./package -r requirements.txt
```

This command installs the required packages in the `package` directory.

#### 2. Package Dependencies

After installing the dependencies, you need to create a ZIP archive containing both your code and the installed packages. You can use the following command:

```bash
cd package
zip -r ../lambda_function.zip .
```

This command creates a ZIP file named `lambda_function.zip` containing your code and the installed packages.

#### 3. Deploy to AWS Lambda

1. Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/).
2. Click on "Create function" and choose "Author from scratch."
3. Enter a name for your function, choose Python as the runtime, and select an existing role with the necessary permissions or create a new role.
4. Click on "Create function."

#### 4. Configure Environment Variables

Configure the following environment variables for your Lambda function:

- `SENDER_EMAIL`: The email address from which the emails will be sent.
- `TABLE_NAME`: The name of the DynamoDB table where email status information will be stored.

#### 5. Upload ZIP Package

Upload the `lambda_function.zip` file you created earlier as the deployment package for your Lambda function.

#### 6. Set Handler

Set the handler to the main Lambda function, for example, `lambda_function.lambda_handler`.

#### 7. Configure Trigger

Configure a trigger for your Lambda function. This code is designed to be triggered by an SNS (Simple Notification Service) topic. Ensure that your Lambda function is subscribed to the appropriate SNS topic.

### Usage

Once the Lambda function is set up, it will be triggered by SNS messages. The SNS messages should contain JSON payloads with information about the submission, assignment, account, and attempts.

The Lambda function will download a file from the specified URL, upload it to GCS, send an email with the submission status, and record the email status in DynamoDB.

### Monitoring

You can monitor the execution of your Lambda function using AWS CloudWatch Logs. Check the logs for any error messages or unexpected behavior.

### Cleanup

To clean up the resources created for this Lambda function, delete the Lambda function, associated IAM role, and any other resources created during the setup.

### Note

Make sure that your AWS Lambda function has the necessary permissions to interact with DynamoDB, SNS, and SES (Simple Email Service). Adjust the IAM role attached to your Lambda function accordingly.
