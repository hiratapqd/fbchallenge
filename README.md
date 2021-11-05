# fbchallenge
- requirements
  This section presents the application you need to install before use this code
  •	Git cli installed
  •	Python 3.6 or above
  •	Aws cli v2

- Download the code
  Use terminal (MAC) or command prompt (windows):
  Create a directory called fbchallenge
  mkdir /Users/<user>/fbchallenge
  Goes to the directory fbchallenge
  cd /Users/<user>/ fbchallenge or cd C:/Users/<user>/ fbchallenge
  git init
  clone the fbchallenge repository to your local computer
  git clone https://github.com/hiratapqd/fbchallenge.git
- deploy the AWS environment
  execute the command:
  aws cloudformation deploy --stack-name fizzbuzz-api --template-file fizzbuzz.yaml --capabilities CAPABILITY_IAM
  
- using the code
  if the above command finished without errors, use the command to test:

  curl -v -X POST \
    'https://yis9q2uwp6.execute-api.sa-east-1.amazonaws.com/test/beta' \
    -H 'content-type: application /json' \
    -d '{ "key1": "15"}'
