from flask import Flask, request
from flask_restx import Resource, Api, fields
from datetime import datetime
import boto3
import json

app = Flask(__name__)
api = Api(app)
ns = api.namespace('Fizzbuzz', description='FizzBuzz Game.') #this set the header of the page
cw_ns = api.namespace('CloudWatch', description='CloudWatch Log.') #this set the header of the page


fizzbuzz_input_model = api.model('FizzBuzzInput', {
    'your_number': fields.Integer(required=True, description='FizzBuzz challenge number', default='15')
})
# Modelos
create_log_model = api.model('CreateLogGroup', {
    'log_group_name': fields.String(required=True, description='Name of the log group')
})

retention_model = api.model('SetRetentionPolicy', {
    'log_group_name': fields.String(required=True, description='Name of the CloudWatch log group (default is "MyCloudwatchLog")', default='MyCloudwatchLog'),
    'retention_in_days': fields.Integer(required=False, description='Retention period in days', default=7)
})
api_gateway_model = api.model('CreateAPIGateway', {
    'api_name': fields.String(required=True, description='Name of the API Gateway'),
    'log_group_name': fields.String(required=False, description='CloudWatch log group name', default='MyCloudwatchLog'),
})
# Cliente Boto3 apontando para LocalStack
logs_client = boto3.client('logs', region_name='us-east-1', endpoint_url='http://localhost:4566')
apig_client = boto3.client('apigateway', region_name='us-east-1', endpoint_url='http://localhost:4566')  # adjust endpoint for AWS if needed
enable_xray_model = api.model('EnableXRayTracing', {
    'api_id': fields.String(required=True, description='The ID of the API Gateway'),
    'stage_name': fields.String(required=True, description='The name of the stage (e.g., "prod")')
})

# 🔢 FizzBuzz route
@ns.route("/")
class FizzBuzz(Resource):
    @api.expect(fizzbuzz_input_model)
    def post(self):
        data = request.get_json()
        number=data.get('your_number')
        if number % 3 == 0 and number % 5 == 0:
            return {"result": "fizzbuzz"}
        elif number % 3 == 0:
            return {"result": "fizz"}
        elif number % 5 == 0:
            return {"result": "buzz"}
        else:
            return {"message": f"The number {number} is divisible by neither 3 nor 5"}

# Rota: Criar log group com retenção de 7 dias
@cw_ns.route("/create_log_group")
class CreateLogGroup(Resource):
    @api.expect(create_log_model)
    def post(self):
        data = request.get_json()
        log_group_name = data['log_group_name']

        try:
            logs_client.create_log_group(logGroupName=log_group_name)
            logs_client.put_retention_policy(logGroupName=log_group_name, retentionInDays=7)
            return {"message": f"Log group '{log_group_name}' created with 7-day retention."}
        except logs_client.exceptions.ResourceAlreadyExistsException:
            return {"message": f"Log group '{log_group_name}' already exists."}, 409

# Rota: Alterar retenção
@cw_ns.route("/set_retention")
class SetRetention(Resource):
    @api.expect(retention_model)
    def post(self):
        data = request.get_json()
        log_group_name = data['log_group_name']
        retention = data.get('retention_in_days', 7)

        try:
            logs_client.put_retention_policy(logGroupName=log_group_name, retentionInDays=retention)
            return {"message": f"Retention for log group '{log_group_name}' set to {retention} days."}
        except logs_client.exceptions.ResourceNotFoundException:
            return {"message": f"Log group '{log_group_name}' not found."}, 404
 
@cw_ns.route("/create_api_gateway")
class CreateAPIGateway(Resource):
    @api.expect(api_gateway_model)
    def post(self):
        data = request.get_json()
        api_name = data['api_name']
        log_group_name = data.get('log_group_name', 'MyCloudwatchLog')

        try:
            # Step 1: Create the REST API
            api_response = apig_client.create_rest_api(
                name=api_name,
                description='API Gateway with IP rate limit, CloudWatch logging, and authentication',
                endpointConfiguration={'types': ['REGIONAL']},
                tags={'Project': 'FizzBuzzApp'}
            )
            api_id = api_response['id']

            # Step 2: Get root resource ID
            resources = apig_client.get_resources(restApiId=api_id)
            root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')

            # Step 3: Enable logging and throttling using stage
            apig_client.create_deployment(restApiId=api_id, stageName='prod')

            apig_client.update_stage(
                restApiId=api_id,
                stageName='prod',
                patchOperations=[
                    {"op": "replace", "path": "/*/*/logging/loglevel", "value": "INFO"},
                    {"op": "replace", "path": "/methodSettings/*/*/logging/dataTrace", "value": "true"},
                ]
            )

            # Step 4: Create API Key & Usage Plan
            api_key_response = apig_client.create_api_key(
                name=f'{api_name}Key',
                enabled=True,
                generateDistinctId=True
            )

            usage_plan = apig_client.create_usage_plan(
                name=f'{api_name}UsagePlan',
                throttle={'rateLimit': 100, 'burstLimit': 100},
                apiStages=[{'apiId': api_id, 'stage': 'prod'}]
            )

            apig_client.create_usage_plan_key(
                usagePlanId=usage_plan['id'],
                keyId=api_key_response['id'],
                keyType='API_KEY'
            )

            return {
                "message": f"API Gateway '{api_name}' created.",
                "api_id": api_id,
                "api_key": api_key_response['value'],
                "log_group": log_group_name
            }

        except Exception as e:
            return {"error": str(e)}, 500        

@cw_ns.route("/enable_xray")
class EnableXRay(Resource):
    @api.expect(enable_xray_model)
    def post(self):
        data = request.get_json()
        api_id = data['api_id']
        stage_name = data['stage_name']

        try:
            response = apig_client.update_stage(
                restApiId=api_id,
                stageName=stage_name,
                patchOperations=[
                    {
                        'op': 'replace',
                        'path': '/tracingEnabled',
                        'value': 'true'
                    }
                ]
            )
            return {"message": f"X-Ray tracing enabled for API {api_id} at stage {stage_name}."}
        except Exception as e:
            return {"error": str(e)}, 500

        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

'''
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.15.6:8000
'''
    
#usage examples on windows
#curl -X "POST" "http://127.0.0.1:8000/Fizzbuzz/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"seu_numero\": 7}"

#usage example on Linux
#curl -X 'POST' 'http://192.168.15.6:8000/Fizzbuzz/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "seu_numero": 3}' 