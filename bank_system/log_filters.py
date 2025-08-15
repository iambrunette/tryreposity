import logging

class MaskCardFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = record.msg.replace("1234-5678-9012-3456", "****-****-****-3456")
        return True
