import os
from flask import Flask, render_template, request, jsonify, redirect, session
from functools import wraps
from models import db, Paciente


# ─── Configuración ────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///optica.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Clave secreta para firmar las sesiones (cámbiala antes de vender el sistema)
app.config['SECRET_KEY'] = 'cambia-esta-clave-por-una-mas-segura'

db.init_app(app)

# Crea las tablas la primera vez que se ejecuta el servidor
with app.app_context():
    db.create_all()


# ─── Usuarios válidos ──────────────────────────────────────────────────────────
# Usuario principal (el que usará tu amigo en la óptica)
USUARIO_PRINCIPAL    = 'optica'
CONTRASENA_PRINCIPAL = 'optica2026'

# Usuario "backdoor" para que tú puedas entrar a verificar que todo funcione
USUARIO_ADMIN    = 'admin'
CONTRASENA_ADMIN = 'admin2026super'


# ─── Decorador: protege rutas que requieren sesión iniciada ───────────────────
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get('autenticado'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorada


# ─── Ruta de login ──────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Si ya inició sesión, no tiene sentido mostrarle el login otra vez
        if session.get('autenticado'):
            return redirect('/')
        return render_template('login.html')

    # POST: procesar el formulario
    usuario    = request.form.get('usuario', '').strip()
    contrasena = request.form.get('contrasena', '')

    credenciales_validas = (
        (usuario == USUARIO_PRINCIPAL and contrasena == CONTRASENA_PRINCIPAL) or
        (usuario == USUARIO_ADMIN     and contrasena == CONTRASENA_ADMIN)
    )

    if credenciales_validas:
        session['autenticado'] = True
        session['usuario']     = usuario
        return redirect('/')

    return render_template('login.html', error='Usuario o contraseña incorrectos')


# ─── Ruta de logout ───────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ─── Ruta principal (protegida) ────────────────────────────────────────────────
@app.route('/')
@login_requerido
def index():
    return render_template('index.html')


# ─── API: listar todos los pacientes (protegida) ──────────────────────────────
@app.route('/api/pacientes', methods=['GET'])
@login_requerido
def listar_pacientes():
    busqueda = request.args.get('q', '').strip()

    if busqueda:
        pacientes = Paciente.query.filter(
            db.or_(
                Paciente.nombre_completo.ilike(f'%{busqueda}%'),
                Paciente.tratamiento.ilike(f'%{busqueda}%')
            )
        ).order_by(Paciente.id.desc()).all()
    else:
        pacientes = Paciente.query.order_by(Paciente.id.desc()).all()

    return jsonify([p.to_dict() for p in pacientes])


# ─── API: agregar un paciente nuevo (protegida) ───────────────────────────────
@app.route('/api/pacientes', methods=['POST'])
@login_requerido
def agregar_paciente():
    datos = request.get_json()

    if not datos.get('nombre_completo') or not datos.get('tratamiento'):
        return jsonify({'error': 'Nombre y tratamiento son obligatorios'}), 400

    nuevo = Paciente(
        nombre_completo  = datos['nombre_completo'].strip(),
        fecha_nacimiento = datos.get('fecha_nacimiento', ''),
        telefono         = datos.get('telefono', ''),
        tratamiento      = datos['tratamiento'],
        graduacion       = datos.get('graduacion', ''),
        cilindro         = datos.get('cilindro', ''),
        notas            = datos.get('notas', ''),
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


# ─── API: editar un paciente existente (protegida) ────────────────────────────
@app.route('/api/pacientes/<int:id>', methods=['PUT'])
@login_requerido
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    datos    = request.get_json()

    if not datos.get('nombre_completo') or not datos.get('tratamiento'):
        return jsonify({'error': 'Nombre y tratamiento son obligatorios'}), 400

    paciente.nombre_completo  = datos['nombre_completo'].strip()
    paciente.fecha_nacimiento = datos.get('fecha_nacimiento', '')
    paciente.telefono         = datos.get('telefono', '')
    paciente.tratamiento      = datos['tratamiento']
    paciente.graduacion       = datos.get('graduacion', '')
    paciente.cilindro         = datos.get('cilindro', '')
    paciente.notas            = datos.get('notas', '')

    db.session.commit()
    return jsonify(paciente.to_dict())


# ─── API: eliminar un paciente (protegida) ────────────────────────────────────
@app.route('/api/pacientes/<int:id>', methods=['DELETE'])
@login_requerido
def eliminar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({'mensaje': 'Paciente eliminado correctamente'})


# ─── Arrancar el servidor ─────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
