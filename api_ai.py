"""
Run this model in Python

> pip install azure-ai-inference
"""

import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
token =  "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"

def main():
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")

    client = ChatCompletionsClient(
        endpoint="https://models.github.ai/inference",
        credential=AzureKeyCredential(token)
    )

    response = client.complete(
        messages=[
            {"role": "user", "content": "привет как дела "}
        ],
        model="deepseek/DeepSeek-R1",
        max_tokens=2048
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"The sample encountered an error: {err}")