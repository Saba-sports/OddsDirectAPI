# How to use SSE python test script

## Install python3

## Install required package
```
pip3 install -r requirements.txt
```

## Adjust config.py
```
VENDOR_ID = 'USE_YOUR_VENDOR_ID'
MEMBER_ID = 'USE_YOUR_MEMBER_ID'
```

## Run script
```
python3 sse_client.py 'getmarkets' "query=%24filter=islive%20and%20marketstatus%20eq%20%27running%27"
```