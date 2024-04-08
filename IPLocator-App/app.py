#!/usr/bin/python3

from flask import Flask, render_template, request, jsonify
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

@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

@app.after_request
def add_security_headers(response):
    '''
    Security Headers: XSS-Protection, MIME-sniffing protection, Strict-Transport-Security (HSTS) protection
    '''
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.after_request
def add_csp_header(response):
    '''
    Content Security Policy
    '''
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.openstreetmap.org https://cdnjs.cloudflare.com https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com; style-src 'self' 'unsafe-inline' https://www.openstreetmap.org https://cdnjs.cloudflare.com https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com; img-src 'self' data: https://www.openstreetmap.org https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com;"
    response.headers['Content-Security-Policy'] = csp
    return response

@app.after_request
def add_x_frame_options(response):
    '''
    Clickjacking Protection
    '''
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

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
