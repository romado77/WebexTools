from typing import Optional

from webextools.http import Session
from webextools.settings import DEFAULT_IDENTITY_URL
from webextools.users import User


class SCIM:
    def __init__(self, base_url: str = DEFAULT_IDENTITY_URL, token: str = "", org_id: str = ""):
        self.session = Session(
            base_url=base_url,
            authorization=f"Bearer {token}",
        )
        self.org_id = org_id

    def get_users(self, org_id: str = ""):
        """
        Get all users in an organization.

        :param org_id: Organization ID
        :return: Generator of User objects
        """
        total_results = 0
        next_index = 1
        items_per_page = 0

        org_id = org_id or self.org_id

        if not org_id:
            raise ValueError("Organization ID is required")

        while True:
            url = f"scim/{org_id}/v2/Users"
            params = {"startIndex": next_index}

            if items_per_page:
                params["count"] = items_per_page

            response = self.session.get(
                url,
            )

            for item in response:
                data = item.json()

                if not total_results:
                    total_results = data.get("totalResults", 0)

                items_per_page = data.get("itemsPerPage", 0)
                next_index = data.get("startIndex", 1) + items_per_page

                resources = data.get("Resources")

                if resources:
                    for resource in resources:
                        yield User(resource)

            if next_index - 1 >= total_results:
                break

    def get_user(self, user_id: str, org_id: str = "") -> Optional[User]:
        """
        Get a user by ID

        :param user_id: User ID
        :param org_id: Organization ID

        :return: User object if found, None otherwise
        """
        org_id = org_id or self.org_id

        if not org_id:
            raise ValueError("Organization ID is required")

        url = f"scim/{org_id}/v2/Users/{user_id}"

        response = self.session.get(url)

        if not response:
            return None

        response = list(response)

        if not response:
            return None

        return User(response[0].json())

    def update_user_patch(self, user_id: str, data: dict, org_id: str = "") -> Optional[User]:
        """
        Update a user using PATCH

        :param user_id: User ID
        :param data: User data
        :param org_id: Organization ID

        :return: User object if found, None otherwise
        """
        org_id = org_id or self.org_id

        if not org_id:
            raise ValueError("Organization ID is required")

        if not isinstance(data, dict) or "schemas" not in data or "Operations" not in data:
            raise ValueError("Invalid data for updating user")

        url = f"scim/{org_id}/v2/Users/{user_id}"

        response = self.session.patch(url, json=data)

        if not response:
            return None

        response = list(response)

        if not response:
            return None

        return User(response[0].json())
