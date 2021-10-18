from PIL import Image
from pathlib import Path
import numpy as np
from datetime import datetime
from flask import Flask, request, render_template

from feature_extractor import FeatureExtractor

app = Flask(__name__)

# Read img features
fe = FeatureExtractor()
features = []
img_paths = []

# load features from .npy files and read img_paths
for feature_path in Path("./static/feature").glob("*.npy"):
    features.append(np.load(feature_path))
    img_paths.append(Path("./static/img") / (feature_path.stem + ".jpeg"))
features = np.array(features)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["query_img"]

        # Save query img
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + \
                            datetime.now().isoformat().replace(":", ".") + "_" + file.filename  # create img path
        img.save(uploaded_img_path)  # save the image to the path

        # RUn search
        fe = FeatureExtractor()
        query = fe.extract(img=img)  # feature extract of uploaded img
        dists = np.linalg.norm(features - query, axis=1)  # calc L2 distance
        ids = np.argsort(dists)[0 : 2]  # sort dists return ids
        scores = [(dists[id], img_paths[id]) for id in ids]
        # return dists ad img path
        # print(scores)

        return render_template("index.html", query_path=uploaded_img_path, scores=scores)
    else:
        return render_template("index.html")


if  __name__ == "__main__":
    app.run()