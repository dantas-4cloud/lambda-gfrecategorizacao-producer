# Terraform Configuration

Infrastructure as Code for Lambda Recategorization Producer.

## Directory Structure

```
terraform/
├── backend.tf           # S3 backend configuration
├── main.tf              # Lambda function, IAM role, CloudWatch
├── variables.tf         # Variable definitions
├── outputs.tf           # Output definitions
├── environments/
│   ├── dev.tfvars      # Development environment variables
│   ├── hom.tfvars      # Homolog environment variables
│   └── prod.tfvars     # Production environment variables
└── .gitignore          # Git ignore patterns
```

## Setup

### Prerequisites

- Terraform >= 1.6.0
- AWS CLI configured with credentials
- S3 bucket for backend state
- DynamoDB table for state locking

### Initialize Terraform

```bash
cd terraform

# Initialize without backend (for local development)
terraform init -backend=false

# Initialize with backend (requires S3 bucket and DynamoDB table)
terraform init
```

### Validate Configuration

```bash
terraform validate
```

### Format Code

```bash
terraform fmt -recursive .
```

## Environments

### Development (dev)

```bash
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
```

- Lambda memory: 256 MB
- Lambda timeout: 60 seconds
- Log retention: 7 days

### Homolog (hom)

```bash
terraform plan -var-file=environments/hom.tfvars
terraform apply -var-file=environments/hom.tfvars
```

- Lambda memory: 512 MB
- Lambda timeout: 120 seconds
- Log retention: 14 days

### Production (prod)

```bash
terraform plan -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars
```

- Lambda memory: 1024 MB
- Lambda timeout: 180 seconds
- Log retention: 30 days

## Resources Created

### Lambda Function
- `aws_lambda_function`: Main Lambda function
- `aws_lambda_function_url`: Function URL for invocation
- `aws_cloudwatch_log_group`: CloudWatch logs

### IAM
- `aws_iam_role`: Lambda execution role
- `aws_iam_role_policy_attachment`: Basic execution policy

### CloudWatch
- `aws_cloudwatch_log_group`: Lambda logs with retention

## CI/CD Pipeline

The terraform configuration is validated and deployed through GitHub Actions:

- `terraform fmt -check`: Format validation
- `terraform validate`: Syntax validation
- `terraform plan`: Plan changes (dev, hom, prod)
- `terraform apply`: Apply changes with manual approval (hom, prod)

## Backend State

State is stored in S3 with DynamoDB locking for consistency across team.

**Note**: Backend configuration requires pre-existing S3 bucket and DynamoDB table.

## Outputs

After applying, retrieve outputs:

```bash
terraform output

# Specific output
terraform output lambda_function_arn
```

Available outputs:
- `lambda_function_arn`: Lambda function ARN
- `lambda_function_name`: Lambda function name
- `lambda_function_url`: Lambda invoke URL
- `lambda_role_arn`: IAM role ARN
- `cloudwatch_log_group_name`: Log group name
- `cloudwatch_log_group_arn`: Log group ARN

## Troubleshooting

### Backend Initialization Error

If you get backend errors after changing backend configuration:

```bash
terraform init -reconfigure
# or
terraform init -migrate-state
```

### Provider Version Mismatch

To upgrade providers:

```bash
terraform init -upgrade
```

### State Lock Issues

Remove state lock if stuck:

```bash
terraform force-unlock <LOCK_ID>
```

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [Lambda Function Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function)
- [S3 Backend](https://www.terraform.io/docs/backends/types/s3.html)
