from waybackpy import WaybackMachineCDXServerAPI
from datetime import datetime, timedelta
import requests

class HistoricalSearch:

    def __init__(self, url, user_agent):
        self.url = url
        self.user_agent = user_agent


    def search_snapshot(self, years_ago, filename="snapshot.html"):
        target_date = datetime.now() - timedelta(days=365 * years_ago) 
        year, month, day = target_date.year, target_date.month, target_date.day

        cdx_api = WaybackMachineCDXServerAPI(self.url, self.user_agent)

        snapshot = cdx_api.near(year=year, month=month, day=day)

        if snapshot:
            print(f"Fecha: {snapshot.timestamp}, URL: {snapshot.archive_url}")
            self.download_snapshot(snapshot.archive_url, filename)
        else:
            print(f"No se encontró un snapshot para la fecha {year}-{month}-{day}.")

    def download_snapshot(self, archive_url, filename):
        res = requests.get(archive_url)
        if res.status_code == 200:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(res.text)
                print(f"Documento guardado exitodamente en {filename}")
        else:
            print(f"Error al descargar el snapshot: {res.status_code}")

    def search_snapshots_by_extensions(self, years_ago, days_interval=30, extensions=None, match_type="domain"):
        if extensions is None:
            extensions = ["pdf", "doc", "docx", "ppt", "xls", "xlsx", "txt"]
            today = datetime.now()
            start_period = (today - timedelta(days=365 * years_ago)).strftime("%Y%m%d")
            end_period = (today - timedelta(days=(365*years_ago) - days_interval)).strftime("%Y%m%d")

            cdx_api = WaybackMachineCDXServerAPI(
                url=self.url, user_agent=self.user_agent,
                start_timestamp=start_period, end_timestamp=end_period,
                match_type=match_type
            )

            regex_filter = "(" + "|".join([f".*\\.{ext}$" for ext in extensions]) + ")"
            cdx_api.filters = [f"urlkey : {regex_filter}"]

            snapshots = cdx_api.snapshots()

            for snapshot in snapshots:
                print(f"Fecha: {snapshot.timestamp}, URL: {snapshot.archive_url}")
                

user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
url = "udemy.com"
hsearch = HistoricalSearch(url, user_agent)

# hsearch.search_snapshot(10)
hsearch.search_snapshots_by_extensions()