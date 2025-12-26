# IPLocator

<p align='center'><img src='example/images/ip_locator.png' alt='iplocator' width='75%'></p>


### Description

Use IPLocator to extract metadata including geolocation information from domain names and IPv4 addresses.

---

<details>
<summary><h2>Installation & Use</h2></summary>
 
 <h3>Installation</h3>

- Clone or download .zip of IPLocator python package.
```
git clone https://github.com/kariemoorman/IPLocator.git
```
- Create and activate a virtual environment.
```
cd IPLocator && python -m venv .iploc-venv && source .iploc-venv/bin/activate
```
- Install Dependencies.
```
pip install -r requirements.txt
```

<h3>Uses</h3>

<h4>IPLocator CLI</h4>

- Run IPLocator CLI. 
```
python iplocator.py --ip <ip_address>
python iplocator.py --url <domain_name>
```

<h4>IPLocator Flask Application</h4>

- Start Redis server.
```
brew services start redis
or
redis-server
```
- Run IPLocator Flask application.
```
python IPLocator-App/app.py
```

<h4>IPLocater Flask Application as Docker Container</h4>

- Build & deploy IPLocator application.
```
docker-compose up --build
```
- Check logs.
```
docker logs -f iplocator-local
```
- Stop & remove services. 
```
docker-compose down
```
</details>


---

<h2>Examples</h2>

<h3>IPLocator Application</h3>

```
python IPLocator-App/app.py
```

<p align='center'><img src='example/images/IPLocator.gif' alt='IPLocatorFlaskApp'></p>


<h3>IPLocator Program</h3>

- #### Search by IP Address
```
 python iplocator.py --ip 185.46.85.45
```
<p><img src='example/images/ip-ru.png' alt='ru-geolocation'></p>

```
{
    "ip": "185.46.85.45",
    "hostname": null,
    "domain_name": "Unknown host",
    "isp": "Silverstar Invest Limited",
    "org": "",
    "asin": "AS35624 Silverstar Invest Limited",
    "proxy": true,
    "hosting": false,
    "mobile": false,
    "is_private": false,
    "continent_code": "EU",
    "region": "Moscow",
    "district": "",
    "zip_code": "144700",
    "time_zone": "Europe/Moscow",
    "lat": 55.7558,
    "lon": 37.6173,
    "country_code": "RU",
    "country": "Russia",
    "timezone": "Europe/Moscow",
    "state": null,
    "region_code": null,
    "city": null,
    "area_code": null,
    "postal_code": null,
    "latitude": 55.7386,
    "longitude": 37.6068
}
```

- #### Search by URL
```
python iplocator.py --url www.tiktok.com
```

<p><img src='example/images/ip_tt.png' alt='tiktok-geolocation'></p>

```
{
    "ip": "184.29.143.154",
    "hostname": "a184-29-143-154.deploy.static.akamaitechnologies.com",
    "domain_name": "www.tiktok.com",
    "isp": "Akamai International B.V.",
    "org": "Akamai Technologies, Inc.",
    "asin": "AS20940 Akamai International B.V.",
    "proxy": false,
    "hosting": false,
    "mobile": false,
    "is_private": false,
    "continent_code": "NA",
    "region": "New York",
    "district": "",
    "zip_code": "10118",
    "time_zone": "America/New_York",
    "lat": 40.7123,
    "lon": -74.0068,
    "country_code": "US",
    "country": "United States",
    "timezone": "America/New_York",
    "state": "New York",
    "region_code": "NY",
    "city": "New York",
    "area_code": 501,
    "postal_code": "10118",
    "latitude": 40.7123,
    "longitude": -74.0068
}
```
