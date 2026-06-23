from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id               = db.Column(db.Integer, primary_key=True)
    nombre_completo  = db.Column(db.String(150), nullable=False)
    fecha_nacimiento = db.Column(db.String(20),  nullable=True)
    telefono         = db.Column(db.String(30),  nullable=True)
    tratamiento      = db.Column(db.String(80),  nullable=False)
    graduacion       = db.Column(db.String(100), nullable=True)
    cilindro         = db.Column(db.String(100),  nullable=True)
    notas            = db.Column(db.Text,         nullable=True)
    fecha_registro   = db.Column(db.String(30),  default=lambda: datetime.now().strftime('%Y-%m-%d'))

    def to_dict(self):
        """Convierte el objeto a diccionario para enviarlo como JSON."""
        return {
            'id':               self.id,
            'nombre_completo':  self.nombre_completo,
            'fecha_nacimiento': self.fecha_nacimiento or '',
            'telefono':         self.telefono or '',
            'tratamiento':      self.tratamiento,
            'graduacion':       self.graduacion or '',
            'cilindro':         self.cilindro or '',
            'notas':            self.notas or '',
            'fecha_registro':   self.fecha_registro or '',
        }
