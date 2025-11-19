from passlib.context import CryptContext


pwd_conetext = CryptContext(schemes=['bcrypt'])

def gerar_hash(texto):
    return pwd_conetext.hash(texto)

def verificar_hash(texto,hash):
    return pwd_conetext.verify(texto, hash)