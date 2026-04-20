#!/usr/bin/env bash
# Creates the Bedrock guardrail used by this project.
#
# Prerequisites:
#   - AWS CLI installed and configured (`aws configure`)
#   - An AWS account with Bedrock access enabled
#   - The Claude model access requested in the Bedrock console
#
# Usage:
#   ./scripts/setup_bedrock_resources.sh
#
# After running, copy the printed Guardrail ID into your .env file
# as BEDROCK_GUARDRAIL_ID.

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
POLICY_FILE="configs/guardrail_policy.json"

echo "🛡️  Creating Bedrock guardrail in region: $REGION"

if [ ! -f "$POLICY_FILE" ]; then
    echo "❌ $POLICY_FILE not found. Run this from the repo root."
    exit 1
fi

# Extract the individual policy sections from the combined JSON
NAME=$(jq -r '.name' "$POLICY_FILE")
DESCRIPTION=$(jq -r '.description' "$POLICY_FILE")
CONTENT_POLICY=$(jq -c '.contentPolicyConfig' "$POLICY_FILE")
PII_POLICY=$(jq -c '.sensitiveInformationPolicyConfig' "$POLICY_FILE")
TOPIC_POLICY=$(jq -c '.topicPolicyConfig' "$POLICY_FILE")
BLOCKED_INPUT=$(jq -r '.blockedInputMessaging' "$POLICY_FILE")
BLOCKED_OUTPUT=$(jq -r '.blockedOutputsMessaging' "$POLICY_FILE")

RESPONSE=$(aws bedrock create-guardrail \
    --region "$REGION" \
    --name "$NAME" \
    --description "$DESCRIPTION" \
    --content-policy-config "$CONTENT_POLICY" \
    --sensitive-information-policy-config "$PII_POLICY" \
    --topic-policy-config "$TOPIC_POLICY" \
    --blocked-input-messaging "$BLOCKED_INPUT" \
    --blocked-outputs-messaging "$BLOCKED_OUTPUT" \
    --output json)

GUARDRAIL_ID=$(echo "$RESPONSE" | jq -r '.guardrailId')
GUARDRAIL_ARN=$(echo "$RESPONSE" | jq -r '.guardrailArn')

echo ""
echo "✅ Guardrail created successfully"
echo ""
echo "   Guardrail ID:  $GUARDRAIL_ID"
echo "   Guardrail ARN: $GUARDRAIL_ARN"
echo ""
echo "👉 Add this to your .env file:"
echo ""
echo "   BEDROCK_GUARDRAIL_ID=$GUARDRAIL_ID"
echo "   BEDROCK_GUARDRAIL_VERSION=DRAFT"
echo ""
echo "Note: The DRAFT version is used until you publish. To publish:"
echo "   aws bedrock create-guardrail-version --guardrail-identifier $GUARDRAIL_ID"
