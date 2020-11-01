class LogLevel:
    LEVEL_INFO="INFO"
    LEVEL_ERROR="ERROR"
    LEVEL_WARNING="WARNING"
    
    @staticmethod
    def valueOf(level):
        val = -1
        if level == LogLevel.LEVEL_ERROR:
            val = 0
        elif level == LogLevel.LEVEL_WARNING:
            val = 1
        elif level == LogLevel.LEVEL_INFO:
            val = 2
        return val
