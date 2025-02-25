import boto3
import json

def make_def(lambda_arn):
    definition = {
      "Comment": "Final Project State Machine",
      "StartAt": "Map",
      "States": {
        "Map": {
          "Type": "Map",
          "End": True,
          "Iterator": {
            "StartAt": "Lambda Invoke",
            "States": {
              "Lambda Invoke": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "OutputPath": "$.Payload",
                "Parameters": {
                  "Payload.$": "$",
                  "FunctionName": lambda_arn
                },
                "Retry": [
                  {
                    "ErrorEquals": [
                      "Lambda.ServiceException",
                      "Lambda.AWSLambdaException",
                      "Lambda.SdkClientException",
                      "Lambda.TooManyRequestsException",
                      "States.TaskFailed"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                  }
                ],
                "End": True
              }
            }
          }
        }
      }
    }
    return definition

if __name__ == '__main__':
    iam = boto3.client('iam', region_name="us-east-1")
    sfn = boto3.client('stepfunctions', region_name="us-east-1")
    aws_lambda = boto3.client('lambda', region_name="us-east-1")

    # Get Lambda Function ARN and Role ARN
    # Assumes Lambda function name is 'wsb_lambda'
    lambda_arn = [f['FunctionArn']
                  for f in aws_lambda.list_functions()['Functions']
                  if f['FunctionName'] == 'wsb_lambda'][0]
    role = iam.get_role(RoleName='LabRole')

    # Use Lambda ARN to create State Machine Definition
    sf_def = make_def(lambda_arn)

    # Create Step Function State Machine and call it 'wsb_sfn'
    response = sfn.create_state_machine(
            name='wsb_sfn',
            definition=json.dumps(sf_def),
            roleArn=role['Role']['Arn'],
            type='EXPRESS'
        )
