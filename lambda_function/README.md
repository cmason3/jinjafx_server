## JinjaFx as a Lambda

JinjaFx can also be used as an AWS Lambda (FaaS) using API Gateway as a front end. There are two components, the Lambda itself and a Lambda layer which consists of the Python modules that JinjaFx depends on.

The first step is to clone the Git repository and then build the separate components:

```
git clone https://github.com/cmason3/jinjafx_server.git

cd jinjafx_server/lambda_function

make
```

This will result in `jinjafx_lambda.zip` (the Lambda itself) and `jinjafx_imports.zip` (the additional Lambda layer which contains all the Python modules) which can be used to create the Lambda in AWS. It is important the Python runtime version you specify for the Lambda matches the version of Python that is installed on the machine where you created the zip files.

Using the AWS CLI we can run the following commands to bring our Lambda online - the first two commands create a new role which we can use to associate our Lambda with the `AWSLambdaBasicExecutionRole` role.

```
aws iam create-role --role-name JinjaFx-Lambda-Role --assume-role-policy-document file://JinjaFx-Lambda-Role.json

aws iam attach-role-policy --role-name JinjaFx-Lambda-Role --policy-arn 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
```

We are then going to create the Lambda function itself and add a layer to it for our Python modules using the following commands (you will need to replace the ${VAR} variables with actual values):

```
aws lambda create-function --function-name JinjaFx --timeout 5 --memory-size 256 --zip-file fileb://jinjafx_lambda.zip --handler lambda_function.lambda_handler --runtime python3.7 --role 'arn:aws:iam::${ACCOUNT_ID}:role/JinjaFx-Lambda-Role'

aws lambda publish-layer-version --layer-name JinjaFx-Imports --zip-file fileb://jinjafx_imports.zip --compatible-runtimes python3.7

aws lambda update-function-configuration --function-name JinjaFx --layers 'arn:aws:lambda:${AWS_REGION}:${ACCOUNT_ID}:layer:JinjaFx-Imports:${LAYER_VERSION}'
```

Finaly we need to create an API Gateway (HTTP API) endpoint using the following commands:

```
aws apigatewayv2 create-api --name JinjaFx --protocol-type HTTP --target 'arn:aws:lambda:${AWS_REGION}:${ACCOUNT_ID}:function:JinjaFx'

aws apigatewayv2 update-stage --api-id ${API_ID} --stage-name '$default' --default-route-settings '{"ThrottlingBurstLimit":50,"ThrottlingRateLimit":250}'

aws lambda add-permission --function-name JinjaFx --source-arn 'arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${API_ID}/*/$default' --principal apigateway.amazonaws.com --statement-id 1 --action lambda:InvokeFunction
```

You should then be able to navigate to your API endpoint URL (i.e. https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com) and it should work.

If you wish to update the running code that your Lambda uses then you can use the following command to update it:

```
aws lambda update-function-code --function-name JinjaFx --zip-file fileb://jinjafx_lambda.zip
```
