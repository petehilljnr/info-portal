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
            site='apps.ramm.co.nz',
            basePath='/RammApi6.1/v1/',
            referer='https://test.com',
            ):

        self.authenticateParams = \
            urllib.urlencode({'database': database,
                             'userName': userName,
                             'password': password})

        self.site = site
        self.basePath = basePath
        self.headers = {'Content-type': 'application/json',
                        'referer': referer}
        self.token = ''
        self.message = ''
        self.expiry = None
        self.error = False
        self.getToken()

    def getToken(self):

        # reset the token in case is has already been set

        self.token = ''
        connection = httplib.HTTPSConnection(self.site)

        try:
            connection.request('POST', self.basePath
                               + 'authenticate/login?'
                               + self.authenticateParams, '',
                               self.headers)

            myresp = connection.getresponse()

            response = myresp.read().decode()

            # check the response status from the server

            if myresp.status == 200:  # check credentials  - need to fix this to check for a proper string
                self.token = response.replace('"', '')
                self.message = 'Successfully logged in'

            elif myresp.status == 500:
                self.token = ''
                self.message = \
                    'The server timed out or the server isnt available'
                self.error = True

            elif myresp.status == 401:
                self.token = ''
                self.message = 'Invalid credentials'
                self.error = True

            else:
                self.token = ''
                self.message = \
                    'An unknown response code was received (' \
                    + str(myresp.status) + ')'
                self.error = True

        except:
            self.message = "An internal error has occurred"
            self.error = True

        finally:
            connection.close()
            print self.message


class getTable:

    def __init__(
            self,
            token,
            table,
            columns,
            filters=[],
            getGeometry=False,
            sorting=[],
            szRoads=[],
            site='apps.ramm.co.nz',
            basePath='/RammApi6.1/v1/',
            referer='https://test.com',
            ):

        if len(szRoads) > 0:
            filters.append({'columnName': 'road_id', 'operator': 'in',
                           'value': szRoads})
        self.site = site
        self.basePath = basePath
        self.headers = {'Content-type': 'application/json',
                        'referer': referer,
                        'Authorization': token}

        self.params = {
            'tableName': table,
            'loadType': 'specified',
            'filters': filters,
            'columns': columns,
            'getGeometry': getGeometry,
            'gridSorting': sorting,
            }

        self.paramData = json.dumps(self.params)
        self.data = []
        self.error = False
        self.message = ''
        self.status = 0

    def getData(self):
        connection = httplib.HTTPSConnection(self.site)
        try:
            connection.request('POST', self.basePath + 'data/table',
                               self.paramData, self.headers)
            myresp = connection.getresponse()
            response = myresp.read().decode()

            self.status = myresp.status

            if myresp.status == 200:
                responseData = json.loads(response)
                rows = responseData['rows']
                self.data = rows
                self.message = 'Successfully retrieved data'
                #for debugging, you could set this to true to return all messages
                self.error = False

            elif myresp.status == 500:
                self.message = \
                    'The server timed out or the server isnt available'
                self.error = True

            elif myresp.status == 401:
                self.message = 'Authorization failed'
                self.error = True

            else:
                self.message = \
                    'An unknown response code was received (' \
                    + str(myresp.status) + ')'
                self.error = True

        except:
            self.message = "An internal error has occurred"
            self.error = True

        finally:
            connection.close()
