from flask import Flask, render_template, request
import re
import socket
from ip_locator import IPLocator

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    msg = None
    locator = None
    if request.method == 'POST':
        ip_or_url = request.form['ip_or_url'].strip()
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, ip_or_url):
            ip = str(ip_or_url)
            locator = IPLocator(ip_address=ip)
        else:
            try:
                socket.gethostbyname(ip_or_url)
                url = str(ip_or_url)
                locator = IPLocator(url=url)
            except socket.gaierror:
                msg = "🚨 Please Enter a Valid IP Addres or Domain Name. 🚨"
                ip_info, latitude, longitude = None, None, None
                return render_template('index.html', ip_info=ip_info, latitude=latitude, longitude=longitude, msg=msg)
        
        if locator: 
            ip_info = locator.get_ip_info()
            latitude = ip_info.get('lat')
            longitude = ip_info.get('long')
            
        return render_template('index.html', ip_info=ip_info, latitude=latitude, longitude=longitude, msg=msg)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
