import os
from flask import Flask, jsonify,request
import requests as req
from werkzeug.utils import secure_filename #for secure name file like "this file.js" to "this-file.js"
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from io import BytesIO

app = Flask(__name__)
#config extention allow
app.config["ALLOWED_EXTENTIONS"] = set(["png","jpg","jpeg"])
app.config["UPLOAD_FOLDER"] = "static/uploads/"

#function to check file we get
def allowed_file(filename):
    return "." in filename and \
        filename.split(".", 1)[1] in app.config["ALLOWED_EXTENTIONS"]

model = load_model("soil_types_model.h5", compile=False)
with open("labels.txt", "r") as file:
    labels= file.read().splitlines()


# routing in flask
@app.route("/")
#function in python
def index():
    return jsonify({
        "status":{
            "code": 200,
            "message": "success fetching the API",
        },
        "data": None
    }), 200


@app.route("/predict", methods = ["GET","POST"])
def prediction():
    if request.method == "POST":
        #client send file with key "image"
        # image = request.files["image"]
        data = request.get_json()
        image = data["image"]
        if image:
            #save input image
            # filename = secure_filename(image.filename)
            # image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            #pre-processsing input image
            response = req.get(image)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img = img.resize((224,224))
            img_array = np.asarray(img)
            img_array = np.expand_dims(img_array,axis = 0)
            normalized_image_array = (img_array.astype(np.float32) / 127.5)-1
            data = np.ndarray(shape=(1,224,224,3), dtype=np.float32)
            data[0] = normalized_image_array

            #predicting the image
            prediction = model.predict(data)
            index = np.argmax(prediction)
            class_names = labels[index]
            class_names = class_names[2:]
            confidence_score = prediction[0][index]

            return jsonify({
                "status": {
                    "code": 200,
                    "message": "Success Predicting"
                },
                "data": {
                    "soil_types_prediction": class_names,
                    "confidence": float(confidence_score)
                }
            }), 200
        else:
            return jsonify({
            "status":{
                "code":400,
                "message": "Bad Request"
            },
            "data": None
        }), 400
    else:
        return jsonify({
            "status":{
                "code":405,
                "message": "method not allow"
            },
            "data": None
        }), 405

#running like void
if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
