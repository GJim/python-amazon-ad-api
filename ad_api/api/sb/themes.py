from ad_api.base import Client, sp_endpoint, ApiResponse
import json


class Themes(Client):
    r"""
    Themes(account='default', marketplace: Marketplaces = Marketplaces.EU, credentials=None, debug=False)

    Amazon Ads API - Sponsored Brands - Theme Targeting

    Theme targeting automatically targets keywords related to your brand or landing pages.

    Supported theme types:
    - KEYWORDS_RELATED_TO_YOUR_BRAND: Keywords related to your brand
    - KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES: Keywords related to your landing pages

    Note: This endpoint does not support Author profiles.
    """

    VALID_THEME_TYPES = ["KEYWORDS_RELATED_TO_YOUR_BRAND", "KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES"]

    VALID_THEME_STATES = ["enabled", "paused", "archived"]

    @sp_endpoint("/sb/themes/list", method="POST")
    def list_themes(
        self,
        nextToken: str = None,
        maxResults: int = None,
        campaignIdFilter: list = None,
        adGroupIdFilter: list = None,
        themeIdFilter: list = None,
        stateFilter: list = None,
        themeTypeFilter: list = None,
        **kwargs,
    ) -> ApiResponse:
        r"""
        list_themes(nextToken: str = None, maxResults: int = None, campaignIdFilter: list = None, adGroupIdFilter: list = None, themeIdFilter: list = None, stateFilter: list = None, themeTypeFilter: list = None, **kwargs) -> ApiResponse

        Gets a list of theme targets associated with the client identifier, filtered by specified criteria.

        Args:
            nextToken (str, optional): Token for pagination. Operations that return paginated results include a pagination token in this field.
            maxResults (int, optional): Maximum number of results to return. Defaults to API maximum.
            campaignIdFilter (list, optional): List of campaign identifiers to filter by (max 100).
            adGroupIdFilter (list, optional): List of ad group identifiers to filter by (max 100).
            themeIdFilter (list, optional): List of theme target identifiers to filter by (max 100).
            stateFilter (list, optional): List of theme target states to filter by. Valid values: enabled, paused, archived. Default: enabled, paused.
            themeTypeFilter (list, optional): List of theme types to filter by. Valid values: KEYWORDS_RELATED_TO_YOUR_BRAND, KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES.

        Returns:
            ApiResponse: Contains themes array and optional nextToken for pagination

        Response Format:
            {
                "themes": [
                    {
                        "themeId": "string",
                        "adGroupId": "string",
                        "campaignId": "string",
                        "themeType": "KEYWORDS_RELATED_TO_YOUR_BRAND|KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES",
                        "state": "enabled|paused|archived",
                        "bid": number
                    }
                ],
                "nextToken": "string"
            }
        """
        body = {}

        if nextToken is not None:
            body["nextToken"] = nextToken

        if maxResults is not None:
            body["maxResults"] = maxResults

        if campaignIdFilter is not None:
            body["campaignIdFilter"] = {"include": campaignIdFilter[:100]}  # Limit to max 100

        if adGroupIdFilter is not None:
            body["adGroupIdFilter"] = {"include": adGroupIdFilter[:100]}  # Limit to max 100

        if themeIdFilter is not None:
            body["themeIdFilter"] = {"include": themeIdFilter[:100]}  # Limit to max 100

        if stateFilter is not None:
            # Validate states
            valid_states = [state for state in stateFilter if state in self.VALID_THEME_STATES]
            if valid_states:
                body["stateFilter"] = {"include": valid_states[:3]}  # Limit to max 3

        if themeTypeFilter is not None:
            # Validate theme types
            valid_types = [theme_type for theme_type in themeTypeFilter if theme_type in self.VALID_THEME_TYPES]
            if valid_types:
                body["themeTypeFilter"] = {"include": valid_types[:2]}  # Limit to max 2

        headers = {"Accept": "application/vnd.sbthemeslistresponse.v3+json"}
        data_str = json.dumps(body) if body else None
        return self._request(kwargs.pop("path"), data=data_str, params=kwargs, headers=headers)

    @sp_endpoint("/sb/themes", method="POST")
    def create_themes(self, themes: list, **kwargs) -> ApiResponse:
        r"""
        create_themes(themes: list, **kwargs) -> ApiResponse

        Create one or more theme targets.

        Args:
            themes (list): List of theme targets to create (max 100). Each theme must contain:
                - adGroupId (str): The identifier of the ad group
                - campaignId (str): The identifier of the campaign
                - themeType (str): Theme type - KEYWORDS_RELATED_TO_YOUR_BRAND or KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES
                - bid (float): The bid amount

        Returns:
            ApiResponse: Contains success and error results with correlation indexes

        Request Format:
            {
                "themes": [
                    {
                        "adGroupId": string,
                        "campaignId": string,
                        "themeType": "KEYWORDS_RELATED_TO_YOUR_BRAND|KEYWORDS_RELATED_TO_YOUR_LANDING_PAGES",
                        "bid": number
                    }
                ]
            }

        Response Format:
            {
                "success": [
                    {
                        "themeId": "string",
                        "index": integer
                    }
                ],
                "error": [
                    {
                        "code": "string",
                        "details": "string",
                        "index": integer
                    }
                ]
            }

        Note:
            - Theme targets can be created on multi-adGroup campaigns where campaign serving status is not archived, terminated, rejected, or ended
            - Ad group state must not be archived
            - Only one target can be created for each themeType per adGroup
            - Maximum list size is 100 theme targets
        """
        if not themes:
            raise ValueError("themes parameter is required and cannot be empty")

        if len(themes) > 100:
            raise ValueError("Maximum 100 theme targets allowed per request")

        # Validate each theme
        for i, theme in enumerate(themes):
            if not isinstance(theme, dict):
                raise ValueError(f"Theme at index {i} must be a dictionary")

            required_fields = ["adGroupId", "campaignId", "themeType", "bid"]
            for field in required_fields:
                if field not in theme:
                    raise ValueError(f"Theme at index {i} missing required field: {field}")

            # Validate theme type
            if theme["themeType"] not in self.VALID_THEME_TYPES:
                raise ValueError(
                    f"Theme at index {i} has invalid themeType: {theme['themeType']}. Valid types: {self.VALID_THEME_TYPES}"
                )

        body = {"themes": themes[:100]}  # Limit to max 100
        headers = {"Accept": "application/vnd.sbthemescreateresponse.v3+json"}
        data_str = json.dumps(body)
        return self._request(kwargs.pop("path"), data=data_str, params=kwargs, headers=headers)

    @sp_endpoint("/sb/themes", method="PUT")
    def update_themes(self, themes: list, **kwargs) -> ApiResponse:
        r"""
        update_themes(themes: list, **kwargs) -> ApiResponse

        Updates one or more theme targets.

        Args:
            themes (list): List of theme targets to update (max 100). Each theme must contain:
                - themeId (str): The identifier of the theme target
                - adGroupId (str): The identifier of the ad group
                - campaignId (str): The identifier of the campaign
                - state (str, optional): Theme target state - enabled, paused, archived
                - bid (float, optional): The bid amount

        Returns:
            ApiResponse: Contains success and error results with correlation indexes

        Request Format:
            {
                "themes": [
                    {
                        "themeId": "string",
                        "adGroupId": "string",
                        "campaignId": "string",
                        "state": "enabled|paused|archived",
                        "bid": number
                    }
                ]
            }

        Response Format:
            {
                "success": [
                    {
                        "themeId": "string",
                        "index": integer
                    }
                ],
                "error": [
                    {
                        "code": "string",
                        "details": "string",
                        "themeId": "string",
                        "index": integer
                    }
                ]
            }

        Note:
            - Theme targets can be updated on multi-adGroup campaigns where campaign serving status is not archived, terminated, rejected, or ended
            - Ad group state must not be archived
            - Theme targets cannot be archived directly - use state management instead
            - Maximum list size is 100 theme targets
            - Bid is only mutable when the corresponding campaign does not have any enabled optimization rule
        """
        if not themes:
            raise ValueError("themes parameter is required and cannot be empty")

        if len(themes) > 100:
            raise ValueError("Maximum 100 theme targets allowed per request")

        # Validate each theme
        for i, theme in enumerate(themes):
            if not isinstance(theme, dict):
                raise ValueError(f"Theme at index {i} must be a dictionary")

            required_fields = ["themeId", "adGroupId", "campaignId"]
            for field in required_fields:
                if field not in theme:
                    raise ValueError(f"Theme at index {i} missing required field: {field}")

            # Validate state if provided
            if "state" in theme and theme["state"] not in self.VALID_THEME_STATES:
                raise ValueError(
                    f"Theme at index {i} has invalid state: {theme['state']}. Valid states: {self.VALID_THEME_STATES}"
                )

        body = {"themes": themes[:100]}  # Limit to max 100
        headers = {"Accept": "application/vnd.sbthemesupdateresponse.v3+json"}
        data_str = json.dumps(body)
        return self._request(kwargs.pop("path"), data=data_str, params=kwargs, headers=headers)
