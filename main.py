import re
import time
import requests
from datetime import datetime
from flask import Flask, jsonify, make_response, render_template, request

# Configuration ##########
PORT = 9000
PATH = '/var/log/auth.log'
TOKEN = "CHANGEME"  # mapbox API Key
SECRET = "abcdefg123456789"  # (Option)LogsViz Secret
##########################
ips = {}


def parse(num):
    id = 0
    parsedJson = [{"count": id}]

    with open(PATH) as f:
        for line in (f.readlines()[num*-1:]):
            id += 1
            list_tmp = line.split()

            tmp = ' '.join(list_tmp[:3])
            date = datetime.strptime(tmp, '%b %d %H:%M:%S').strftime('%m/%d')
            ttime = datetime.strptime(tmp, '%b %d %H:%M:%S').strftime('%X')
            target = list_tmp[3]
            description = ' '.join(list_tmp[4:])

            try:
                ip_regex = r'((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
                ip = re.search(ip_regex, description).group()
            except AttributeError:
                ip = ""

            if ip != "" and ip in ips:
                longitude = ips[ip][0]
                latitude = ips[ip][1]
            elif ip != "" and ip not in ips:
                time.sleep(1)
                url = "http://ip-api.com/json/"
                url = str(url) + str(ip)
                response = requests.get(url)
                jsonData = response.json()
                longitude = str(jsonData['lon'])
                latitude = str(jsonData['lat'])
                ips[ip] = [longitude, latitude]
            else:
                latitude = ""
                longitude = ""

            try:
                user = re.search(r'user .*? ', description).group()
                user = user.split()[1]
            except AttributeError:
                user = ""

            parsedJson_tmp = [
                    {
                        'id': id,
                        'Date': date,
                        'Time': ttime,
                        'target': target,
                        'description': description,
                        'sourceIP': ip,
                        'targetUser': user,
                        'longitude': longitude,
                        'latitude': latitude
                        }
                    ]
            parsedJson += parsedJson_tmp
    parsedJson[0]["count"] = id
    return parsedJson


api = Flask(__name__)


@api.route('/api/<string:key>', methods=["GET"])
def ret_json(key):
    num = request.args.get('n', "100")
    if key == SECRET:
        res = parse(int(num))
    else:
        res = {'status': "error", }
    return make_response(jsonify(res))


@api.route("/", methods=["GET"])
def index():
    param = request.args.get('n', "100")
    return render_template("index.html", param=param, token=TOKEN, secret=SECRET)


if __name__ == "__main__":
    api.run(host='0.0.0.0', port=PORT, debug=True)
