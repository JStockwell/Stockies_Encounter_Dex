from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from stockies_encounter_dex.auth import login_required
from stockies_encounter_dex.db import get_db

bp = Blueprint('db_view', __name__)

@bp.route('/')
def index():
    db = get_db()

    encounters = db.execute(
        'SELECT pokemon.name, game_id, location_id, chance, max_level, min_level, method, condition'
        ' FROM encounters JOIN pokemon ON pokemon_id = pokemon.id'
        ' ORDER BY pokemon_id ASC'
    ).fetchall()

    games = db.execute(
        'SELECT * FROM games'
    ).fetchall()

    return render_template('db_view/index.html', encounters=encounters, games=games)