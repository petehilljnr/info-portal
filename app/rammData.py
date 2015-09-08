#!/usr/bin/python
# -*- coding: utf-8 -*-

from rammConnection import getTable
import datetime
from shapely.wkt import loads, dumps
import math

def getRoughnessData(
    road_id,
    start_m,
    end_m,
    token
    ):
    errors = []

    hsd_rough_hdr = getTable(
        token=token,
        table='hsd_rough_hdr',
        columns=['survey_number', 'survey_desc', 'survey_date']
        )

    hsd_rough_hdr.getData()

    if hsd_rough_hdr.error is True:
        errors.append('hsd_rough_hdr: ' + hsd_rough_hdr.message)

    filters = []
    filters.append({'columnName': 'road_id', 'operator': 'EqualTo',
                   'value': road_id})
    filters.append({'columnName': 'start_m', 'operator': 'LessThan',
                   'value': end_m})
    filters.append({'columnName': 'end_m', 'operator': 'GreaterThan',
                   'value': start_m})

    hsd_rough = getTable(
        token=token,
        table='hsd_rough',
        columns=['start_m', 'survey_number', 'lane', 'naasra', 'latest'],
        filters=filters,
        sorting=[{'order': 'asc', 'columnName': 'start_m'}],
        )

    hsd_rough.getData()

    if hsd_rough.error is True:
        errors.append('hsd_rough: ' + hsd_rough.message)

    d = dict()

    for row in hsd_rough_hdr.data:
        survey_number = row['values'][0]
        datestring = row['values'][2]
        survey_date = datetime.datetime.strptime(datestring,
                '%Y-%m-%dT%H:%M:%S').date().year
        d[survey_number] = [row['values'][1], row['values'][2],
                            survey_date]

    data = []

    for row in hsd_rough.data:
        data.append([row['values'][0], row['values'][2],
                    row['values'][3], row['values'][4], d[row['values'][1]][2]])

    return {'data': data, 'errors': errors}


def getRuttingData(
    road_id,
    start_m,
    end_m,
    token
    ):

    errors = []
    filters = []

    hsd_rutting_hdr = getTable(
        token=token,
        table='hsd_rutting_hdr',
        columns=['survey_number', 'survey_desc', 'survey_date']
        )

    hsd_rutting_hdr.getData()

    if hsd_rutting_hdr.error is True:
        errors.append('hsd_rutting_hdr: ' + hsd_rutting_hdr.message)

    filters.append({'columnName': 'road_id', 'operator': 'EqualTo',
                   'value': road_id})
    filters.append({'columnName': 'start_m', 'operator': 'LessThan',
                   'value': end_m})
    filters.append({'columnName': 'end_m', 'operator': 'GreaterThan',
                   'value': start_m})

    hsd_rutting = getTable(
        token=token,
        table='hsd_rutting',
        columns=[
            'start_m',
            'survey_number',
            'lane',
            'latest',
            'lwp_20',
            'lwp_30',
            'lwp_40',
            'lwp_50',
            'lwp_60',
            'lwp_100',
            'lwp_100plus',
            'lwp_rut_mean',
            'rwp_20',
            'rwp_30',
            'rwp_40',
            'rwp_50',
            'rwp_60',
            'rwp_100',
            'rwp_100plus',
            'rwp_rut_mean',
            ],
        filters=filters,
        sorting=[{'order': 'asc', 'columnName': 'start_m'}],
        )
    hsd_rutting.getData()

    if hsd_rutting.error is True:
        errors.append('hsd_rutting: ' + hsd_rutting.message)

    d = dict()

    for row in hsd_rutting_hdr.data:
        survey_number = row['values'][0]
        datestring = row['values'][2]
        survey_date = datetime.datetime.strptime(datestring,
                    '%Y-%m-%dT%H:%M:%S').date().year
        d[survey_number] = [row['values'][1], row['values'][2],
                            survey_date]

    data = []

    for row in hsd_rutting.data:
        data.append([
            d[row['values'][1]][2],
            row['values'][0],
            row['values'][2],
            row['values'][3],
            row['values'][4],
            row['values'][5],
            row['values'][6],
            row['values'][7],
            row['values'][8],
            row['values'][9],
            row['values'][10],
            row['values'][11],
            row['values'][12],
            row['values'][13],
            row['values'][14],
            row['values'][15],
            row['values'][16],
            row['values'][17],
            row['values'][18],
            row['values'][19],
            ])

    return {'data': data, 'errors': errors}


def getRoadsByZone(token, zone):
    #to get roads by security zone
    errors = []
    roads = getTable(token=token, table='sz_road', columns=['road_id'], filters=[{'columnName': 'sec_zone', 'operator': 'EqualTo', 'value': str(zone)}])
    roads.getData()
    if roads.error is True:
        errors.append('sz_road: ' + roads.message)

    roadIds = ','.join([str(row['values'][0]) for row in roads.data])

    return {'data': roadIds, 'errors': errors}


def getRoadNames(token, road_list):
    errors = []
    data = []
    roads = getTable(token=token, table='roadnames', columns=['road_id', 'road_name'], filters=[{'columnName': 'road_id', 'operator': 'in', 'value': road_list}])
    roads.getData()

    if roads.error is True:
        errors.append('roadnames: ' + roads.message)

    for row in roads.data:
        data.append(row['values'])

    return {'data': data, 'errors': errors}


def getSCRIMData(
    road_id,
    start_m,
    end_m,
    token
    ):
    errors=[]
    filters = []
    filters.append({'columnName': 'road_id', 'operator': 'EqualTo',
                   'value': road_id})
    filters.append({'columnName': 'start_m', 'operator': 'LessThan',
                   'value': end_m})
    filters.append({'columnName': 'end_m', 'operator': 'GreaterThan',
                   'value': start_m})

    skid_resistance = getTable(
        token=token,
        table='skid_resistance',
        columns=[
            'start_m',
            'survey_number',
            'lane',
            'latest',
            'scrim_coeff_left',
            'scrim_coeff_right',
            'seasonal_factor',
            'esc_factor',
            'skid_site',
            ],
        filters=filters,
        sorting=[{'order': 'asc', 'columnName': 'start_m'}]
        )
    skid_resistance.getData()

    skid_resistance_hd = getTable(
        token=token,
        table='skid_resistance_hd',
        columns=['survey_number', 'survey_desc', 'survey_date']
        )

    skid_resistance_hd.getData()

    skid_site = getTable(
        token=token,
        table='skid_site',
        columns=['skid_site', 'scrim_site_il']
        )

    skid_site.getData()

    if skid_resistance.error is True:
        errors.append('skid_resistance: ' + skid_resistance.message)

    if skid_resistance_hd.error is True:
        errors.append('skid_resistance_hd: ' + skid_resistance_hd.message)

    if skid_site.error is True:
        errors.append('skid_site: ' + skid_site.message)


    surveys = dict()
    skid_sites = dict()

    for row in skid_resistance_hd.data:
        survey_number = row['values'][0]
        datestring = row['values'][2]
        survey_date = datetime.datetime.strptime(datestring,
                '%Y-%m-%dT%H:%M:%S').date().year
        surveys[survey_number] = [row['values'][1], row['values'][2],
                                  survey_date]

    for row in skid_site.data:
        site = row['values'][0]
        il = row['values'][1]
        skid_sites[site] = [site, il]

    data = []

    for row in skid_resistance.data:
        data.append([
            surveys[row['values'][1]][2],
            skid_sites[row['values'][8]][1],
            row['values'][0],
            row['values'][2],
            row['values'][3],
            row['values'][4],
            row['values'][5],
            row['values'][6],
            row['values'][7],
            row['values'][8],
            ])

    return {'data': data, 'errors': errors}


def getMaintenanceData(
    start_date,
    end_date,
    token,
    sz_roads,
    ):
    errors=[]
    filters = []
    filters.append({'columnName': 'transaction_date',
                   'operator': 'GreaterEqualThan', 'value': start_date})
    filters.append({'columnName': 'transaction_date',
                   'operator': 'LessEqualThan', 'value': end_date})

    mc_cost = getTable(
        token=token,
        table='mc_cost',
        columns=[
            'cost_group',
            'activity',
            'fault',
            'cost_amount',
            ],
        filters=filters,
        szRoads=sz_roads,
        getGeometry=True
        )

    mc_cost.getData()

    if mc_cost.error is True:
        errors.append('mc_cost: ' + mc_cost.message)

    data = []

    for row in mc_cost.data:
        line = loads(row['values'][4])
        #length = line.length

        #sections = int(math.ceil(length / 200))
        #sections_pc = 1 / (sections + 1)
        #section = 1
        #while (section <= sections):
        point = line.interpolate(0.5, True)
        data.append([
            row['values'][0],
            row['values'][1],
            row['values'][2],
            row['values'][3],
            dumps(point, rounding_precision=0),
            ])
        #  section = section + 1

    return {'data': data, 'errors': errors}
