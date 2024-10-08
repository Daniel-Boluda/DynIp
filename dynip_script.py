import logging
import requests
import subprocess
import os
import time
from datetime import datetime

# Configure the logging system to log to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables for secrets
api_token = os.getenv('API_TOKEN')
zone_id = os.getenv('ZONE_ID')
sleep_duration = int(os.getenv('SLEEP_DURATION', 30))  # Default to 30 seconds if not set

# Check if the environment variables are set
if not api_token or not zone_id:
    logging.error("API_TOKEN or ZONE_ID environment variables are not set.")
    exit(1)

# Global variable to store the last known IP
last_known_ip = None

# Function to get the current time
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function to get the external IP
def get_external_ip():
    try:
        output = subprocess.check_output(['curl', '-s', '-4', 'icanhazip.com']).decode('utf-8').strip()
        return output
    except subprocess.CalledProcessError as e:
        logging.error(f'An error occurred while fetching the external IP: {e}')
        return None

# Function to get DNS record
def get_dns_record(api_token, zone_id, domain_name, record_type='A'):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'name': domain_name,
        'type': record_type,
    }
    response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers, params=params)
    if response.status_code == 200:
        records = response.json()['result']
        if records:
            return records[0]  # Return the first record found
    return None

# Function to create or update DNS record
def create_or_update_dns_record(api_token, zone_id, domain_name, new_ip, record_type='A'):
    existing_record = get_dns_record(api_token, zone_id, domain_name, record_type)
    if existing_record:
        if existing_record['content'] == new_ip:
            logging.info(f'{get_current_time()}: DNS record for {domain_name} is up to date')
            return
        record_id = existing_record['id']
        update_dns_record(api_token, zone_id, record_id, domain_name, new_ip, record_type)
    else:
        create_dns_record(api_token, zone_id, domain_name, new_ip, record_type)

# Function to create DNS record
def create_dns_record(api_token, zone_id, domain_name, ip, record_type='A'):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'type': record_type,
        'name': domain_name,
        'content': ip,
        'proxied': False,
        'ttl': 1  # Auto TTL
    }
    response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers, json=data)
    if response.status_code == 200:
        logging.info(f'{get_current_time()}: DNS record for {domain_name} created successfully')
    else:
        logging.error(f'{get_current_time()}: Failed to create DNS record for {domain_name}')

# Function to update DNS record
def update_dns_record(api_token, zone_id, record_id, domain_name, new_ip, record_type='A'):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'type': record_type,
        'name': domain_name,
        'content': new_ip,
        'proxied': False,
        'ttl': 1  # Auto TTL
    }
    response = requests.put(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}', headers=headers, json=data)
    if response.status_code == 200:
        logging.info(f'{get_current_time()}: DNS record for {domain_name} updated successfully with new IP: {new_ip}')
    else:
        logging.error(f'{get_current_time()}: Failed to update DNS record for {domain_name}')

# Main function to run the script
def main():
    global last_known_ip
    domain_name = 'dbcloud.org'

    while True:
        # Retrieve external IP
        new_ip = get_external_ip()
        if new_ip:
            if new_ip != last_known_ip:
                logging.info(f'{get_current_time()}: IP changed from {last_known_ip} to {new_ip}')
                create_or_update_dns_record(api_token, zone_id, domain_name, new_ip)
                create_or_update_dns_record(api_token, zone_id, 'wireguard.dbcloud.org', domain_name, record_type='CNAME')
                last_known_ip = new_ip
            else:
                logging.info(f'{get_current_time()}: IP unchanged: {new_ip}')
        else:
            logging.error(f'{get_current_time()}: Failed to retrieve external IP')
        
        # Wait for the specified duration before the next check
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()