import time
from threading import Lock

class MetricsCollector:
    def __init__(self):
        self.lock = Lock()
        self.start_time = time.time()
        self.total_requests = 0
        self.requests_by_endpoint = {}
        self.response_times_all = []
        self.response_times_graphql = []

    def record_request(self,endpoint):
        with self.lock:
            self.total_requests += 1
            if endpoint not in self.requests_by_endpoint:
                self.requests_by_endpoint[endpoint] = 0 
            self.requests_by_endpoint[endpoint] += 1
    
    def record_response_time(self,endpoint,time_ms):
        with self.lock:
            self.response_times_all.append(time_ms)
            if len(self.response_times_all) > 1000:
                self.response_times_all.pop(0)
            if endpoint  == '/graphql':
                self.response_times_graphql.append(time_ms)
                if len(self.response_times_graphql) > 1000:
                    self.response_times_graphql.pop(0)
            
    
    def get_uptime(self):
        return time.time() - self.start_time
    
    def get_average_response_time(self):
        if len(self.response_times_all) > 0:
            avg_response_time = sum(self.response_times_all)/len(self.response_times_all)

            return avg_response_time
        return 0
    def get_graphql_average_response_time(self):
        if self.response_times_graphql:
            average_response_time = sum(self.response_times_graphql)/len(self.response_times_graphql)
            return average_response_time
        return 0
    
        

