#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import render_template, session, request, redirect, url_for, flash
from flask.ext import restful
from app import app, api
from rammConnection import connectRAMM
from rammData import getRoughnessData, getRuttingData, getSCRIMData, \
    getMaintenanceData, getRoadsByZone, getRoadNames
import json


def getSecurityZoneRoads(token, zone):
    #method to retrieve a comma separated list of roads which can be used as a filter for roads by security zone
    print 'Getting roads for security zone ' + str(zone)

    data = getRoadsByZone(token=token, zone=zone)

    if len(data['errors']) > 0:
        return []
    else:
        return data['data']


def getRoadsWithName(token, road_list):
    #get a list of all roadnames by road id
    data = getRoadNames(token=token, road_list=road_list)

    if len(data['errors']) > 0:
        print data['errors']
        return []
    else:
        return data['data']


@app.route('/')
@app.route('/index.html')
def index():
    print session
    return render_template('pages/index.html', title='Home',
                           header='Home')


@app.route('/roughness.html')
def roughness():
    if session.get('AUTHENTICATED'):
        if session['AUTHENTICATED'] is True:
            roads = session['road_list']
            road_id = 752
            road_name = '01S-0667'
            start_m = 1200
            end_m = 1700
            road = {'name': road_name, 'start_m': start_m,
                    'end_m': end_m}
            site = session['site']
            path = session['basePath']
            headers = session['headers']

            data = json.dumps(getRoughnessData(
                road_id,
                start_m,
                end_m,
                site,
                path,
                headers,
                ))
            return render_template(
                'pages/roughness.html',
                title='Roughness Charts',
                header='Roughness',
                nav='Roughness',
                roads=roads,
                data=data,
                road=road,
                )
    else:
        return redirect(url_for('ramm_login'))


@app.route('/rutting.html', methods=['GET', 'POST'])
def rutting():
    token = session.get('token')

    if request.method == 'POST':
        #reset the session variables from the submitted values
        form = request.form

        token['road_id'] = form['road_id']
        token['start_m'] = form['start_m']
        token['end_m'] = form['end_m']

    road_id = token['road_id'] if token['road_id'] else 0
    road_name = token['road_id'] if token['road_id'] else 0
    start_m = token['road_id'] if token['road_id'] else 0
    end_m = token['road_id'] if token['road_id'] else 0
    roads = json.dumps(token['roadnames'] if token['roadnames'] else [])

    section = {'road_name': road_name, 'start_m': start_m, 'end_m': end_m}

    data = getRuttingData(token=token['token'], road_id=road_id, start_m=start_m, end_m=end_m)

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
        section=section,
        )


@app.route('/scrim.html')
def scrim():
    if session.get('AUTHENTICATED'):
        if session['AUTHENTICATED'] is True:
            roads = session['road_list']
            road_id = 752
            road_name = '01S-0667'
            start_m = 10000
            end_m = 11000
            road = {'name': road_name, 'start_m': start_m,
                    'end_m': end_m}
            site = session['site']
            path = session['basePath']
            headers = session['headers']

            data = json.dumps(getSCRIMData(
                road_id,
                start_m,
                end_m,
                site,
                path,
                headers,
                ))
            return render_template(
                'pages/scrim.html',
                title='SCRIM Charts',
                header='SCRIM',
                nav='SCRIM',
                roads=roads,
                data=data,
                road=road,
                )
    else:
        return redirect(url_for('ramm_login'))


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
                sz = getSecurityZoneRoads(token=connection.token, zone=security_zone)
                roadnames = getRoadsWithName(token=connection.token, road_list=sz)
                session['token']['sz_roads'] = sz
                session['token']['roadnames'] = roadnames
                session['token']['road_id'] = 0
                session['token']['start_m'] = 0
                session['token']['end_m'] = 0

                session.permanent = False
                session.modified = True

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


@app.route('/mc_maps.html')
def mc_maps():
    if session.get('AUTHENTICATED'):
        if session['AUTHENTICATED'] is True:
            start_date = '2015-06-01'
            end_date = '2015-06-30'
            period = {'start_date': start_date, 'end_date': end_date}
            site = session['site']
            path = session['basePath']
            headers = session['headers']

            data = json.dumps(getMaintenanceData(
                start_date,
                end_date,
                site,
                path,
                headers,
                session['sz_roads']
                ))

            return render_template(
                'pages/mc_maps.html',
                title='Maintenance Activity',
                header='Maintenance Activity',
                nav='Maintenance Activity',
                period=period,
                map_data=data,
                )
    else:
        return redirect(url_for('ramm_login'))


class getDataTest(restful.Resource):

    def get(self, val):
        #session.clear()
        return str(session)

api.add_resource(getDataTest, '/api/map/<int:val>')
