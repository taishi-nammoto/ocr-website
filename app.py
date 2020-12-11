from flask import Flask, render_template, url_for, request, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
import ocr_system
import translate
import psycopg2
import base64


app = Flask(__name__)
app.secret_key = 'secret key'

ENV = 'pro'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/ocr-web'

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gweiqpuummctvf:798f0d92b24adf78572e81b07b7fd293f5105f4e97956ac97f6bfdd47c829552@ec2-34-237-247-76.compute-1.amazonaws.com:5432/d628nv41a202dd'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ImageFile(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String)
    mimetype = db.Column(db.Text)
    date_created = db.Column(db.String)
    transcribed = db.Column(db.Text)
    translated = db.Column(db.Text)
    def __init__(self, name, image, mimetype, date_created, transcribed, translated):
        self.name = name
        self.image = image
        self.mimetype = mimetype
        self.date_created = date_created
        self.transcribed = transcribed
        self.translated = translated


@app.route('/')
def index():
    tasks = ImageFile.query.order_by(ImageFile.id).all()
    tasks.reverse()
    return render_template('index.html', tasks=tasks)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        if not request.files['image']:
            flash('Please select an image.', "warning")
            return redirect('/')
        image = request.files['image']
        img_name = secure_filename(image.filename)
        if db.session.query(ImageFile).filter(ImageFile.name == img_name).count() != 0:
            flash('You have already uploaded the image.', "warning")
            return redirect('/')
        img_binary = image.read()
        img_data = base64.b64encode(img_binary)
        img_data = img_data.decode('UTF-8')
        mimetype = image.mimetype
        now = datetime.now()
        date_created = now.strftime("%m/%d/%Y, %H:%M")
        try:
            transcribed_text= ocr_system.image_to_string(img_binary)
        except:
            flash('This file type is not supported. Please confirm the file type of the image again.', "danger")
            return redirect('/')
        if not transcribed_text:
            flash('No texts were detected. Please select an image of a Hawaiian document.', "warning")
            return redirect('/')
        transcribed_text = transcribed_text.rstrip()
        translated_text = translate.haw_to_eng(transcribed_text)
        data = ImageFile(img_name, img_data, mimetype, date_created, transcribed_text, translated_text)
        db.session.add(data)
        db.session.commit()
        flash('The file has been successfully uploaded!', "success")
        return redirect('/')
    else:
        return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = ImageFile.query.filter_by(id=id).first()
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash('The file has been successfully deleted!', "primary")
        return redirect('/')
    except:
        flash('There was a problem deleting that task', "warning")
        return redirect('/')


if __name__ == '__main__':
    app.run()