import boto3
import time
from math import sqrt, ceil

client = boto3.client("textract", region_name="us-east-1")


def log(service, message, meta=None):
    print({"service": service, "message": message, "meta": meta})


def process_file(bucket, object_name):

    response = client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": object_name}}
    )

    job_id = response["JobId"]
    job_status = "IN_PROGRESS"

    # wait for job to complete
    while job_status == "IN_PROGRESS":

        response = client.get_document_text_detection(JobId=job_id)
        job_status = response["JobStatus"]

        log("textract", "Job status.", job_status)

        time.sleep(5)

    # wait for pages
    blocks = []
    token = "START"

    while token is not None:
        if token == "START":
            response = client.get_document_text_detection(JobId=job_id)
        else:
            response = client.get_document_text_detection(JobId=job_id, NextToken=token)
        token = response.get("NextToken", None)
        blocks += response.get("Blocks", [])

    return blocks


if __name__ == "__main__":
    process_file(bucket="textract-cvs", object_name="kate-1.pdf")
