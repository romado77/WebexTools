from dataclasses import InitVar, dataclass, field


@dataclass
class User:
    data: InitVar[dict]
    id: str = ""
    user_name: str = ""
    emails: list = field(default_factory=list)
    display_name: str = ""
    nick_name: str = ""
    first_name: str = ""
    last_name: str = ""
    roles: list = field(default_factory=list)
    timezone: str = ""
    active: bool = False
    type: str = ""

    def __post_init__(self, data):
        if isinstance(data, dict):
            self._data = data
        else:
            return None

        self.id = self._data.get("id", "")
        self.user_name = self._data.get("userName", "")
        self.emails = self._data.get("emails", [])
        self.display_name = self._data.get("displayName", "")
        self.nick_name = self._data.get("nickName", "")
        self.first_name = self._data.get("name", {}).get("givenName", "")
        self.last_name = self._data.get("name", {}).get("familyName", "")
        self.roles = self._data.get("roles", [])
        self.timezone = self._data.get("timezone", "")
        self.active = self._data.get("active", False)
        self.type = self._data.get("userType", "")
