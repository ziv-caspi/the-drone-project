import datetime
import pandas as pd
import os.path


class UsageAnalysis():
    class Endpoint():
        def __init__(self, IP):
            self.ip = IP
            self.sent_requests = []
            self.approved_commands = []
            self.bad_requests_count = 0

    def __init__(self):
        self.endpoints = []
        self.mapping_list = [
            'ip',
            'sent_requests',
            'approved_commands',
            'bad_requests_count'
        ]


    def get_endpoint_by_ip(self, ip) -> Endpoint:
        for endpoint in self.endpoints:
            if ip == endpoint.ip:
                return endpoint
        return None

    def request_received(self, src_ip, request, command):
        endpoint = self.get_endpoint_by_ip(src_ip)
        
        if not endpoint:
            endpoint = self.Endpoint(src_ip)
            self.endpoints.append(endpoint)

        now = datetime.datetime.now()
        now = now.strftime('%H:%M:%S')

        if command:
            endpoint.approved_commands.append(command)
            endpoint.sent_requests.append((now, request, command))
        else:
            endpoint.sent_requests.append((now, request, 'Not Valid'))
            endpoint.bad_requests_count += 1
    def endpoint_to_dict(self, endpoint):
        map = ['Time', 'Raw', 'Command']
        d = {}
        for i in range(len(map)):
            d[map[i]] = endpoint.sent_requests[i]
        return d

    def dict_to_xl(self, dict, endpoint_ip):
        df = pd.DataFrame(dict)
        writer = pd.ExcelWriter('data/usg_analysis_{0}.xlsx'.format(endpoint_ip), engine='xlsxwriter')
        df.to_excel(writer)
        writer.save()

    def dict_list_to_xl(self, list):
        for dict in list:
            pass
    
    def save_endpoint(self, src_ip):
        endpoint = self.get_endpoint_by_ip(src_ip)
        dict = self.endpoint_to_dict(endpoint)
        print('Dict:', dict)
        self.dict_to_xl(dict, endpoint.ip)



