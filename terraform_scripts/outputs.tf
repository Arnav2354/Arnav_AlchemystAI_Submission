output "caller_public_ip" {
  value = aws_instance.caller.public_ip
}

output "inference_private_ip" {
  value = aws_instance.inference.private_ip
}