variable "credentials" {
  description = "My Credentials"
}

variable "project" {
  description = "Project"
}

variable "gcs_bucket_name" {
  description = "NYC taxi data"
}

variable "region" {
  description = "Region"
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}
