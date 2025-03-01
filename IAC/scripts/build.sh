#!/bin/bash

# Set default values
STACK_NAME="<your-stack-name>"
API_KEY="<your-api-key>"
TEMPLATE_FILE="../templates/main.yaml"
REGION="us-east-1"

# Function to display usage information
usage() {
  echo "Usage: $0 [-s <stack-name>] [-a <api-key>] [-t <template-file>] [-r <aws-region>]"
  echo "  -s  CloudFormation stack name (default: $STACK_NAME)"
  echo "  -a  API key value (required)"
  echo "  -t  Path to the CloudFormation template file (default: $TEMPLATE_FILE)"
  echo "  -r  AWS region (default: $REGION)"
  exit 1
}

# Parse command-line arguments
while getopts "s:a:t:r:h" opt; do
  case "$opt" in
    s) STACK_NAME="$OPTARG" ;;
    a) API_KEY="$OPTARG" ;;
    t) TEMPLATE_FILE="$OPTARG" ;;
    r) REGION="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

# Check if API_KEY is provided
if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY is required. Please provide it using the -a option."
  usage
fi

# Check if the template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file '$TEMPLATE_FILE' not found."
  exit 1
fi

# AWS CLI command
aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://"$TEMPLATE_FILE" \
  --parameters ParameterKey=ApiKey,ParameterValue="$API_KEY" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION"

echo "Creating CloudFormation stack '$STACK_NAME' using template '$TEMPLATE_FILE'..."

# Optional: Add a wait command to monitor stack creation
# aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"