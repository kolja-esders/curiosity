from lake.models import Log as LogModal

class Log:

    @staticmethod
    def trace(producer, msg):
        LogModal.objects.create(producer=producer, lvl='DEBUG', lvl_id=1, msg=msg)

    @staticmethod
    def debug(producer, msg):
        LogModal.objects.create(producer=producer, lvl='DEBUG', lvl_id=2, msg=msg)

    @staticmethod
    def info(producer, msg):
        LogModal.objects.create(producer=producer, lvl='INFO', lvl_id=3, msg=msg)

    @staticmethod
    def warn(producer, msg):
        LogModal.objects.create(producer=producer, lvl='WARN', lvl_id=4, msg=msg)

    @staticmethod
    def error(producer, msg):
        LogModal.objects.create(producer=producer, lvl='ERROR', lvl_id=5, msg=msg)

    @staticmethod
    def fatal(producer, msg):
        LogModal.objects.create(producer=producer, lvl='FATAL', lvl_id=6, msg=msg)
