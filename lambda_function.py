import json
import boto3

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('CelebrityResults') # type: ignore

def lambda_handler(event, context):
    print(event)

    params = event.get("queryStringParameters") or {}
    image_name = params.get("image")

    if not image_name:
        return {
            "statusCode": 400,
            "body": "Image parameter missing"
        }

    bucket_name = "celebrity-detector"

    response = rekognition.recognize_celebrities(
        Image={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": image_name
            }
        }
    )

    celebrities = []

    for celeb in response["CelebrityFaces"]:
        celebrities.append({
    "name": celeb["Name"],
    "confidence": str(round(celeb["MatchConfidence"], 2))
    })

    table.put_item(
        Item={
            "image_name": image_name,
            "result": celebrities
        }
    )

    return {
    "statusCode": 200,
    "headers": {
        "Content-Type": "text/html"
    },
    "body": f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>AI Celebrity Detector</title>

    <style>
    body {{
        font-family: Arial, sans-serif;
        background: #f4f4f4;
        text-align: center;
        padding: 40px;
    }}

    .card {{
        width: 500px;
        margin: auto;
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.2);
    }}

    img {{
        width: 220px;
        height: 220px;
        object-fit: cover;
        border-radius: 15px;
    }}

    .name {{
        font-size: 32px;
        color: #E1306C;
        margin-top: 20px;
    }}

    .confidence {{
        margin-top: 15px;
        font-size: 22px;
        font-weight: bold;
        color: green;
    }}
    </style>

    </head>

    <body>

    <div class="card">

    <h1>AI Celebrity Detector</h1>

    <img src="https://celebrity-detector.s3.ap-south-1.amazonaws.com/{image_name}">

    <div class="name">
    {celebrities[0]['name']}
    </div>

    <div class="confidence">
    Confidence: {celebrities[0]['confidence']}%
    </div>

    </div>

    </body>
    </html>
    """
}