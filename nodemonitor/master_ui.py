#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2017-12-22
@author: foxty

UI for master node
"""
import logging
from collections import namedtuple
from datetime import datetime, timedelta
from flask import Flask, render_template
from common import dump_json
from master import Agent, NSystemReport, NCPUReport, NMemoryReport, NDiskReport, \
    SInfo, SInfoHistory, SPidstatReport, SJstatGCReport
logging.basicConfig(level=logging.INFO)


_APP = Flask(__name__,
             static_folder='../web/static/',
             static_url_path='/static',
             template_folder='../web/template/')

JavaGCStat = namedtuple('JavaGCStat', 'category, start_at, end_at, samples, '
                                      'ygc, ygct, avg_ygct, fgc, fgct, avg_fgct, throughput')
JavaMemStat = namedtuple('JavaMemStat', 'category, start_at, end_at, samples')


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


@_APP.route('/api/dashboard/summary')
def dashboard_summary():
    summary = {'agent_count': Agent.count(),
               'service_count': SInfo.count(),
               'alarm_count': 0,
               'sample_count': 0}
    return dump_json(summary)


@_APP.route('/api/agents/by_load1')
def get_agents_byload1():
    agents = Agent.query_by_load1()
    return dump_json(agents)


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


@_APP.route('/api/agents/<string:aid>/services')
def get_agent_services(aid):
    services = SInfo.query_by_aid(aid)
    status_map = {report.service_id: report for report in SPidstatReport.lst_report_by_aid(aid, len(services))}
    return dump_json({'services': services, 'services_status_map': status_map})


@_APP.route('/api/agents/<string:aid>/services/<string:service_id>/<any(last_hour,last_day,last_week):date_range>')
def get_service_info(aid, service_id, date_range):
    service = SInfo.byid(service_id)
    service_history = SInfoHistory.query_by_rtime(service_id, *calc_daterange(date_range))
    return dump_json({'service': service, 'service_history': service_history})


@_APP.route('/api/agents/<aid>/services/<service_id>/report/pidstat/<any(last_hour,last_day,last_week):date_range>',
            methods=['GET'])
def get_service_pidstats(aid, service_id, date_range='last_hour'):
    reports = SPidstatReport.query_by_rtime(service_id, *calc_daterange(date_range))
    return dump_json(reports)


@_APP.route('/api/agents/<aid>/services/<service_id>/report/jstatgc/<any(last_hour,last_day,last_week):date_range>',
            methods=['GET'])
def get_service_jstatgc(aid, service_id, date_range='last_hour'):
    start, end = calc_daterange(date_range)
    reports = SJstatGCReport.query_by_rtime(service_id, start, end)
    # shistory = SInfoHistory.query_by_rtime(service_id, start, end)
    # calculate gc stats and memory stats
    if len(reports) >= 2:
        lastts = 0
        samples = 0
        ygc = 0
        ygct = 0
        fgc = 0
        fgct = 0
        for r in reports:

            pass
    else:
        pass
    gcstat_recent = JavaGCStat(category='recent', )
    return dump_json({'reports': reports})


def ui_main(host='0.0.0.0', port=8080, debug=False):
    logging.info('starting master ui...')
    _APP.jinja_env.variable_start_string = '{-'
    _APP.jinja_env.variable_end_string = '-}'
    _APP.jinja_env.auto_reload = True
    _APP.config['TEMPLATES_AUTO_RELOAD'] = True
    _APP.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    ui_main(port=8081, debug=True)