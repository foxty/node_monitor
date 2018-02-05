#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2017-12-22
@author: foxty

UI for master node
"""
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from common import dump_json
from master import Agent, NSystemReport, NCPUReport, NMemoryReport, NDiskReport
logging.basicConfig(level=logging.INFO)


_APP = Flask(__name__,
             static_folder='../web/static/',
             static_url_path='/static',
             template_folder='../web/template/')


def calc_daterange(r):
    if r == 'last_hour':
        hours = 1
    elif r == 'last_day':
        hours = 24
    elif r == 'last_week':
        hours = 24*7
    else:
        hours = 1
    end = datetime.now()
    start = end - timedelta(hours=hours)
    return start, end


@_APP.route("/")
def index():
    return render_template('index.html')


@_APP.route('/api/agents', methods=['GET'])
def get_agents():
    agents = Agent.query(orderby='last_msg_at DESC')
    return dump_json(agents)


@_APP.route('/api/agents/<string:aid>')
def get_agent(aid):
    agent = Agent.get_by_id(aid)
    return dump_json(agent)


@_APP.route('/api/agents/<aid>/report/system/<any(last_hour,last_day,last_week):date_range>', methods=['GET'])
def get_agent_sysreports(aid, date_range='last_hour'):
    reports = NSystemReport.query_by_rtime(aid, *calc_daterange(date_range))
    return dump_json(reports)


@_APP.route('/api/agents/<aid>/report/cpu/<any(last_hour,last_day,last_week):date_range>', methods=['GET'])
def get_agent_cpureports(aid, date_range='last_hour'):
    reports = NCPUReport.query_by_rtime(aid, *calc_daterange(date_range))
    return dump_json(reports)


@_APP.route('/api/agents/<aid>/report/memory/<any(last_hour,last_day,last_week):date_range>', methods=['GET'])
def get_agent_memreports(aid, date_range='last_hour'):
    reports = NMemoryReport.query_by_rtime(aid, *calc_daterange(date_range))
    return dump_json(reports)


@_APP.route('/api/agents/<aid>/report/disk/<any(last_hour,last_day,last_week):date_range>', methods=['GET'])
def get_agent_diskreports(aid, date_range='last_hour'):
    reports = NDiskReport.query_by_rtime(aid, *calc_daterange(date_range))
    return dump_json(reports)


def ui_main(host='0.0.0.0', port=8080, debug=False):
    logging.info('starting master ui...')
    _APP.jinja_env.variable_start_string = '{-'
    _APP.jinja_env.variable_end_string = '-}'
    _APP.jinja_env.auto_reload = True
    _APP.config['TEMPLATES_AUTO_RELOAD'] = True
    _APP.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    ui_main(port=8081, debug=True)