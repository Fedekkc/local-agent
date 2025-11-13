import datetime


class SystemTool:
    
    @staticmethod
    def hora_actual() -> str:

        ahora = datetime.datetime.now()
        return ahora.strftime("%Y-%m-%d %H:%M:%S")
