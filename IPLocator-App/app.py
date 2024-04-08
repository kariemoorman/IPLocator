#!/usr/bin/python3

from flask import Flask, render_template, request
import re
import socket
from ip_locator import IPLocator
import logging

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
redis_client = Redis(host='localhost', port=6379)
limiter = Limiter(get_remote_address, app=app, storage_uri='redis://localhost:6379', default_limits=["500 per day", "100 per hour", "10 per minute"])


@app.route('/', methods=['GET', 'POST'])
def index():
    logging.info("Incoming request...")
    msg = None
    locator = None
    
    if request.method == 'POST':
        logging.info(f"Received POST request from IP address: {request.remote_addr}.")
        ip_or_url = request.form['ip_or_url'].strip()
        
        if not ip_or_url:
            logging.error(f"Invalid IP address or domain name provided for: {ip_or_url} from {request.remote_addr}. Status Code: 400.")
            msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
            ip_info, lat, long, latitude, longitude = None, None, None, None, None
            return render_template('index.html', ip_info=ip_info, lat=lat, long=long, latitude=latitude, longitude=longitude, msg=msg)
        
        logging.info(f"Classifying input value: {ip_or_url} from {request.remote_addr}.")
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, ip_or_url):
            logging.info(f"Received valid IPv4 address: {ip_or_url} from {request.remote_addr}.")
            ip = str(ip_or_url)
            locator = IPLocator(ip_address=ip)
        else:
            try:
                logging.info(f"Input does not match IPv4 pattern, attempting DNS resolution for: {ip_or_url} from {request.remote_addr}.")
                socket.gethostbyname(ip_or_url)
                logging.info(f"Input matches DNS pattern for: {ip_or_url} from {request.remote_addr}.")
                url = str(ip_or_url)
                locator = IPLocator(url=url)
            except socket.gaierror:
                logging.error(f"Invalid IP address or domain name provided for: {ip_or_url} from {request.remote_addr}.")
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
