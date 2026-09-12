import dns.resolver

class DnsResolver:
    def __init__(self, target_domain, record_types):
        self.resolver = dns.resolver.Resolver()
        self.target_domain = target_domain
        self.record_types = record_types

    def resolver_dns(self):
        for record_type in self.record_types:
            try:
                answers = self.resolver.resolve(self.target_domain, record_type)
            except dns.resolver.NoAnswer:
                continue

            print(f"{record_type} registros para {self.target_domain}")
            for data in answers:
                print(f" {data}")
    
