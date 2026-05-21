# AlchemystAI DevOps Internship Assignment

## Live API Endpoint
## What Was Built

- AWS VPC with public and private subnets
- caller-worker on public EC2 — accepts POST /v1/chat/completions from internet
- inference-worker on private EC2 — processes requests, not reachable from internet
- All infrastructure provisioned with Terraform

## Why iii-sdk Was Not Used

The iii framework requires KVM virtualization to run worker sandboxes.
t3.micro instances on AWS do not support KVM (no /dev/kvm available).
Additionally, iii-sdk is not available on public PyPI and their private
registry (pypi.iii.dev) had an expired SSL certificate at time of submission.

Equivalent architecture was implemented using Flask — same network topology,
same request flow, same isolation between public and private workers.

## Setup Instructions

### Prerequisites
- AWS CLI configured
- Terraform installed
- SSH key at ~/.ssh/id_rsa

### Provision Infrastructure

```bash
cd terraform_scripts
terraform init
terraform apply
```

Note the output IPs:
- caller_public_ip
- inference_private_ip

### Deploy Inference Worker (private VM)

```bash
# copy key to caller VM first
scp -i ~/.ssh/id_rsa ~/.ssh/id_rsa ec2-user@<caller_public_ip>:~/.ssh/id_rsa

# SSH into caller VM
ssh -i ~/.ssh/id_rsa ec2-user@<caller_public_ip>

# from caller VM, SSH into inference VM
ssh -i ~/.ssh/id_rsa ec2-user@<inference_private_ip>

# on inference VM
pip3 install flask
curl -O https://raw.githubusercontent.com/Arnav2354/Arnav_AlchemystAI_Submission/main/workers/inference-worker/inference_app.py
python3 inference_app.py &
```

### Deploy Caller Worker (public VM)

```bash
# on caller VM
pip3 install flask requests
curl -O https://raw.githubusercontent.com/Arnav2354/Arnav_AlchemystAI_Submission/main/workers/caller-worker/caller_app.py
INFERENCE_HOST=<inference_private_ip> python3 caller_app.py &
```

### Test

```bash
curl -X POST http://<caller_public_ip>:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}]}'
```

## What I Would Harden Before Production

- Replace Flask dev server with gunicorn
- Add HTTPS/TLS to the public endpoint
- Use AWS Secrets Manager for any credentials
- Add proper logging and CloudWatch integration
- Use Auto Scaling Group for the caller worker
- Lock down security groups further — restrict SSH to specific IPs
- Add health check endpoint and ALB in front of caller worker
- Use IAM instance roles instead of passing credentials

## What I Would Do Differently at 100x Model Size

- Use GPU instances (p3 or g4dn) for inference
- Put inference worker behind an internal load balancer
- Use S3 to store model weights instead of local disk
- Use EKS to horizontally scale inference workers
- Add a queue (SQS) between caller and inference to handle load spikes
- Use spot instances for inference to reduce cost

## Server Restart Behavior

Currently both workers run as background processes.
On restart they need to be manually restarted.

In production this would be handled with systemd units:

```bash
# example systemd unit for inference worker
[Unit]
Description=Inference Worker
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/ec2-user/inference_app.py
Restart=always
User=ec2-user

[Install]
WantedBy=multi-user.target
```

This ensures workers restart automatically on server reboot.

## Screenshots

### VPC
![VPC](Screenshot_22-5-2026_05939_us-...jpeg)

### Subnets
![Subnets](Screenshot_22-5-2026_1052_us-...jpeg)

### EC2 Instances
![EC2](Screenshot_22-5-2026_1018_us-...jpeg)

## Note on Live Deployment

The live deployment has been torn down after submission to avoid unnecessary AWS costs (NAT Gateway + EC2 running costs).

To redeploy from scratch:

```bash
cd terraform_scripts
terraform init
terraform apply
```

Full infrastructure comes up in under 5 minutes. Then follow the setup instructions above to deploy the workers.
