#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import render_template, session, request, redirect, url_for, flash
from flask.ext import restful
from flask.ext.restful import reqparse, Resource
from app import app, api
from rammConnection import connectRAMM
from rammData import getRoughnessData, getRuttingData, getSCRIMData, \
    getMaintenanceData, getRoadsByZone, getRoadNames
import json
import datetime
from datetime import timedelta
import sys


def getPeriod(date):
    """ Function to get a month period prior to the existing month """
    print date
    year, month = divmod(date.month-1, 12)
    if month == 0:
        month = 12
        year = year - 1
    period_start = datetime.datetime(date.year + year, month, 1)

    year, month = divmod(period_start.month+1, 12)
    if month == 0:
        month = 12
        year = year - 1
    period_end = datetime.datetime(period_start.year + year, month, 1) - timedelta(1)

    return (period_start, period_end)


def getSecurityZoneRoads(token, zone):
    #method to retrieve a comma separated list of roads which can be used as a filter for roads by security zone
    print 'Getting roads for security zone ' + str(zone)

    data = getRoadsByZone(token=token, zone=zone)

    if len(data['errors']) > 0:
        return []
    else:
        print 'Size of security zone is ' + str(sys.getsizeof(data['data'])) + ' bytes'
        return data['data']


def getRoadsWithName(token, road_list):
    #get a list of all roadnames by road id
    data = getRoadNames(token=token, road_list=road_list)

    if len(data['errors']) > 0:
        print data['errors']
        return []
    else:
        print 'Size of road names is ' + str(sys.getsizeof(data['data'])) + ' bytes'
        return data['data']


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('pages/index.html', title='Home',
                           header='Home')


@app.route('/roughness.html', methods=['GET', 'POST'])
def roughness():
    token = session.get('token')
    print token['token']
    if request.method == 'POST':
        form = request.form
        session['token']['road_id'] = form['road_id']
        session['token']['start_m'] = form['start_m']
        session['token']['end_m'] = form['end_m']

    road_id = session['token']['road_id'] if session['token']['road_id'] else 0
    start_m = session['token']['start_m'] if session['token']['start_m'] else 0
    end_m = session['token']['end_m'] if session['token']['end_m'] else 0

    roads = session['token']['roadnames'] if session['token']['roadnames'] else 0
    road_name = '(not selected)'

    #find the correct road name
    for r in roads:
        if str(r[0]) == str(road_id):
            road_name = r[1]
            break

    section = {'road_name': str(road_name), 'road_id': road_id, 'start_m': start_m, 'end_m': end_m}
    data = getRoughnessData(token=token['token'], road_id=str(road_id), start_m=str(start_m), end_m=str(end_m))

    #add all errors from the data retrieval from to the flashed messages queue
    if len(data['errors']) > 0:
        for e in data['errors']:
            flash(e)

    return render_template(
        'pages/roughness.html',
        title='Roughness Charts',
        header='Roughness',
        nav='Rutting',
        roads=roads,
        data=json.dumps(data['data']),
        section=section
        )


@app.route('/rutting.html', methods=['GET', 'POST'])
def rutting():
    token = session.get('token')

    if request.method == 'POST':
        form = request.form
        session['token']['road_id'] = form['road_id']
        session['token']['start_m'] = form['start_m']
        session['token']['end_m'] = form['end_m']

    road_id = session['token']['road_id'] if session['token']['road_id'] else 0
    start_m = session['token']['start_m'] if session['token']['start_m'] else 0
    end_m = session['token']['end_m'] if session['token']['end_m'] else 0

    roads = session['token']['roadnames'] if session['token']['roadnames'] else 0
    road_name = '(not selected)'

    #find the correct road name
    for r in roads:
        if str(r[0]) == str(road_id):
            road_name = r[1]
            break

    section = {'road_name': str(road_name), 'road_id': road_id, 'start_m': start_m, 'end_m': end_m}
    data = getRuttingData(token=token['token'], road_id=str(road_id), start_m=str(start_m), end_m=str(end_m))

    #add all errors from the data retrieval from to the flashed messages queue
    if len(data['errors']) > 0:
        for e in data['errors']:
            flash(e)

    return render_template(
        'pages/rutting.html',
        title='Rutting Charts',
        header='Rutting',
        nav='Rutting',
        roads=roads,
        data=json.dumps(data['data']),
        section=section
        )


@app.route('/scrim.html', methods=['GET', 'POST'])
def scrim():
    token = session.get('token')
    print token['token']
    if request.method == 'POST':
        form = request.form
        session['token']['road_id'] = form['road_id']
        session['token']['start_m'] = form['start_m']
        session['token']['end_m'] = form['end_m']

    road_id = session['token']['road_id'] if session['token']['road_id'] else 0
    start_m = session['token']['start_m'] if session['token']['start_m'] else 0
    end_m = session['token']['end_m'] if session['token']['end_m'] else 0

    roads = session['token']['roadnames'] if session['token']['roadnames'] else 0
    road_name = '(not selected)'

    #find the correct road name
    for r in roads:
        if str(r[0]) == str(road_id):
            road_name = r[1]
            break

    section = {'road_name': str(road_name), 'road_id': road_id, 'start_m': start_m, 'end_m': end_m}
    data = getSCRIMData(token=token['token'], road_id=str(road_id), start_m=str(start_m), end_m=str(end_m))

    #add all errors from the data retrieval from to the flashed messages queue
    if len(data['errors']) > 0:
        for e in data['errors']:
            flash(e)

    return render_template(
        'pages/scrim.html',
        title='SCRIM Charts',
        header='SCRIM',
        nav='SCRIM',
        roads=roads,
        data=json.dumps(data['data']),
        section=section
        )


@app.route('/ramm_login.html', methods=['GET', 'POST'])
def ramm_login():
    database = ''
    username = ''
    password = ''
    security_zone = ''

    # see if we are submitting login data
    if request.method == 'POST':
        #clear the existing session
        form = request.form
        database = form['database']
        username = form['username']
        password = form['password']
        security_zone = form['security_zone']

        # check all the fields are filled in to use the RAMM API
        if database and not database.isspace() and username and not username.isspace() and password and not password.isspace() and security_zone and not security_zone.isspace():
        # use the RAMM API class called connectRAMM from rammConnection.py to check credentials
            connection = connectRAMM(
                database,
                username,
                password
                )

            #if no errors occur - then the connection was a success and we have received a token which we will use as authentication from now on
            if connection.error is False:
                session.clear()
                session['token'] = {}
                session['token']['token'] = connection.token
                print connection.token
                sz = getSecurityZoneRoads(token=connection.token, zone=security_zone)
                roadnames = getRoadsWithName(token=connection.token, road_list=sz)
                session['token']['sz_roads'] = sz
                session['token']['roadnames'] = roadnames
                session['token']['road_id'] = 0
                session['token']['start_m'] = 0
                session['token']['end_m'] = 0
                today = datetime.date.today()
                periods = getPeriod(today)
                session['token']['start_date'] = str(periods[0].date())
                session['token']['end_date'] = str(periods[1].date())

                session.permanent = False
                session.modified = True

                #print session

                return redirect(url_for('index'))  # login was successful - go to the index page
            else:
                flash(connection.message)
                print connection.message

        else:
            flash('All fields must be filled out')

    return render_template(
        'pages/ramm_login.html',
        title='Login',
        header='Login',
        nav='RAMM Login',
        database=database,
        security_zone=security_zone,
        username=username,
        password=password
        )


@app.route('/mc_maps.html', methods=['GET', 'POST'])
def mc_maps():
    token = session.get('token')

    if request.method == 'POST':
        form = request.form
        session['token']['start_date'] = datetime.datetime.strptime(form['start_date'], "%d/%m/%Y").strftime("%Y-%m-%d")
        session['token']['end_date'] = datetime.datetime.strptime(form['end_date'], "%d/%m/%Y").strftime("%Y-%m-%d")

    start_date = session['token']['start_date'] if session['token']['start_date'] else '2015-12-25'
    end_date = session['token']['end_date'] if session['token']['end_date'] else '2015-12-25'
    roads = session['token']['sz_roads'] if session['token']['sz_roads'] else '0'
    data = getMaintenanceData(token=token['token'], start_date=start_date, end_date=end_date, sz_roads=roads)

    #add all errors from the data retrieval from to the flashed messages queue
    if len(data['errors']) > 0:
        for e in data['errors']:
            flash(e)

    return render_template(
        'pages/mc_maps.html',
        title='Maintenance Activity',
        header='Maintenance Activity',
        nav='Maintenance Activity',
        map_data=json.dumps(data['data']),
        start_date=start_date,
        end_date=end_date
        )


class getDataTest(Resource):

    def get(self, start_date, end_date):

        token = session.get('token')
        roads = session['token']['sz_roads'] if session['token']['sz_roads'] else '0'
        data = getMaintenanceData(token=token['token'], start_date=start_date, end_date=end_date, sz_roads=roads)

        #add all errors from the data retrieval from to the flashed messages queue
        if len(data['errors']) > 0:
            for e in data['errors']:
                flash(e)

        return data

api.add_resource(getDataTest, '/api/mc_data/<string:start_date>/<string:end_date>')
