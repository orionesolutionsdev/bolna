
# JWKS_URL = os.getenv('JWKS_URL')
JWKS_URL= "https://civil-marmoset-57.clerk.accounts.dev/.well-known/jwks.json"
from jose import jwt
import requests
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request



def get_jwks():
    response = requests.get(JWKS_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to validate token")
    return response.json()


# Auth Middleware
class CustomAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Extract authorization header from request
            authorization_header = request.headers.get("Authorization")
            if not authorization_header: # 1.if not authorization header
                raise HTTPException(status_code=401, detail="Unauthorized")

            # Split authorization header to get token
            authorization = authorization_header.split(" ")

            if len(authorization) != 2 or authorization[0].lower() != "bearer":# 2.if not Bearer scheme
                raise HTTPException(status_code=401, detail="Invalid authentication scheme, Please use Bearer scheme.")

            token = authorization[1]
            if not token: # 3.if not token
                raise HTTPException(status_code=401, detail="Missing token")
            if token :
                try:
                    # Decode token
                    header = jwt.get_unverified_header(token)
                    jwks = get_jwks()

                    # Find the appropriate key in JWKS
                    key = None
                    for k in jwks["keys"]:
                        if k["kid"] == header["kid"]:
                            key = k
                            break

                    if key is None:
                        raise HTTPException(status_code=401, detail="Invalid token")
                    # Verify token signature
                    decoded_token = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
                    # Attach user information to request state
                    request.state.user = decoded_token.get("sub")

                except jwt.JWTError as e:
                    raise HTTPException(status_code=401, detail="Invalid token")
                except HTTPException as exc:
                    raise HTTPException(status_code=401, detail='Invalid token')

            # If token is valid, proceed with the request
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse({"error": str(exc.detail)}, status_code=exc.status_code)


def get_key(token):
    # Extract header from token
    header = jwt.get_unverified_header(token)
    jwks = get_jwks()

    # Find the appropriate key in JWKS
    key = None
    for k in jwks["keys"]:
        if k["kid"] == header["kid"]:
            key = k
            break

    if key is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return key

def get_user_id_from_Token(request: str) -> str:
    try:
        token = request.headers['authorization'].split(" ")[1]

        # Getting User ID  from Token
        key = get_key(token)    
        decoded_token = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False}) 
        user_id = decoded_token['sub']
    except Exception as e: 
        raise HTTPException(status_code=401, detail="Unauthorized Access: Token")

    
    return user_id

