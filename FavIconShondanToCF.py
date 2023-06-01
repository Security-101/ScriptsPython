# This Python code performs a search for hosts in Shodan that share the same favicon as a specified website
# by user. Next, it tries to get the actual IP address behind Cloudflare of the host that matches the
# favicon by using a reverse DNS resolution technique.
# Next, I will explain in detail the parts of the code:
# import - Import the necessary modules for the program to work, including mmh3 to generate a hash of the favicon,
# requests to make HTTP requests, codecs to encode and decode data, and shodan to access the Shodan API.
#
# SHODAN_API_KEY - The Shodan API key used to query the Shodan API.
#
# main() - The main function of the program. Check if a hostname is provided, look for the favicon on the site
# web specified, generates a hash of the favicon, queries the Shodan API to find hosts with
# the same favicon hash and finally get the actual IP address of the host behind Cloudflare.
#
# get_favicon(favicon_url) - The function that is responsible for downloading the favicon of the specified website.
#
# if __name__ == '__main__': - The line of code that starts the execution of the program.

# In short, this code is an example of how you can use the Shodan API and problem solving techniques
# Reverse DNS to get the real IP address behind Cloudflare of a website and find hosts that share the
# same favicon. However, it is important to note that this technique does not always work and that there may be other measures
# protections that prevent the real IP address of the origin server from being discovered.


import mmh3
import requests
import codecs
import sys
import shodan

SHODAN_API_KEY = "YOUR_API_KEY"

def main():
    if len(sys.argv) < 2:
        print("[!] Error!")
        print(f"[-] Use: python3 {sys.argv[0]} <hostname>")
        sys.exit()

    # Buscar favicon en el host especificado
    favicon_url = f"http://{sys.argv[1]}/favicon.ico"
    favicon_data = get_favicon(favicon_url)
    if not favicon_data:
        print("[!] Error!")
        print(f"[-] No se pudo obtener el favicon desde {favicon_url}")
        sys.exit()

    print(f"[+] Favicon data: {favicon_data}")
    favicon = codecs.encode(favicon_data, "base64")
    print(f"[+] Encoded favicon: {favicon}")
    hash_favicon = mmh3.hash(favicon)
    print(f"[+] Favicon hash: {hash_favicon}")

    # Realizar consulta a Shodan para encontrar hosts con el mismo favicon
    api = shodan.Shodan(SHODAN_API_KEY)
    query = f"http.favicon.hash:{hash_favicon}"
    print(f"[+] Shodan query: {query}")
    results = api.search(query)

    # Obtener dirección IP real del host detrás de Cloudflare
    for result in results["matches"]:
        ip = result["ip_str"]
        headers = {"Host": sys.argv[1]}
        url = f"http://{ip}/favicon.ico"
        try:
            response = requests.get(url, headers=headers, verify=False, proxies={"http": "http://127.0.0.1:8080"})
            print(f"[+] Response status code: {response.status_code}")
            if response.status_code == 200 and response.content == favicon_data:
                print(f"[+] Hostname: {sys.argv[1]}")
                print(f"[+] IP address: {ip}")
                break
        except:
            pass

def get_favicon(favicon_url):
    try:
        response = requests.get(favicon_url, verify=False, proxies={"http": "http://127.0.0.1:8080"})
        print(f"[+] Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.content
    except:
        pass

if __name__ == '__main__':
    main()

