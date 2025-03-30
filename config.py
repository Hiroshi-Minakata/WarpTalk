import os

# API
API_KEY                 = os.environ["API_KEY"]
CHANNEL_ACCESS_TOKEN    = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET          = os.environ["CHANNEL_SECRET"]

# AI
MODEL_NAME          = os.environ["MODEL_NAME"]
SYSTEM_INSTRUCTIONS = os.environ["SYSTEM_INSTRUCTIONS"]

# Chat
SYSTEM_SET_URL      = os.environ["SYSTEM_SET_URL"]
SYSTEM_REPLY_TIME   = os.environ["SYSTEM_REPLY_TIME"]
SYSTEM_HOW_TO_USE   = os.environ["SYSTEM_HOW_TO_USE"]
MESSAGE_SETED_URL   = os.environ["MESSAGE_SETED_URL"]
MESSAGE_NOT_SET_URL = os.environ["MESSAGE_NOT_SET_URL"]
MESSAGE_REPLY_TIME  = os.environ["MESSAGE_REPLY_TIME"]
MESSAGE_HOW_TO_USE  = os.environ["MESSAGE_HOW_TO_USE"]
MESSAGE_OK_URL      = os.environ["MESSAGE_OK_URL"]
MESSAGE_BAD_URL     = os.environ["MESSAGE_BAD_URL"]

# DB
USER_DATA_PATH = os.environ["USER_DATA_PATH"]

# Other
ENV     = os.environ["ENV"]
PORT    = os.getenv("PORT", 8080)