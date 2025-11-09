from passlib.context import CryptContext
from jose import jwt, JWTError, JWTClaimsError, ExpiresSignatureError
from datetime import datetime, timedelta, timezone
from app.core.config import settings


'''
HASHAGE DE MOTS DE PASSE
'''

pwd_context = CryptContext(schemes=["argon2"],deprecated="auto")

def get_password_hash(password: str)-> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hash_password: str)-> bool:
    return pwd_context.verify(plain_password,hash_password)



    '''
    GESTION DES TOKENS JWT
    '''


def create_token(data: dict, expire_time: timedelta) -> str:
    ''' 
    jwt signer avec RS256 incluant des champs standard:
    -iat : emis a
    -ndf : pas avant
    -exp : expiration
    '''
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expire_time
    to_encode.update({
        "iat": now, # emis a
        "nbf": now, # pas avant
        "exp": expire   # Expiration
        })

    encoded_jwt = jwt.encode(
        to_encode,
        Settings.PRIVATE_KEY,
        algorithms = settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        decode_jwt = jwt.decode(
            token,
            Settings.PUBLIC_KEY,
            algorithms = [settings.ALGORITHM]
        )
        return decode_jwt

    except ExpiresSignatureError:
        raise ValueError("le token a expirer. veuillez vous reconnecter.")
    except JWTClaimsError:
        raise ValueError("les claims du token sont invalides (nbf, iat ou exp incorrectes)")    
    except JWTError:
        raise ValueError("le token est invalide (signature ou structure incorrecte)")    


