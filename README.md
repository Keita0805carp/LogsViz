# LogsViz
### Visualize Server Attack Source from IP
![image](https://user-images.githubusercontent.com/44022415/138573225-181becb8-427f-484d-834a-baf03c699f30.png)


## Requirements
- Python3
- pip
- Linux Server which has `/var/log/auth.log`
- [mapbox](https://www.mapbox.com/) account & API key (Free)

## Install
```bash
git clone https://github.com/Keita0805carp/LogsViz.git
pip3 install -r requirements.txt

# Edit config at main.py
nano/vim/etc... main.py

python3 main.py
```
## How to Use
### Web

- http://{{ YOUR_SERVER }}:9000/
- http://{{ YOUR_SERVER }}:9000/?n={{INT}} (default: 100)

### API
#### Request
```bash
curl {{ YOUR_SERVER }}:9000/api/{{ SECRET@main.py }}
curl {{ YOUR_SERVER }}:9000/api/{{ SECRET@main.py }}?n={{INT}} (default: 100)
```

#### Response
```json
[
  {
    "count": 10
  },
  {
    "Date": "MM/DD",
    "Time": "hh:mm:ss",
    "description": "LOG",
    "id": 1,
    "latitude": "",
    "longitude": "",
    "sourceIP": "",
    "target": "SERVERNAME",
    "targetUser": "USERNAME"
  },
  {
    "Date": "MM/DD",
    "Time": "hh:mm:ss",
    "description": "LOG",
    "id": 2,
    "latitude": "",
    "longitude": "",
    "sourceIP": "",
    "target": "SERVERNAME",
    "targetUser": "USERNAME"
  },
  .
  .
  .
]
```

## Using...
- [flask](https://github.com/pallets/flask)
- [ip-api](https://ip-api.com/)
- [mapbox](https://www.mapbox.com/)
