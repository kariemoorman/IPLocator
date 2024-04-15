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
from geopy.geocoders import Nominatim


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

    def get_address(self, latitude, longitude):
        geolocator = Nominatim(user_agent="IPLocator-App")
        location = geolocator.reverse((latitude, longitude))
        return location.address

    def get_ip_type(self):
        try:
            hostnames = socket.gethostbyaddr(self.ip_address)
            hostname = hostnames[0]
        except (socket.herror, socket.gaierror):
            hostname = None
        try:
            response = requests.get(f"http://ip-api.com/json/{self.ip_address}?fields=58454015")
            ip_data = response.json()
            address = self.get_address(ip_data.get("lat"), ip_data.get("lon"))
            output = {
                "ip": self.ip_address,
                'ip_domain': self.url,
                "hostname": hostname,
                "isp": ip_data.get("isp"),
                "org": ip_data.get("org", None),
                "as": ip_data.get("as"),
                #"continent_code": ip_data.get("continentCode"),
                "dc_region": ip_data.get("regionName"),
                #"district": ip_data.get("district"),
                #"dc_postal_code": ip_data.get("zip"),
                "dc_timezone": ip_data.get("timezone"),
                "dc_latitude": ip_data.get("lat"),
                "dc_longitude": ip_data.get("lon"),
                "dc_address": address,
                #"proxy": ip_data.get("proxy"),
                "is_host": ip_data.get("hosting"),
                #"mobile": ip_data.get("mobile"),
                "is_private" : self.is_private_ip()
            }
        except requests.RequestException:
            ip_data = {}

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
                address = self.get_address(latitude, longitude)
                output = {
                    # 'ip_address': self.ip_address,
                    # 'url': self.url,
                    #'country_code': country_code,
                    #'continent_code': continent_code,
                    #'country': country,
                    'az_timezone': timezone,
                    # 'state': state,
                    #'region_code': region_code,
                    # 'city': city,
                    # 'area_code': area_code,
                    # 'az_postal_code': postal_code,
                    'az_latitude': latitude,
                    'az_longitude': longitude,
                    'az_address': address
                    }
                return output
            except geoip2.errors.AddressNotFoundError:
                return None

    def get_company_data(self): 
        try:
            response = requests.get(f"https://api.ipapi.is?q={self.ip_address}")
            company_data = response.json()
            
            company_info = company_data['company']
            asn = company_data['asn']
            location = company_data['location']

            address = self.get_address(location.get("latitude"), location.get("longitude"))
            
            output = {
                "is_bogon": company_data.get("is_bogon"),
                "is_mobile": company_data.get("is_mobile"),
                "is_crawler": company_data.get("is_crawler"),
                "is_datacenter": company_data.get("is_datacenter"),
                "is_tor": company_data.get("is_tor"),
                "is_proxy": company_data.get("is_proxy"),
                "is_vpn": company_data.get("is_vpn"),
                'is_type': company_info.get('type'),
                'company_org': company_info.get('name'),
                'asn_org': asn.get('org'),
                'company_domain': company_info.get('domain', None),
                'asn_domain': asn.get('domain'),
                'network': company_info.get('network'),
                'route': asn.get('route'),
                'active_status': asn.get('active'),
                'created_date': asn.get('created', None),
                'updated_date': asn.get('updated', None),
                "is_abuser": company_data.get("is_abuser"),
                'company_abuser_score': company_info.get('abuser_score'),
                'asn_abuser_score': asn.get('abuser_score'),
                'company_latitude':  location.get('latitude'),
                'company_longitude': location.get('longitude'),
                'company_timezone': location.get('timezone'),
                'company_address': address
            }
        except requests.RequestException:
            output = {}
        
        return output 
    
    def get_ip_info(self):
        location_data = self.get_location()
        company_data = self.get_company_data()
        type_data = self.get_ip_type()
        self.set_filepath()
        
        if company_data: 
            for key, value in company_data.items():
                type_data[key] = value
                
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
