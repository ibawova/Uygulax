
import sys

def main():
    try:
        command = sys.argv[1]
    except IndexError:
        return

    if command == 'startup':
        from lib import startup
        startup.show()

    elif command == 'logout':
        #from lib import login
        #from lib import startup
        #from lib import utils
        #from lib import variables
        login.session.setToken(True)
    elif command == 'install':
        from lib import install
        install.show()
    elif command == 'ftp':
        from lib import ftp
        ftp.show()
    elif command == 'restart':
        from lib import vavoo_api
        vavoo_api.restart()


if __name__ == '__main__':
    main()
