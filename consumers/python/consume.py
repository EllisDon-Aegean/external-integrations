from consumers.python.app.app import App
from consumers.python.config.config import setConfig

if __name__=="__main__":

    setConfig()
    app = App()
    app.startApp()
