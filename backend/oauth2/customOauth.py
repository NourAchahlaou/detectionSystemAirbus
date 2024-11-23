from typing import Annotated, Union
from fastapi import Depends, FastAPI, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel





class CustomOAuth2PasswordRequestForm:
    """
    Custom form class to collect the `user_id` and `password` as form data
    for an OAuth2 password flow.
    """

    def __init__(
        self,
        *,
        grant_type: Annotated[
            Union[str, None],
            Form(pattern="password")
        ] = None,
        user_id: Annotated[
            str,
            Form()
        ],
        password: Annotated[
            str,
            Form()
        ],
        scope: Annotated[
            str,
            Form()
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form()
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form()
        ] = None,
    ):
        self.grant_type = grant_type
        self.user_id = user_id
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

class CustomOAuth2PasswordRequestFormStrict(CustomOAuth2PasswordRequestForm):
    """
    Strict form class to require `grant_type` with the value "password" along
    with `user_id` and `password` fields.
    """

    def __init__(
        self,
        grant_type: Annotated[
            str,
            Form(pattern="password")
        ],
        user_id: Annotated[
            str,
            Form()
        ],
        password: Annotated[
            str,
            Form()
        ],
        scope: Annotated[
            str,
            Form()
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form()
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form()
        ] = None,
    ):
        super().__init__(
            grant_type=grant_type,
            user_id=user_id,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret
        )
