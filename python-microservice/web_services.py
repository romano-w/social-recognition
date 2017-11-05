# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import face_recognition, json
from flask import Flask, jsonify, request, redirect
from os import listdir
from os.path import isfile, join, dirname, abspath
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    result = {
        "face_found_in_image": "False",
        "is_picture_of_obama": "False"
    }
    return jsonify(result)


def detect_faces_in_image(file_stream):
    with open('names.json') as data_file:    
        names_info = json.load(data_file)

    mypath = dirname(abspath(__file__))+"/known-pics"
    known_encoding_list = [{}]
    fileList = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    print(fileList)
    # Load the uploaded image file
    unknown_img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(unknown_img)
    listMatches = []
    for photo in fileList:
        known_image = face_recognition.load_image_file("./known-pics/"+photo, mode='RGB')
        temp_code = face_recognition.face_encodings(known_image)
        if len(temp_code) == 0:
            print("\n"+photo+" is not being parsed right for some reason")
            continue
        known_encoding = temp_code[0]

        #known_encoding_list.append({"fileName": photo, "encoding": known_encoding})

        if len(unknown_face_encodings) > 0:
            face_found = True
            # See if the first face in the uploaded image matches the known face of Obama
            face_distances = face_recognition.face_distance([known_encoding], unknown_face_encodings[0])
            #if match_results[0]:
            #    is_obama = True
           # if face_distances < 0.6:
            print("Distance:" + str(face_distances))
                #listMatches.append({"fileName": photo, "score":face_distances})
            listMatches.append({"fileName": photo, "score":face_distances})

    #listMatches = sorted(listMatches, key=lambda k: k['score'])
   
    
    #Result is the json we send back to the client
    result = { "results":[]}
    # result = {
    #         "results":[
    #         {
    #         "pic_url": "/known-pics/connor-hat.JPG",
    #         "name": "Connor Hamlet",
    #         "score":face_distances[0]
    #         },

    #         {
    #         "pic_url": "/known-pics/connor-hat.JPG",
    #         "name": "Connor Hamlet",
    #         "score":face_distances[0]
    #         }
    #     ]

    # }
    for match in listMatches:
        print("match: " +match["fileName"] + " "+str(match["score"]))
        result["results"].append({"pic_url": 
        "/known-pics/"+match["fileName"],
        #Below gets the name using the filename in names.json
        "name": names_info[match["fileName"]]["name"],
        "score": str(match["score"]),
        "link": names_info[match["fileName"]]["link"]
        })
    print("Results:\n")
    print(jsonify(result))
    return jsonify(result)

if __name__ == "__main__":
    print("curl -F \"file=@obama2.jpg\" http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
