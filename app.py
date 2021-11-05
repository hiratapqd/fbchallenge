
import json
import sys


# lambda function handler
def lambda_handler(event, context):
    print (json.dumps(event))
      # print command line arguments
    resp=""
    # arg=sys.argv[1:]
    # user_input = json.loads(event)
    arg=event["key1"]
    print(arg)
    try :
    	arg= int(arg)

    	if arg%3==0:
    		# print("multiplo de 3")
    		resp=resp+"fizz"
    	if arg%5==0:
    		# print("multiplo de 5")
    		resp=resp+"buzz"
    	if arg%3!=0 and arg%5!=0:
    		print("Nao e multiplo de 3 e nem de 5")
    except ValueError  :
    	print("please enter a integer")

    response_body = {
      "result": resp
    }
    response = {
        'headers':{
          "Content-Type": "application/json"
        },
        'statusCode':200,
        'body':json.dumps(response_body),
        'isBase64Encoded': False
    }

    print (resp)
    return response
