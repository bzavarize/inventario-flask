from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
from weasyprint import HTML

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Modelos
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')

    def get_id(self):
        return self.username


class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    patrimonio_arklok = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'patrimonio_arklok': self.patrimonio_arklok,
            'setor': self.setor,
            'hostname': self.hostname
        }


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.filter_by(username=user_id).first()


# Rotas principais
@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        if user and user.senha == senha:
            login_user(user)
            return redirect('/')
        return render_template('login.html', erro='Credenciais inválidas')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Desconectado'})


@app.route('/usuarios', methods=['POST'])
@login_required
def criar_usuario():
    if current_user.role != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403
    data = request.get_json()
    novo_usuario = Usuario(
        username=data['username'],
        senha=data['senha'],
        role=data['role']
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'message': 'Usuário criado com sucesso'})


@app.route('/equipamentos', methods=['GET', 'POST'])
@login_required
def equipamentos():
    if request.method == 'GET':
        setor = request.args.get('setor')
        query = Equipamento.query
        if setor:
            query = query.filter_by(setor=setor)
        equipamentos = query.all()
        return jsonify([e.to_dict() for e in equipamentos])

    if request.method == 'POST':
        if current_user.role != 'admin':
            return jsonify({'message': 'Apenas administradores podem adicionar equipamentos'}), 403
        data = request.get_json()
        novo = Equipamento(
            tipo=data.get('tipo'),
            patrimonio_arklok=data.get('patrimonio_arklok'),
            setor=data.get('setor'),
            hostname=data.get('hostname')
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_dict()), 201


@app.route('/equipamentos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def equipamento_id(id):
    eq = Equipamento.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify(eq.to_dict())

    if request.method == 'PUT':
        if current_user.role != 'admin':
            return jsonify({'message': 'Apenas administradores podem editar'}), 403
        data = request.get_json()
        eq.tipo = data.get('tipo', eq.tipo)
        eq.patrimonio_arklok = data.get('patrimonio_arklok', eq.patrimonio_arklok)
        eq.setor = data.get('setor', eq.setor)
        eq.hostname = data.get('hostname', eq.hostname)
        db.session.commit()
        return jsonify(eq.to_dict())

    if request.method == 'DELETE':
        if current_user.role != 'admin':
            return jsonify({'message': 'Apenas administradores podem excluir'}), 403
        db.session.delete(eq)
        db.session.commit()
        return '', 204


@app.route('/setores', methods=['GET'])
@login_required
def setores():
    setores = db.session.query(Equipamento.setor).distinct().all()
    lista_setores = [s[0] for s in setores if s[0]]
    return jsonify(lista_setores)


@app.route('/relatorio')
@login_required
def relatorio():
    equipamentos = Equipamento.query.all()
    rendered = render_template('relatorio_pdf.html', equipamentos=equipamentos)
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
    return response

@app.route('/relatorio_pdf')
@login_required
def relatorio_pdf():
    # código que gera o PDF
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', senha='admin123', role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com a senha: admin123")
    app.run(debug=True)
