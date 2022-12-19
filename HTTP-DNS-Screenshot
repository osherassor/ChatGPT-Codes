import os
import socket
import requests
import selenium
from selenium import webdriver

# This function takes an IP address as input and returns a list of hostnames
# for that IP address by querying a few different sources
def get_reverse_dns(ip):
    hostnames = []

    # Query the first source
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        if "." in hostname:  # Validate that the result is a domain name
            hostnames.append(hostname)
    except:
        pass

    # Query the second source
    try:
        hostname = socket.gethostbyname(ip)
        if "." in hostname:  # Validate that the result is a domain name
            hostnames.append(hostname)
    except:
        pass

    # Query the third source
    try:
        response = requests.get(f"http://api.hackertarget.com/reverseiplookup/?q={ip}")
        hostnames += response.text.split("\n")
    except:
        pass

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
def take_screenshot(ip, port, protocol):
    # Set up Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)

    # Navigate to the website and take the screenshot
    url = f"{protocol}://{ip}:{port}"
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.close()

    # Save the screenshot to the specified directory
    filename = f"{ip}_{port}_{protocol}.png"
    path = r"c:\tmp\screenshots"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), "wb") as f:
        f.write(screenshot)

# This is the main function that puts everything together
def main():
    # Read the list of IP addresses from the file
    with open("ips.txt", "r") as f:
        ips = f.read().split("\n")

    # For each IP address, get the list of hostnames and check accessibility
    # using different protocols and ports
    for ip in ips:
        hostnames = get_reverse_dns(ip)
        hostnames.append(ip)  # Add the IP itself to the hostnames list
        for hostname in hostnames:
            for port in [80, 443, 8080, 8443]:
                for protocol in ["http", "https"]:
                    if website_accessible(hostname, port, protocol):
                        print(f"{hostname}:{port} ({protocol}) is accessible")
                        try:
                            take_screenshot(hostname, port, protocol)
                        except:
                            print(f"Failed to take screenshot of {hostname}:{port} ({protocol})")
                    else:
                        print(f"{hostname}:{port} ({protocol}) is not accessible")

if __name__ == "__main__":
    main()
