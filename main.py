import json

import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CREATE DATABASE


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///colgados.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class Colgado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_key = db.Column(db.Integer, unique=False, nullable=False)
    part_no = db.Column(db.String(250), unique=False, nullable=False)
    pieza_rack = db.Column(db.Integer, unique=False, nullable=False)
    rack_eslabon = db.Column(db.Integer, unique=False, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Colgados {self.title}>'


db.create_all()

all_colgados = []


# WTForm
class AddForm(FlaskForm):
    part_key = IntegerField("Part Key", validators=[DataRequired()])
    part_no = StringField("Numero de Parte (Part_No)", validators=[DataRequired()])
    pieza_rack = IntegerField("Piezas por Rack", validators=[DataRequired()])
    rack_eslabon = IntegerField("Racks por Eslabon", validators=[DataRequired()])
    submit = SubmitField("Agregar")


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/lista_de_colgados")
def lista_de_colgados():
    all_colgados = db.session.query(Colgado).all()
    return render_template("lista_de_colgados.html", colgados=all_colgados)


@app.route("/atributos_Lineas")
def atributos_lineas():
    return render_template("atributos_lineas.html")


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_colgado = Colgado(
            part_key=form.part_key.data,
            part_no=form.part_no.data,
            pieza_rack=form.pieza_rack.data,
            rack_eslabon=form.rack_eslabon.data
        )
        # if request.method == "POST":
        #     new_colgado = Colgado(
        #         part_key = request.form["part_key"],
        #         part_no = request.form["part_no"],
        #         pieza_rack = request.form["pieza_rack"],
        #         rack_eslabon = request.form["rack_eslabon"]
        #     )
        db.session.add(new_colgado)
        db.session.commit()
        return redirect(url_for('lista_de_colgados'))
    return render_template("add.html", form=form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # Actualizar Registro
        colgado_id = request.form["id"],
        colgado_actualizar = Colgado.query.get(colgado_id)
        colgado_actualizar.pieza_rack = request.form["pieza_rack"]
        colgado_actualizar.rack_eslabon = request.form["rack_eslabon"]
        db.session.commit()
        return redirect(url_for('lista_de_colgados'))
    colgado_id = request.args.get('id')
    colgado_seleccionado = Colgado.query.get(colgado_id)
    return render_template("edit.html", colgado=colgado_seleccionado)


@app.route("/delete")
def delete():
    colgado_id = request.args.get('id')

    # Borra registro
    colgado_borrar = Colgado.query.get(colgado_id)
    db.session.delete(colgado_borrar)
    db.session.commit()
    return redirect(url_for('lista_de_colgados'))


# --------------------funcionalidad para traer rates de produccion de PLEX------------
@app.route("/rates_actuales")
def get_rate():
    ds_endpoint = "https://scanpaintmx1.on.plex.com/api/datasources/4494/execute"

    headers = {
        "Authorization": "Basic U2NhbnBhaW50TVhXczFAcGxleC5jb206ODJhNDgxOS05YTkzLTQ=",
        "Content-Type": "application/json;charset=utf-8",
        "Accept": "application/json",
        "Accept-Encoding": "application/gzip",
    }

    json_request = {
        "inputs": {
            "Part_Key": 6220439,
            "Part_Operation_Key": 31460695
        }
    }

    response = requests.post(url=ds_endpoint, json=json_request, headers=headers)
    data = response.json()
    data_dict = json.loads(response.text)
    # return response.json()
    return render_template("rates_actuales.html", rates=data_dict)

    # data = response.json()
    # df = pd.io.json.json_normalize(data)
    # temp = df.to_dict("records")
    # columnNames = df.columns.values
    # return render_template("test.html", records=temp, colnames=columnNames)

    # data1 = response.json()
    # data = pd.io.json.json_normalize(data1)
    # temp_dict = data.to_dict(orient='records')
    # return render_template('rates_actuales.html', rates = temp_dict)

    # data1 = response.json()

    # return data1


# --------------------Test para json PLEX a HTML Table------------
# @app.route("/test")
# def get_rate():
#     with open("plex_api2.json") as data:
#         data_lines2 = data.read()
#         data_json2 = json.loads(data_lines2)
#         data_dict2 = data_json2["tables"][0]
#
#     return render_template("test.html", rates=data_dict2)


if __name__ == "__main__":
    app.run(debug=True)
