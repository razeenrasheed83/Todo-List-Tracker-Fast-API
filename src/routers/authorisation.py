from fastapi import APIRouter,status,HTTPException,Depends
from src.models.authorisation import SignUp,Login,TokenData
from src.utilities.dbutils import DButils
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
import jwt

router = APIRouter(
        tags=["Authorisation"]
)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "YwqaxxPtVk6F9h7cAiNOdmhWALBkvwoJcgEohhPmjVvYeC2TQMqsOfTg3edppGQzliIwBs68DQ4g1lPBrq8rh7FuMmGF2rVwmWIv"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post('/signup',status_code=status.HTTP_201_CREATED)
def userSignup(payload:SignUp):
        
        db = DButils()
        columns = ['username','email','contact','password']
        hashed_password = pwd_context.hash(payload.password)
        values =(
                payload.username,
                payload.email,
                payload.contact,
                hashed_password,
        )
        db.insert_query('users',columns,values)
        return{
                "message":"Signup Success"
        }

@router.post('/login')
def userLogin(payload:OAuth2PasswordRequestForm = Depends()):
         db = DButils()
         query = f"""select * from users where username = '{payload.username}' """
         response = db.execute_query(query, True)
         if len(response) == 0:
                 return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Found")
         user_password = payload.password
         check = pwd_context.verify(user_password, response[0]['password'])
         if not check:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
         data={"name":payload.username}
         access_token = generate_access_token(data)
         return {"access_token": access_token, "token_type": "bearer"}
         



def generate_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token:str=Depends(oauth_scheme)):
        # credential_exception
        try:
            payload  = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
            username = payload.get('name')
            if username is None:
                   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            token_data = TokenData(username=username)
        except:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
       
       
         

