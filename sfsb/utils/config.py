import yaml


class YAMLConfiguration:
    file = None
    __config = None

    def __init__(self, file):
        self.file = file
        self.__config = dict()

    def load(self):
        with open(self.file, 'r', encoding='utf-8') as f:

            try:
                self.__config = yaml.safe_load(f)
                return True

            except yaml.YAMLError as err:
                return err

    def save(self):
        with open(self.file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.__config, stream=f, default_flow_style=False, allow_unicode=True)

    def get(self, path):
        paths = path.split(".")
        res = self.__config

        for x in paths:
            if x not in res:
                return False
            else:
                res = res[x]

        return res

    def set(self, path, value):
        paths = path.split(".")
        d = self.__config

        for x in range(0, len(paths) - 1):
            if paths[x] not in d:
                d[paths[x]] = dict()
            d = d[paths[x]]

        d[paths[-1]] = value
