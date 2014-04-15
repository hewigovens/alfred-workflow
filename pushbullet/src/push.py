#!/usr/bin/python

import urllib
import urllib2
import base64
import json
import sys
import urlparse

APIKEY = ""


def get_auth_header():
    basic = base64.urlsafe_b64encode("%s:" % APIKEY)
    auth_header = ("Authorization", "Basic %s" % basic)
    return auth_header


def main():

    # print sys.argv
    action = sys.argv[1]
    if action == 'list':
        req = urllib2.Request("https://api.pushbullet.com/api/devices")
        req.add_header(*get_auth_header())
        response = urllib2.urlopen(req)
        devices = json.load(response)
        xml_output = '''<?xml version="1.0"?>\n<items>\n'''
        for device in devices["devices"]:
            item_format = '''\t<item uid="%s" arg="%s">\n\t<title>%s</title>\n\t<subtitle>%s</subtitle>\n\t<icon>%s</icon>\n</item>\n'''
            arg_to_pass = {'iden': device['iden'], 'title':
                           'Pushed from Alfred', 'body': sys.argv[2]}
            encoded_string = base64.urlsafe_b64encode(json.dumps(arg_to_pass))

            icon_path = None
            if device['extras']['android_version']:
                icon_path = 'mobile.png'
            else:
                icon_path = 'chrome.png'

            xml_output += item_format % (device['iden'],
                                         encoded_string,
                                         device['extras']['model'],
                                         device['extras']['manufacturer'],
                                         icon_path)
        xml_output += '</items>'
        print(xml_output)
    elif action == 'push':
        print sys.argv
        req = urllib2.Request("https://api.pushbullet.com/api/pushes")
        req.add_header(*get_auth_header())

        args = json.loads(base64.urlsafe_b64decode(sys.argv[2]))
        payload = {"device_iden": args["iden"],
                   "title": args["title"]}

        urlparse_result = urlparse.urlparse(args['body'])
        if urlparse_result.scheme:
            payload['type'] = 'link'
            payload['url'] = args['body']
        else:
            payload['type'] = 'note'
            payload['body'] = args['body']

        req.data = urllib.urlencode(payload)
        response = urllib2.urlopen(req)
        resp_json = json.load(response)
        print(resp_json)

if __name__ == '__main__':
    main()
