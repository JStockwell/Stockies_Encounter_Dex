from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from stockies_encounter_dex.auth import login_required
from stockies_encounter_dex.db import get_db

bp = Blueprint('db_view', __name__)

@bp.route('/encounters')
def encounters():
    db = get_db()

    encounters = db.execute(
        'SELECT pokemon_id, pokemon.name, game_id, location_id, chance, max_level, min_level, method, condition'
        ' FROM encounters JOIN pokemon ON pokemon_id = pokemon.id'
        ' ORDER BY pokemon_id ASC'
    ).fetchall()

    games = db.execute(
        'SELECT * FROM games'
    ).fetchall()

    data = [encounters, games]
    return render_template('db_view/encounters.html', data=data)

@bp.route('/version-exclusives')
def version_exclusives():
    db = get_db()

    encounters = db.execute(
        'SELECT *'
        ' FROM version_exclusive_pokemon'
        ' ORDER BY pokemon_id ASC'
    ).fetchall()

    games = db.execute(
        'SELECT * FROM games'
    ).fetchall()

    data = [encounters, games]
    return render_template('db_view/version_exclusives.html', data=data)

@bp.route('/')
def index():
    return render_template('db_view/index.html')