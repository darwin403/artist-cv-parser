import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.resolve()


#################
# ENV VARIABLES #
#################

ENV_PATH = str(PROJECT_ROOT / ".env")
ENV_LOCAL_PATH = str(PROJECT_ROOT / ".env.local")

# load default variables
load_dotenv(ENV_PATH)

# overide variables with .env.local
load_dotenv(ENV_LOCAL_PATH, override=True)

#######
# AWS #
#######

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")