from fastapi import status


ALREADY_EXISTS = {
    "description": "User already in call",
    "content": {
        "application/json": {
            "example": {
                "detail": "User already in call."
            }
        }
    },
}

CALLEE_RESPONSES = {status.HTTP_208_ALREADY_REPORTED: ALREADY_EXISTS}
