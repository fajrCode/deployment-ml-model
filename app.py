from flask import Flask, jsonify,request
from werkzeug.utils import secure_filename #for secure name file like "this file.js" to "this-file.js"
# from tensorflow.keras.models import load_model


app = Flask(__name__)
#config extention allow
app.config["ALLOWED_EXTENTIONS"] = set(["png","jpg","jpeg"])

#function to check file we get
def allowed_file(filename):
    return "." in filename and \
        filename.split(".", 1)[1] in app.config["ALLOWED_EXTENTIONS"]

#load model
# model = load_model("soil_types_model.h5", compile=False)
#read labels.txt
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
        image = request.files["image"]
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save("static/uploads/", filename)
            return "Saved"
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
    app.run()

