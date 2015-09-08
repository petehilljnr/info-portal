#!/usr/bin/python
# -*- coding: utf-8 -*-
from app import api
from flask.ext import restful


class getDataTest(restful.Resource):

    def get(self,val):
        return str(session)

api.add_resource(getDataTest, '/api/map/<int:val>')
