

from flask import Flask, render_template, send_from_directory, request
import json
import html
import os
import io
import base64

from tensorflow.keras.models import load_model
from tensorflow.keras.losses import BinaryCrossentropy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
import mpld3

from PIL import ImageOps, Image

def DataURL2Bytes(_url):
    format , payload = _url.split(',',1)
    buf = io.BytesIO(base64.urlsafe_b64decode(payload))
    return buf, format

class Models:
    chars = ['a','nu','ti','ke','yo','yorozu']
    models = {}
    BCE = BinaryCrossentropy()
    bce = BinaryCrossentropy(reduction = 'none')
    def init():
        os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
        for c in Models.chars:
            Models.models[c] = load_model('models/' + c + '/autoencoder.h5')
    
    def predict(img, ch, preprocessed = False):
        if not preprocessed:
            if type(img) is str:
                img, _ = DataURL2Bytes(img)
                img = Image.open(img)
            bg = Image.new(mode="RGBA", size=(200, 200), color=(255,255,255,255))
            img = Image.alpha_composite(bg, img).convert("L")
            img = ImageOps.invert(img)
            img.thumbnail((64,64), Image.Resampling.LANCZOS)
            img = np.asarray(img)
        
        img = (np.asarray(img) / 255).reshape((1,64,64,1))
        reconstructed = Models.models[ch](img).numpy()
        loss = Models.BCE(img,reconstructed).numpy()
        loss_map = Models.bce(img,reconstructed).numpy()
        return ((img * 255).astype('uint8'), (reconstructed * 255).astype('uint8'), loss_map, loss)
    
    def visualize(img1, img2, lossmap):
        img1 = img1.reshape((64,64))
        img2 = img2.reshape((64,64))
        lossmap = lossmap.reshape((64,64))

        fig, ax = plt.subplots()
        ax.set_title("You drew")
        ax.imshow(img1, cmap = "bone")
        im1url = Models.to_dataurl(fig)
        plt.close()

        fig, ax = plt.subplots()
        ax.set_title("Reconstructed")
        ax.imshow(img2, cmap = "bone")
        im2url = Models.to_dataurl(fig)
        plt.close()

        fig, ax = plt.subplots()
        ax.set_title("Loss Map")
        ax.imshow(img1, cmap = "bone")
        im = ax.imshow(lossmap, cmap = "inferno", vmin = 0, vmax = 5, alpha = 0.9)
        fig.colorbar(im,
                    ax=ax, orientation='horizontal', label='Loss', ticks = [0,5], 
                    format = mp.ticker.FixedFormatter(['0', '≥ 5']))
        
        im3url = Models.to_dataurl(fig)
        plt.close()
        

        """if to_dataurl: 
            bio = io.BytesIO()
            plt.savefig(bio, format = 'png', dpi  = 100)
            plt.close()
            bio.seek(0)
            dataurl = "data:image/png;base64," + base64.b64encode(bio.getvalue()).decode('utf-8')
            return dataurl
        """

        return (im1url,im2url,im3url)

    def to_dataurl(fig):
        bio = io.BytesIO()
        plt.savefig(bio, format = 'png', dpi  = 100)
        plt.close()
        dataurl = "data:image/png;base64," + base64.b64encode(bio.getvalue()).decode('utf-8')
        return dataurl

Models.init()

app = Flask(__name__, static_folder = 'web/')
@app.route("/")
def indexPage():
    return render_template('main.html')

@app.route('/web/<path:path>', methods=['GET'])
def staticFileSend(path):
    return send_from_directory('web', path)

@app.route('/analyze', methods=['POST'])
def imageAnalyzing():
    char = request.args.get('char')
    img = data = request.get_data().decode('utf-8')
    img, rec, lossmap, loss = Models.predict(img, char)
    img, rec, lossmap = Models.visualize(img, rec, lossmap)

    dat = json.dumps({"input": img, "output": rec, "lossmap" : lossmap, "loss": str(loss)})

    return dat

@app.route('/<string:name>', methods=['GET'])
def webServer(name):
    if name == 'test':
        return render_template('test-model.html')
    elif name == 'work':
        return ''
    elif name == 'about':
        return ''
    return ''

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = '0.0.0.0', port = 80)