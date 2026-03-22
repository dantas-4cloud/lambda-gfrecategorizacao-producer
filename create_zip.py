import zipfile
import os

# Create lambda_function.zip in terraform directory
os.chdir("terraform")

with zipfile.ZipFile("lambda_function.zip", "w") as zf:
    content = 'def lambda_handler(event, context):\n    return {"statusCode": 200}'
    zf.writestr("lambda_handler.py", content)

print("lambda_function.zip created successfully")
