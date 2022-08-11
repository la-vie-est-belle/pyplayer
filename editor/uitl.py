import uuid
import time


def getUUID():
    UUID = uuid.uuid3(uuid.NAMESPACE_OID, str(time.time()))
    return str(UUID)