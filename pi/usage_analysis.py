import pandas as pd

class UsageAnalysis():
    class Endpoint():
        def __init__(self, IP):
            self.ip = IP
            self.sent_requests = []
            self.approved_commands = []
            self.bad_requests_count = 0

    def __init__(self):
        self.endpoints = []
        self.mapping_dict = {'ip': None,
                             'sent_requests': None,
                             'approved_commands': None,
                             'bad_requests_count': None
                             }

    def get_endpoint_by_ip(self, ip) -> Endpoint:
        for endpoint in self.endpoints:
            if ip == endpoint.ip:
                return endpoint
        return None

    def request_received(self, src_ip, request, command):
        endpoint = self.get_endpoint_by_ip(src_ip)
        if not endpoint:
            raise LookupError

        endpoint.sent_requests.append(request)
        if command:
            endpoint.approved_commands.append(command)
        else:
            endpoint.bad_requests_count += 1
    def to_excel(self):
        pass