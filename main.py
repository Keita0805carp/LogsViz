import re
import time
import requests
from datetime import datetime
from flask import Flask, jsonify, make_response, render_template, request

# Configuration ##########
PORT = 9000
TOKEN = "CHANGEME"  # mapbox API Key
PATH = '/var/log/auth.log'  # On Docker, do not edit!
SECRET = "abcdefg123456789"  # (Option)LogsViz Secret
##########################

app = Flask(__name__)
ips = {}
ipv6_regex = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
ipv4_regex = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'


def parse(num):
    start_time = time.time()
    app.logger.info("API is Called. Parsing...")
    cntTotal = 0
    cntKnownIP = 0
    cntNewIP = 0
    cntNullIP = 0

    parsedJson = [{"count": cntTotal}]
    with open(PATH) as f:
        for line in (f.readlines()[num*-1:]):
            cntTotal += 1
            list_tmp = line.split()

            tmp = ' '.join(list_tmp[:3])
            date = datetime.strptime(tmp, '%b %d %H:%M:%S').strftime('%m/%d')
            ttime = datetime.strptime(tmp, '%b %d %H:%M:%S').strftime('%X')
            target = list_tmp[3]
            description = ' '.join(list_tmp[4:])

            ip = checkIP(description)

            if ip != "" and ip in ips:
                cntKnownIP += 1
                longitude = ips[ip][0]
                latitude = ips[ip][1]
            elif ip != "" and ip not in ips:
                cntNewIP += 1
                time.sleep(1)
                url = "http://ip-api.com/json/"
                url = url + str(ip)
                response = requests.get(url)
                try: 
                    jsonData = response.json()
                    longitude = jsonData["lon"]
                    latitude = jsonData["lat"]
                    ips[ip] = [longitude, latitude]
                except KeyError as e:
                    app.logger.info("Key Error. Skip...")
                    pass
                except Exception as e:
                    app.logger.info("Parse Error. Skip...")
                    pass
            else:
                cntNullIP += 1
                latitude = ""
                longitude = ""

            try:
                user = re.search(r'user .*? ', description).group()
                user = user.split()[1]
            except AttributeError:
                user = ""

            parsedJson_tmp = [
                    {
                        'id': cntTotal,
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
    parsedJson[0]["count"] = cntTotal
    app.logger.info("Total    : " + str(cntTotal))
    app.logger.info("Known IPs: " + str(cntKnownIP))
    app.logger.info("New IPs  : " + str(cntNewIP))
    app.logger.info("Null IPs : " + str(cntNullIP))
    app.logger.info("Response Time: %s" % (time.time() - start_time))
    return parsedJson


def checkIP(description):
    ip = re.search(ipv6_regex, description)
    if ip != None:
        ip = ip.group()
        return ip
    ip = re.search(ipv4_regex, description)
    if ip != None:
        ip = ip.group()
        return ip
    else:
        ip = ""
        return ip




@app.route('/api/<string:key>', methods=["GET"])
def ret_json(key):
    num = request.args.get('n', "100")
    if key == SECRET:
        res = parse(int(num))
    else:
        res = {'status': "error", }
    return make_response(jsonify(res))


@app.route("/", methods=["GET"])
def index():
    param = request.args.get('n', "100")
    return render_template("index.html", param=param, token=TOKEN, secret=SECRET)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
