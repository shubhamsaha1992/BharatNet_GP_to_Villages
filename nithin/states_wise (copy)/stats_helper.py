
from __future__ import print_function

class LogData:

    def __init__(self, name):
        self.name = name
        self.matched = dict()
        self.unmatched = dict()
        self.unmatched_list = dict()

    def init_field(self, name):
        self.matched[name] = 0
        self.unmatched[name] = 0
        self.unmatched_list[name] = set()

    def clear_all(self):
        for key in  self.matched.iterkeys():
            self.matched[key] = 0
        for key in self.unmatched.iterkeys():
            self.unmatched[key] = 0
        for key in self.unmatched_list.iterkeys():
            self.unmatched_list[key] = set()

    def print_data(self, pfile):
        for key in self.matched.iterkeys():
            print ( (key + '_matched : ' + str(self.matched[key])), file=pfile)
        for key in self.unmatched.iterkeys():
            print (key + '_unmatched : ' + str(self.unmatched[key]), file=pfile)
        for key in self.unmatched_list.iterkeys():
            print (key + '_unmatched_items : ' + str(self.unmatched_list[key]), file=pfile)


class StatsHelper:

    def __init__(self):
        self.local_data = LogData('local')
        self.global_data = LogData('global')
        self.cur_file = ""

    def add_field(self, name, global_need=False):
        self.local_data.init_field(name)
        self.global_data.init_field(name)

    def _clear_log(self):
        self.local_data.clear_all()
        self.local_data.clear_all()

    def matched(self, name, value):
        self.local_data.matched[name] += 1
        self.global_data.matched[name] += 1

    def unmatch(self, name, value):
        self.local_data.unmatched_list[name].add(value)
        self.local_data.unmatched += 1

        self.global_data.unmatched_list[name].add(value)
        self.global_data.unmatched += 1

    def flush_local(self, file_name):
        pass

    def print_global(self, file_name):
        pass

# matched num, unmacthed num, unmatched list -> global