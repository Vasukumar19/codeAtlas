import uuid

NAMESPACE_RIM = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')

class IdentityGenerator:
    @staticmethod
    def generate_repository_id(owner: str, name: str) -> uuid.UUID:
        sig = f"repository:{owner}/{name}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_directory_id(repo_id: uuid.UUID, path: str) -> uuid.UUID:
        sig = f"directory:{repo_id}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_file_id(repo_id: uuid.UUID, path: str) -> uuid.UUID:
        sig = f"file:{repo_id}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_symbol_id(file_id: uuid.UUID, fully_qualified_name: str) -> uuid.UUID:
        sig = f"symbol:{file_id}:{fully_qualified_name}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_import_id(file_id: uuid.UUID, raw: str) -> uuid.UUID:
        sig = f"import:{file_id}:{raw}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_route_id(file_id: uuid.UUID, method: str, path: str) -> uuid.UUID:
        sig = f"route:{file_id}:{method}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)
