import re
from aprslib.exceptions import ParseError

__all__ = [
    'parse_weather',
    'parse_weather_data',
    ]

key_map = {
    'g': 'wind_gust',
    'c': 'wind_direction',
    't': 'temperature',
    'S': 'wind_speed',
    'r': 'rain_1h',
    'p': 'rain_24h',
    'P': 'rain_since_midnight',
    'h': 'humidity',
    'b': 'pressure',
    'l': 'luminosity',
    'L': 'luminosity',
    's': 'snow',
    '#': 'rain_raw',
}
val_map = {
    'g': lambda x: int(x),
    'c': lambda x: int(x),
    'S': lambda x: int(x),
    't': lambda x: float(x),
    'r': lambda x: int(x),
    'p': lambda x: int(x),
    'P': lambda x: int(x),
    'h': lambda x: 100 if int(x) == 0 else int(x),
    'b': lambda x: float(x),
    'l': lambda x: int(x),
    'L': lambda x: int(x),
    's': lambda x: float(x),
    '#': lambda x: int(x),
}

def parse_weather_data(body):
    parsed = {}

    # parse weather data
    body = re.sub(r"^([0-9]{3})/([0-9]{3})", "c\\1s\\2", body)
    body = body.replace('s', 'S', 1)

    # match as many parameters from the start, rest is comment
    data = re.match(r"^([cSgtrpPlLs#][0-9\-\. ]{3}|h[0-9\. ]{2}|b[0-9\. ]{5})+", body)

    if data:
        data = data.group()
        # split out data from comment
        body = body[len(data):]
        # parse all weather parameters
        data = re.findall(r"([cSgtrpPlLs#]\d{3}|t-\d{2}|h\d{2}|b\d{5}|s\.\d{2}|s\d\.\d)", data)
        data = map(lambda x: (key_map[x[0]] , val_map[x[0]](x[1:])), data)
        parsed.update(dict(data))

    return (body, parsed)

def parse_weather(body):
    match = re.match(r"^(\d{8})c[\. \d]{3}s[\. \d]{3}g[\. \d]{3}t[\. \d]{3}", body)
    if not match:
        raise ParseError("invalid positionless weather report format")

    comment, weather = parse_weather_data(body[8:])

    parsed = {
        'format': 'wx',
        'wx_raw_timestamp': match.group(1),
        'comment': comment.strip(' '),
        'weather': weather,
        }

    return ('', parsed)
