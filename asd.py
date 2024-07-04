from fastapi import FastAPI, Response
import base64
import json

app = FastAPI()

@app.get("/image_and_array")
async def image_and_array():
    # Load the image from the server
    with open("image.jpg", "rb") as f:
        image_bytes = f.read()
    
    # Encode the image as a base64 string
    image_base64 = base64.b64encode(image_bytes).decode()

    # Create an array of some data
    array = [1, 2, 3, 4, 5]

    # Create a JSON object with the image and the array
    data = {
        "image": image_base64,
        "array": array
    }

    # Return the JSON object as a response
    return Response(content=json.dumps(data), media_type="application/json")