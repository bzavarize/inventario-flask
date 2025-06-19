from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    patrimonio_arklok = db.Column(db.String(50), nullable=False, unique=True)
    setor = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "patrimonio_arklok": self.patrimonio_arklok,
            "setor": self.setor,
            "hostname": self.hostname
        }
