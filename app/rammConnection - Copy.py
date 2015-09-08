#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import json


class connectRAMM:

    def __init__(
        self,
        database,
        userName,
        password,
        site,
        basePath,
        referer,
        securityZone,
        ):

        self.authenticateParams = \
            urllib.urlencode({'database': database,
                             'userName': userName,
                             'password': password})

        self.site = site
        self.basePath = basePath
        self.refer = referer
        self.headers = {'Content-type': 'application/json',
                        'referer': referer}
        self.token = None
        self.connection = None

        self.AUTHENTICATED = False
        self.CONNECTED = False
        self.securityZone = securityZone
        self.getToken()

    def open(self):
        if not self.CONNECTED:
            self.connection = httplib.HTTPSConnection(self.site)
        else:
            self.close()
            self.connection = httplib.HTTPSConnection(self.site)

        self.CONNECTED = True

    def close(self):
        if self.CONNECTED:
            self.connection.close()
            self.connection = None

        self.CONNECTED = False

    def getToken(self):

        self.token = None
        self.open()
        try:
            self.connection.request('POST', self.basePath
                                    + 'authenticate/login?'
                                    + self.authenticateParams, '',
                                    self.headers)

            myresp = self.connection.getresponse()

            response = myresp.read().decode()

            if myresp.status==200:  # check credentials  - need to fix this to check for a proper string
                self.headers['Authorization'] = str('Bearer '
                        + response.replace('"', ''))
                self.token = response.replace('"', '')
                self.AUTHENTICATED = True
                print 'token: ' + self.token
                params = {
                    'tableName': 'sz_road',
                    'loadType': 'specified',
                    'filters': [{'columnName': 'sec_zone',
                                'operator': 'EqualTo',
                                'value': self.securityZone}],
                    'columns': ['road_id'],
                    }
                paramData = json.dumps(params)
                self.connection.request('POST', self.basePath
                        + 'data/table', paramData, self.headers)
                response = self.connection.getresponse().read().decode()
                responseData = json.loads(response)
                rows = responseData['rows']
                roadIds = ','.join([str(row['values'][0]) for row in rows])
                self.sec_zone_roads = roadIds
            else:
                print 'Invalid credentials'
                self.AUTHENTICATED = False
        finally:
            self.close()


class getTable:

    def __init__(
        self,
        site,
        basePath,
        headers,
        sz_roads,
        table,
        filters,
        columns,
        isLookup,
        getGeometry,
        sorting
        ):

        if isLookup == False:
            filters.append({'columnName': 'road_id', 'operator': 'in', 'value': sz_roads})

        self.params = {
            'tableName': table,
            'loadType': 'specified',
            'filters': filters,
            'columns': columns,
            'getGeometry': getGeometry,
            'gridSorting': sorting
            }
        self.paramData = json.dumps(self.params)
        self.data = None
        self.site = site
        self.headers = headers
        self.basePath = basePath
        self.exceptions = None
        
    def getData(self):
        connection = httplib.HTTPSConnection(self.site)
        try:
            connection.request('POST',
                    self.basePath + 'data/table',
                    self.paramData, self.headers)
            myresp = connection.getresponse()

            response = \
                myresp.read().decode()

            if myresp.status == 200:
                responseData = json.loads(response)
                rows = responseData['rows']
                self.data = rows
            else:
                self.data = []

        finally:
            connection.close()