variable "environment"  { type = string }
variable "app_name"     { type = string; default = "todo-api" }
variable "app_version"  { type = string; default = "1.0.0" }
variable "app_port"     { type = number; default = 5000 }
variable "replicas"     { type = number; default = 2 }
variable "log_level"    { type = string; default = "INFO" }
variable "output_dir"   { type = string; default = "./output" }
variable "docker_image" { type = string }
