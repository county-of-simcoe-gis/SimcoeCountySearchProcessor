from configparser import ConfigParser


def getConfig(section='tabular'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read('database.ini')

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found'.format(section))

    return db
