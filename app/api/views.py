from flask import render_template, session, redirect, url_for, request, jsonify
from . import api
from flask.ext.login import login_user, logout_user, login_required
from ..models import Contest

@api.route('/contest', methods=['GET'])
def get_contest():
	contests = Contest.query.all()
	return jsonify({'contests' : [contest.to_json() for contest in contests] })