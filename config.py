import os

# API
API_KEY                 = os.environ["API_KEY"]
CHANNEL_ACCESS_TOKEN    = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET          = os.environ["CHANNEL_SECRET"]

# AI
MODEL_NAME          = os.environ["MODEL_NAME"]
SYSTEM_INSTRUCTIONS = os.environ["SYSTEM_INSTRUCTIONS"]

# Chat
SYSTEM_SET_EMAIL    = os.environ["SYSTEM_SET_EMAIL"]
SYSTEM_REPLY_TIME   = os.environ["SYSTEM_REPLY_TIME"]
MESSAGE_SET_EMAIL   = os.environ["MESSAGE_SET_EMAIL"]
MESSAGE_REPLY_TIME  = os.environ["MESSAGE_REPLY_TIME"]
MESSAGE_OK_EMAIL    = os.environ["MESSAGE_OK_EMAIL"]
MESSAGE_BAD_EMAIL   = os.environ["MESSAGE_BAD_EMAIL"]

# DB
USER_DATA_PATH = os.environ["USER_DATA_PATH"]

# Other
ENV     = os.environ["ENV"]
PORT    = os.getenv("PORT", 8080)
USER_ID = os.getenv("USER_ID")