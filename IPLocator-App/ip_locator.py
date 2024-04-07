#!/usr/bin/python3

import argparse
import socket
import os
from datetime import datetime
import re
import requests
import ipaddress
import json
import geoip2.database


class IPLocator:
    def __init__(self, url=False, ip_address=False, database='../GeoLite2-City.mmdb'):
        self.url = url
        self.ip_address = ip_address
        self.database = database
        
    def set_filepath(self): 
        data_dir = '__queries'
        os.makedirs(data_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ip = re.sub(r'\.', '', self.ip_address)
        self.output_filepath = f"{data_dir}/{ip}_{timestamp}"
        
    def ip_to_url(self):
        try: 
            hostnames = socket.gethostbyaddr(self.ip_address)
            self.url = hostnames
        except socket.herror as e: 
            self.url = e.args[1]
            
    def url_to_ip(self):
        try:
            ip_address = socket.gethostbyname(self.url)
            self.ip_address = ip_address
        except socket.error as e:
            self.ip_address = e
    
    def is_private_ip(self):
        try:
            ip_obj = ipaddress.ip_address(self.ip_address)
            return ip_obj.is_private
        except ValueError:
            return False

    def get_ip_type(self):
        try:
            hostnames = socket.gethostbyaddr(self.ip_address)
            hostname = hostnames[0]
        except (socket.herror, socket.gaierror):
            hostname = None
        try:
            response = requests.get(f"http://ip-api.com/json/{self.ip_address}?fields=58454015")
            ip_data = response.json()
        except requests.RequestException:
            ip_data = {}
            
        output = {
            "ip": self.ip_address,
             "hostname": hostname,
             'domain_name': self.url,
             "isp": ip_data.get("isp"),
             "org": ip_data.get("org"),
             "asin": ip_data.get("as"),
             "proxy": ip_data.get("proxy"),
             "hosting": ip_data.get("hosting"),
             "mobile": ip_data.get("mobile"),
             "is_private": self.is_private_ip(),
             "continent_code": ip_data.get("continentCode"),
             "region": ip_data.get("regionName"),
             "district": ip_data.get("district"),
             "zip_code": ip_data.get("zip"),
             "time_zone": ip_data.get("timezone"),
             "lat": ip_data.get("lat"),
             "lon": ip_data.get("lon")
        }
        return output
    
    def get_location(self):
        database_path = self.database
        if not self.ip_address and self.url: 
            self.url_to_ip()
        if not self.url and self.ip_address:
            self.ip_to_url() 
        with geoip2.database.Reader(database_path) as reader: 
            try:
                response = reader.city(self.ip_address)
                region_code = response.subdivisions.most_specific.iso_code
                timezone = response.location.time_zone
                area_code = response.location.metro_code
                postal_code = response.postal.code
                country_code = response.country.iso_code
                continent_code = response.continent.code
                country = response.country.name
                state = response.subdivisions.most_specific.name
                city = response.city.name
                latitude = response.location.latitude
                longitude = response.location.longitude
                output = {
                    # 'ip_address': self.ip_address,
                    # 'url': self.url,
                    'country_code': country_code,
                    'continent_code': continent_code,
                    'country': country,
                    'timezone': timezone,
                    'state': state,
                    'region_code': region_code,
                    'city': city,
                    'area_code': area_code,
                    'postal_code': postal_code,
                    'latitude': latitude,
                    'longitude': longitude
                    }
                return output
            except geoip2.errors.AddressNotFoundError:
                return None
            
    def get_ip_info(self):
        location_data = self.get_location()
        type_data = self.get_ip_type()
        self.set_filepath()
        if location_data: 
            for key, value in location_data.items():
                type_data[key] = value
        
        with open(f"{self.output_filepath}.json", 'w') as json_file:
            json.dump(type_data, json_file, indent=4)
        print(f"\nExtracted text saved to: {self.output_filepath}.json\n")
        return type_data

def main():
    parser = argparse.ArgumentParser(description="IP Location Finder")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', '-u', type=str, help="URL")
    group.add_argument('--ip', '-i', type=str, help="IP Address")
    parser.add_argument('--database', type=str, help="Path to GeoLite2 database file", default="GeoLite2-City.mmdb")
    args = parser.parse_args()
    
    locator = IPLocator(url=args.url, ip_address=args.ip, database=args.database)
    locator.get_ip_info()

if __name__ == "__main__":
    main()
