# Embedded file name: ./lib/vprop.py
import variables

def get(key):
    return variables.WINDOW_HOME.getProperty('Vavoo_' + key)


def set(key, value):
    if value is None:
        variables.WINDOW_HOME.clearProperty('Vavoo_' + key)
    else:
        variables.WINDOW_HOME.setProperty('Vavoo_' + key, value)
    return