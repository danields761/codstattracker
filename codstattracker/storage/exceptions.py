class StorageError(Exception):
    pass


class StorageIOError(StorageError):
    pass


class StorageSaveError(StorageError):
    pass
