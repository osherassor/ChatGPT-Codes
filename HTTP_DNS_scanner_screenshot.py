import os
import socket
import requests
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import ipaddress
import threading


# This function takes an IP address as input and returns a list of hostnames
# for that IP address by querying a few different sources
def get_reverse_dns(ip):
    hostnames = set()  # Use a set to store the hostnames

    # Query the first source
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        if "." in hostname:  # Validate that the result is a domain name
            hostnames.add(hostname)  # Add the hostname to the set
    except:
        pass

    # Query the second source
    try:
        hostname = socket.gethostbyname(ip)
        if "." in hostname:  # Validate that the result is a domain name
            hostnames.add(hostname)  # Add the hostname to the set
    except:
        pass

    # Query the third source
    try:
        response = requests.get(f"http://api.hackertarget.com/reverseiplookup/?q={ip}")
        results = response.text.split("\n")
        for result in results:
            if "." in result:
                hostnames.add(result)  # Add the hostname to the set
    except:
        pass
    # Convert the set to a list and return the list of hostnames
    hostnames = list(hostnames)
    print(hostnames)
    return hostnames

# This function takes an IP address, a port, and a protocol as input and returns
# a boolean indicating whether the website at that IP and port is accessible
# using the specified protocol
def website_accessible(ip, port, protocol):
    url = f"{protocol}://{ip}:{port}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code in [200, 301, 302, 403]
    except:
        return False

# This function takes an IP address, a port, and a protocol as input and takes
# a screenshot of the website at that IP and port using the specified protocol
def take_screenshot(ip, port, protocol, response_code):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Navigate to the website and take the screenshot
    url = f"{protocol}://{ip}:{port}"
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.close()

    # Save the screenshot to the specified directory
    filename = f"{ip}_{port}_{protocol}_{response_code}.png"
    path = r"c:\tmp\screenshots"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), "wb") as f:
        f.write(screenshot)

def check_accessibility(url, accessible_urls):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code in [200, 301, 302, 403]:
            print(f"\033[32m{url} is accessible (status code: {response.status_code})\033[0m")
            # Add the URL to the set of accessible URLs
            accessible_urls.add(url)
            try:
                ip, port, protocol = url.split("://")[1].split(":")
                take_screenshot(ip, port, protocol, response.status_code)
            except:
                pass
        else:
            print(f"\033[31m{url} is not accessible (status code: {response.status_code})\033[0m")
    except:
        print(f"\033[31m{url} is not accessible\033[0m")

# This is the main function that puts everything together
def main():
    # Read the list of IP addresses or network ranges from the file
    with open("ips.txt", "r") as f:
        ips = f.read().split("\n")

    # Create a set to store the accessible URLs
    accessible_urls = set()

    # For each IP address or network range, get the list of hostnames and check
    # accessibility using different protocols and ports
    for ip in ips:
        # If the IP is a network range, generate a list of all the host IP addresses in the range
        if "/" in ip:
            ip_range = ipaddress.ip_network(ip)
            ip_list = [str(ip) for ip in ip_range.hosts()]
        else:
            ip_list = [ip]

        for ip in ip_list:
            hostnames = get_reverse_dns(ip)
            hostnames.append(ip)  # Add the IP itself to the hostnames list
            threads = []
            for hostname in hostnames:
                for port in [80, 443, 8080, 8443]:
                    for protocol in ["http", "https"]:
                        url = f"{protocol}://{hostname}:{port}"
                        # Create a new thread to check the accessibility of the website
                        t = threading.Thread(target=check_accessibility, args=(url, accessible_urls))
                        threads.append(t)
                        t.start()
            # Wait for all the threads to complete
            for t in threads:
                t.join()

    # Convert the set to a list and print the list of accessible URLs
    accessible_urls = list(accessible_urls)
    print("\nAccessible URLs:")
    for url in accessible_urls:
        print(url)

if __name__ == "__main__":
    main()
