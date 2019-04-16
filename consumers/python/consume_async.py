from consumers.python.app.app_async import AppAsync
from consumers.python.config.config import setConfig

if __name__=="__main__":

    setConfig()
    app = AppAsync()
    app.startApp()
