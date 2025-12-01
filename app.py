from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "clave_secreta"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

usuario_valido = {"admin": "1234"}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        if usuario in usuario_valido and usuario_valido[usuario] == password:
            session["usuario"] = usuario
            flash("Bienvenido, inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales incorrectas, intente de nuevo.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesion.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    servicios = Servicio.query.all()
    return render_template("dashboard.html", servicios=servicios)

@app.route("/crear", methods=["POST"])
def crear():
    if "usuario" not in session:
        return redirect(url_for("login"))

    servicio = request.form["servicio"].strip()
    precio = request.form["precio"].strip()

    if not servicio or not precio:
        flash("Todos los campos son obligatorios.", "warning")
    elif len(servicio) > 100:
        flash("El nombre del servicio no puede superar los 100 caracteres.", "danger")
    else:
        try:
            precio = float(precio)
            if precio <= 0:
                flash("El precio debe ser mayor a 0.", "danger")
            else:
                nuevo_servicio = Servicio(servicio=servicio, precio=precio)
                db.session.add(nuevo_servicio)
                db.session.commit()
                flash("Servicio agregado exitosamente.", "success")
        except ValueError:
            flash("El precio debe ser un numero valido.", "danger")

    return redirect(url_for("dashboard"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    servicio_obj = Servicio.query.get(id)
    if request.method == "POST":
        servicio = request.form["servicio"].strip()
        precio = request.form["precio"].strip()

        if not servicio or not precio:
            flash("Todos los campos son obligatorios.", "warning")
        elif len(servicio) > 100:
            flash("El nombre del servicio no puede superar los 100 caracteres.", "danger")
        else:
            try:
                precio = float(precio)
                if precio <= 0:
                    flash("El precio debe ser mayor a 0.", "danger")
                else:
                    servicio_obj.servicio = servicio
                    servicio_obj.precio = precio
                    db.session.commit()
                    flash("Servicio actualizado exitosamente.", "info")
                    return redirect(url_for("dashboard"))
            except ValueError:
                flash("El precio debe ser un numero valido.", "danger")

    return render_template("editar.html", servicio=servicio_obj)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    servicio_obj = Servicio.query.get(id)
    if servicio_obj:
        db.session.delete(servicio_obj)
        db.session.commit()
        flash("Servicio eliminado.", "danger")
    else:
        flash("El servicio no existe.", "warning")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
