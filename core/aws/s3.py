import boto3
from pathlib import Path
from botocore.errorfactory import ClientError

s3 = boto3.client("s3")


def upload_text(text, bucket, object_name):
    text_encoded = text.encode()
    response = s3.put_object(
        Body=text_encoded,
        Bucket=bucket,
        Key=object_name,
        ACL="public-read",
        ContentType="application/json",
    )
    return response


def upload_file(file_path, bucket, object_name=None):
    """Upload a file to an S3 bucket

    Args:
        file_path (str): File to upload
        bucket (str):  Bucket to upload to
        object_name (str, optional): S3 object name. Defaults to None.

    Returns:
        bool: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_path
    if object_name is None:
        object_name = Path(file_path).name
    
    # Convert paths to string
    file_path = str(file_path)
    object_name = str(object_name)

    # Upload the file
    s3.upload_file(
        file_path,
        bucket,
        object_name,
        ExtraArgs={"ACL": "public-read", "ContentType": "application/pdf"},
    )

    return True


def exists_file(bucket, object_name):
    try:
        s3.head_object(Bucket=bucket, Key=object_name)
        return True
    except ClientError:
        pass

    return False


def copy_file(source, bucket, object_name):
    response = s3.copy_object(CopySource=source, Bucket=bucket, Key=object_name,)
    return response


def read_file(bucket, object_name):
    response = s3.get_object(Bucket=bucket, Key=object_name,)
    text = response["Body"].read().decode("utf-8")
    return text


if __name__ == "__main__":
    # upload = upload_file(
    #     "/home/skd/Work/bot-python-cvs/.freelancer/cvs/kate/kate-1.pdf", "textract-cvs"
    # )
    # print("Uploaded:", upload)

    # exists = exists_file(bucket="textract-cvs", object_name="kate.pdf")
    # print("Exists:", exists)

    # copy = copy_file("textract-cvs/kate.pdf", "artists-cvs", "omg/kate.pdf")
    # print (copy)

    # text = read_file("textract-cvs", "apiResponse.json")
    # print("Text:", text)

    upload = upload_binary(
        "hello omg!", bucket="textract-cvs", object_name="123123.json"
    )
    print(upload)
