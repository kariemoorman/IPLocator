#!/usr/bin/python3

from flask import Flask, render_template, request
import re
import socket
from ip_locator import IPLocator
import logging

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/', methods=['GET', 'POST'])
def index():
    logging.info("Incoming request...")
    msg = None
    locator = None
    if request.method == 'POST':
        logging.info("Received POST request.")
        ip_or_url = request.form['ip_or_url'].strip()
        logging.info(f"Received input: {ip_or_url}.")
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, ip_or_url):
            logging.info("Input matches IPv4 pattern.")
            ip = str(ip_or_url)
            locator = IPLocator(ip_address=ip)
        else:
            try:
                logging.info("Input does not match IPv4 pattern, attempting DNS resolution.")
                socket.gethostbyname(ip_or_url)
                logging.info("Input matches DNS pattern.")
                url = str(ip_or_url)
                locator = IPLocator(url=url)
            except socket.gaierror:
                logging.error("Invalid IP address or domain name provided.")
                msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
                ip_info, lat, long, latitude, longitude = None, None, None, None, None
                return render_template('index.html', ip_info=ip_info, lat=lat, long=long, latitude=latitude, longitude=longitude, msg=msg)
        
        if locator: 
            logging.info("IPLocator object created successfully.")
            ip_info = locator.get_ip_info()
            lat = ip_info.get('lat')
            long = ip_info.get('long')
            latitude = ip_info.get('latitude')
            longitude = ip_info.get('longitude')
            
        return render_template('index.html', ip_info=ip_info, lat=lat, long=long, latitude=latitude, longitude=longitude, msg=msg)
    logging.info("Rendering index.html")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
