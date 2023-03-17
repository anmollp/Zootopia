import web
import subprocess
from subprocess import Popen, PIPE
import shlex

urls = (
    '/count?(.+)', 'Count',
    '/addSource?(.+)', 'AddSource',
    '/listSources', 'ListSources',
    '/window?(.+)', 'Window'
)

def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")

active_sources = []
required_list = ["Fungi", "Animalia", "Plantae"]

class Count(object):
    def GET(self, by):
        result = []
        data = web.input()
        by = data.by
        data_dictionary = {}
        text = ""
        if by == "kingdom":
            cat = Popen(["hadoop", "fs", "-cat", "/kingdom/*/*"], stdout=PIPE)
            for line in cat.stdout:
                _, kingdom, records = line.decode().strip("\n").split(",")
                if kingdom in required_list:
                    data_dictionary[kingdom] = int(records) + data_dictionary.get(kingdom, 0)
        elif by == "totalSpecies":
            cat = Popen(["hadoop", "fs", "-cat", "/species/*/*"], stdout=PIPE)
            key = 'Species'
            for line in cat.stdout:
                _, records = line.decode().strip("\n").split(",")
                data_dictionary[key] = int(records) + data_dictionary.get(key, 0)
        elif by == "source":
            cat = Popen(["hadoop", "fs", "-cat", "/kingdom/*/*"], stdout=PIPE)
            for line in cat.stdout:
                x = line.decode().strip("\n").split(",")
                if len(x) == 2:
                    source, records = x[0], x[1]
                elif len(x) == 3:
                    source, records = x[0], x[2]
                data_dictionary[source] = int(records) + data_dictionary.get(source, 0)
        else:
            return web.badrequest(message="Unrecognized parameter '{}'.".format(by))
        result.append(data_dictionary)
        for key, value in data_dictionary.items():
            text += "{:<20} {:<15}\n".format(key, value)
        return text
#        return result

class AddSource:
    def __init__(self):
        self.url_list = ['https://idigbio.org', 'https://gbif.org', 'https://obis.org']
        self.command_list = ['python3 idigbio_producer.py', 'python3 gbif_producer.py', 'python3 obis_producer.py']
        self.bootstrap_servers = ["128.105.144.46:9092", "128.105.144.45:9092", "128.105.144.51:9092"]

    def GET(self, url):
        data = web.input()
        url = data.url
        if url in self.url_list:
            command = None
            if url == self.url_list[0]:
                command = self.command_list[0] + " --bootstrap-servers " + self.bootstrap_servers[0]
                process = Popen(shlex.split(command), shell=False, stderr=subprocess.DEVNULL)
                active_sources.append(self.url_list[0])
                return web.ok("Source {} added".format(url))
            elif url == self.url_list[1]:
                command = self.command_list[1] + " --bootstrap-servers " + self.bootstrap_servers[1]
                process = Popen(shlex.split(command), shell=False, stderr=subprocess.DEVNULL)
                active_sources.append(self.url_list[1])
                return web.ok("Source {} added".format(url))
            elif url == self.url_list[2]:
                command = self.command_list[2] + " --bootstrap-servers " + self.bootstrap_servers[2]
                process = Popen(shlex.split(command), shell=False, stderr=subprocess.DEVNULL)
                active_sources.append(self.url_list[2])
                return web.ok("Source {} added".format(url))
        else:
            return web.badrequest("Unrecognized url")

class ListSources:
    def GET(self):
        text = ""
        for source in active_sources:
            text += "{:<15}\n".format(source)
        return text

class Window:

    def GET(self, id):
        data = web.input()
        window_num = data.id
        data_dictionary = {"Fungi": 0, "Animalia": 0, "Plantae": 0, "Unique Species": 0}
        cat = Popen(["hadoop", "fs", "-cat", "/kingdom/{}/*".format(window_num)], stdout=PIPE)
        for line in cat.stdout:
            _, kingdom, records = line.decode().strip("\n").split(",")
            if kingdom in required_list:
                data_dictionary[kingdom] = int(records) + data_dictionary.get(kingdom, 0)
        cat = Popen(["hadoop", "fs", "-cat", "/species/{}/*".format(window_num)], stdout=PIPE)
        for line in cat.stdout:
            _, records = line.decode().strip("\n").split(",")
            data_dictionary["Unique Species"] = int(records) + data_dictionary.get("Unique Species", 0)
        table = """
-------------------------------------------------------------------------------------------
{:<10}|  {:<17}|  {:<17}|  {:<14}|{:<23}
-------------------------------------------------------------------------------------------
{:<10}|  {:<17}|  {:<17}|  {:<14}|{:<23}
-------------------------------------------------------------------------------------------
""".format("Window #", "Plant Records", "Animal Records", "Fungi Records", "Unique Species Records", window_num, data_dictionary["Plantae"], data_dictionary["Animalia"],
           data_dictionary["Fungi"], data_dictionary["Unique Species"])
        return table

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.notfound = notfound
    app.run()

