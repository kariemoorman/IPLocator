#!/usr/bin/python3

from flask import Flask, render_template, request, jsonify
import os
import re
import socket
from ip_locator import IPLocator
import logging
from urllib.parse import urlparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

redis_host = os.getenv("REDIS_HOST", "redis")  # default to 'redis'
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_client = Redis(host=redis_host, port=redis_port)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=f"redis://{redis_host}:{redis_port}",
    default_limits=["500 per day", "100 per hour", "10 per minute"]
)

@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    '''
    Rate-Limiting
    '''
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

@app.after_request
def add_security_headers(response):
    # Security Headers: XSS-Protection, MIME-sniffing protection, Strict-Transport-Security (HSTS) protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Content Security Policy
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.openstreetmap.org https://cdnjs.cloudflare.com https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com; style-src 'self' 'unsafe-inline' https://www.openstreetmap.org https://cdnjs.cloudflare.com https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com; img-src 'self' data: https://www.openstreetmap.org https://cdn.rawgit.com https://*.tile.openstreetmap.org https://unpkg.com;"
    response.headers['Content-Security-Policy'] = csp

    # Clickjacking Protection
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.route("/health")
def health():
    return "OK", 200

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     logging.info("Incoming request...")
#     msg = None
#     locator = None
#     if request.method == 'POST':
#         logging.info(f"Received POST request from IP address: {request.remote_addr}.")
#         ip_or_url = request.form['ip_or_url'].strip()
     
#         if not ip_or_url:
#             logging.error(f"Invalid IP address or domain name provided for: {ip_or_url} from {request.remote_addr}. Status Code: 400.")
#             msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
#             ip_info, dc_latitude, dc_longitude, az_latitude, az_longitude, company_latitude, company_longitude = None, None, None, None, None, None, None
#             return render_template('index.html', ip_info=ip_info, dc_latitude=dc_latitude, dc_longitude=dc_longitude, az_latitude=az_latitude, az_longitude=az_longitude, company_latitude=company_latitude, company_longitude=company_longitude, msg=msg)
            
#         logging.info(f"Received input: {ip_or_url}.")
#         parsed_url = urlparse(ip_or_url)
#         hostname = parsed_url.netloc if parsed_url.netloc else parsed_url.path
#         ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
#         if re.match(ipv4_pattern, hostname):
#             logging.info(f"Received valid IPv4 address: {hostname} from {request.remote_addr}.")
#             ip = str(hostname)
#             locator = IPLocator(ip_address=ip)
#         else:
#             try:
#                 logging.info(f"Input does not match IPv4 pattern, attempting DNS resolution for: {hostname} from {request.remote_addr}.")
#                 socket.gethostbyname(hostname)
#                 logging.info(f"Input matches DNS pattern for: {hostname} from {request.remote_addr}.")
#                 url = str(hostname)
#                 locator = IPLocator(url=url)
#             except socket.gaierror:
#                 logging.error(f"Invalid IP address or domain name provided for: {hostname} from {request.remote_addr}. Status Code: 400.")
#                 msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
#                 ip_info, dc_latitude, dc_longitude, az_latitude, az_longitude, company_latitude, company_longitude = None, None, None, None, None, None, None
#                 return render_template('index.html', ip_info=ip_info, dc_latitude=dc_latitude, dc_longitude=dc_longitude, az_latitude=az_latitude, az_longitude=az_longitude, company_latitude=company_latitude, company_longitude=company_longitude, msg=msg)
        
#         if locator: 
#             logging.info("IPLocator object created successfully.")
#             ip_info = locator.get_ip_info()
#             dc_latitude = ip_info.get('dc_latitude')
#             dc_longitude = ip_info.get('dc_longitude')
#             az_latitude = ip_info.get('az_latitude')
#             az_longitude = ip_info.get('az_longitude')
#             company_latitude = ip_info.get('company_latitude')
#             company_longitude = ip_info.get('company_longitude')
            
#         return render_template('index.html', ip_info=ip_info, dc_latitude=dc_latitude, dc_longitude=dc_longitude, az_latitude=az_latitude, az_longitude=az_longitude, company_latitude=company_latitude, company_longitude=company_longitude, msg=msg)
#     logging.info("Rendering index.html")
#     return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    logging.info("Incoming request...")
    msg = None

    if request.method == 'POST':
        ip_or_url = request.form['ip_or_url'].strip()

        if not ip_or_url:
            msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
            return render_template('index.html', msg=msg)

        try:
            parsed_url = urlparse(ip_or_url)
            hostname = parsed_url.netloc if parsed_url.netloc else parsed_url.path

            ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

            if re.match(ipv4_pattern, hostname):
                locator = IPLocator(ip_address=hostname)
            else:
                socket.gethostbyname(hostname)
                locator = IPLocator(url=hostname)

            ip_info = locator.get_ip_info()

            return render_template(
                'index.html',
                ip_info=ip_info,
                msg=msg
            )

        except Exception as e:
            logging.error(e)
            msg = "🚨 Please Enter a Valid IP Address or Domain Name. 🚨"
            return render_template('index.html', msg=msg)

    return render_template('index.html')

@app.route('/api/ip-info', methods=['POST'])
def api_ip_info():
    ip_or_url = request.json.get("ip_or_url", "").strip()

    if not ip_or_url:
        return jsonify({"error": "Invalid input"}), 400

    try:
        parsed_url = urlparse(ip_or_url)
        hostname = parsed_url.netloc if parsed_url.netloc else parsed_url.path

        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

        if re.match(ipv4_pattern, hostname):
            locator = IPLocator(ip_address=hostname)
        else:
            socket.gethostbyname(hostname)
            locator = IPLocator(url=hostname)

        ip_info = locator.get_ip_info()

        return jsonify({
            "dc_latitude": ip_info.get("dc_latitude"),
            "dc_longitude": ip_info.get("dc_longitude"),
            "az_latitude": ip_info.get("az_latitude"),
            "az_longitude": ip_info.get("az_longitude"),
            "company_latitude": ip_info.get("company_latitude"),
            "company_longitude": ip_info.get("company_longitude")
        })

    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Lookup failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
