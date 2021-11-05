import requests
import json

#final code to check the APIgateway

# url to the api gateway we created

url='https://nvik0to4b8.execute-api.sa-east-1.amazonaws.com/blur/charlie'
url='https://gfigsf70if.execute-api.sa-east-1.amazonaws.com/v0/lambda'
# url='https://yis9q2uwp6.execute-api.sa-east-1.amazonaws.com/test/beta'
# url='https://r1ppwau0ug.execute-api.sa-east-1.amazonaws.com/test/alfa'
# url = 'https://xhnher889l.execute-api.sa-east-1.amazonaws.com/test/cloud_aysha'
# url ='https://xhnher889l.execute-api.sa-east-1.amazonaws.com/prod/cloud_aysha'
# the api key value we created
# api_key = '0zxisQpEGi9JlmEe0opDu7UnRFRbu8CXPOfJmWQ5'
api_key='ERrs793Bx02kXvrRF2ApH64KFVt3WaBb894mnGJ6'

# the key is passed to the api gateway throught the 'x-api-key' key in the headers
headers = {
    'x-api-key':api_key
}

# the text we want to correct
payload = {
    "key1": "5"
}

# get the corrected text from the serverless lambda through standard HTTP requests
response = requests.post(url, headers=headers, json=payload)

# print result
print(response.json())