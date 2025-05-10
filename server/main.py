from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import random
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
db = SQLAlchemy(app)

GRID_WIDTH = 20
GRID_HEIGHT = 15

# Флаг для первого запроса
first_request = True


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    x = db.Column(db.Integer, default=0)
    y = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, default=5)
    y = db.Column(db.Integer, default=5)


def setup():
    db.create_all()
    if not Coin.query.first():
        create_new_coin()


def create_new_coin():
    occupied = {(p.x, p.y) for p in Player.query.all()}
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in occupied:
            break
    coin = Coin(x=x, y=y)
    db.session.query(Coin).delete()
    db.session.add(coin)
    db.session.commit()


@app.before_request
def before_request():
    global first_request
    if first_request:
        setup()
        first_request = False


@app.route('/join', methods=['POST'])
def join():
    data = request.json
    name = data.get('name')
    if not name:
        return {"error": "No name provided"}, 400

    existing = Player.query.filter_by(name=name).first()
    if existing:
        return {"id": existing.id}, 200

    x = random.randint(0, GRID_WIDTH - 1)
    y = random.randint(0, GRID_HEIGHT - 1)

    player = Player(name=name, x=x, y=y)
    db.session.add(player)
    db.session.commit()
    return {"id": player.id}, 201


@app.route('/move', methods=['POST'])
def move():
    data = request.json
    pid = data.get('id')
    direction = data.get('direction')

    player = Player.query.get(pid)
    if not player:
        return {"error": "Player not found"}, 404

    dx, dy = 0, 0
    if direction == 'up':
        dy = -1
    elif direction == 'down':
        dy = 1
    elif direction == 'left':
        dx = -1
    elif direction == 'right':
        dx = 1

    new_x = max(0, min(GRID_WIDTH - 1, player.x + dx))
    new_y = max(0, min(GRID_HEIGHT - 1, player.y + dy))

    player.x = new_x
    player.y = new_y

    coin = Coin.query.first()
    if coin and coin.x == new_x and coin.y == new_y:
        player.score += 1
        db.session.delete(coin)
        create_new_coin()

    db.session.commit()
    return {"status": "ok"}


@app.route('/game_state')
def game_state():
    players = Player.query.all()
    coin = Coin.query.first()
    return jsonify({
        "players": [{"id": p.id, "name": p.name, "x": p.x, "y": p.y} for p in players],
        "coin": {"x": coin.x, "y": coin.y} if coin else None
    })


@app.route('/leaderboard')
def leaderboard():
    players = Player.query.order_by(Player.score.desc()).all()
    table = "<h2>Leaderboard</h2><table border='1'><tr><th>Name</th><th>Score</th><th>Time</th></tr>"
    for p in players:
        duration = int(time.time() - p.created_at.timestamp())
        table += f"<tr><td>{p.name}</td><td>{p.score}</td><td>{duration}s</td></tr>"
    table += "</table>"
    return table


@app.route('/about')
def about():
    return render_template_string("""
    <h2>Про меня</h2>
    <p>Я работал с искусственным интеллектом на начальном уровне, изучая основные методы и алгоритмы, но еще не погружался в эту сферу глубоко. Тем не менее, я заинтересован в дальнейшем освоении ИИ и планирую развивать свои навыки в этой области</p>
    """)


if __name__ == '__main__':
    app.run(debug=True)
