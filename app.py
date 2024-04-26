from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import OID

Base = declarative_base()

class ResepMaster(Base):
    __tablename__ = 'resep_master'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    bahan_master = relationship("BahanMaster", back_populates="resep_master")
    cara_membuat = relationship("CaraMembuat", back_populates="resep_master")
    testi_diskusi = relationship("TestiDiskusi", back_populates="resep_master")
    rating = relationship("Rating", back_populates="resep_master")

class BahanMaster(Base):
    __tablename__ = 'bahan_master'
    id = Column(Integer, primary_key=True)
    id_resep_master = Column(Integer, ForeignKey('resep_master.id'))
    porsi = Column(Integer)
    bahan_detail = relationship("BahanDetail", back_populates="bahan_master")
    resep_master = relationship("ResepMaster", back_populates="bahan_master")

class BahanDetail(Base):
    __tablename__ = 'bahan_detail'
    id = Column(Integer, primary_key=True)
    id_bahan_master = Column(Integer, ForeignKey('bahan_master.id'))
    name = Column(String(255))
    bahan_master = relationship("BahanMaster", back_populates="bahan_detail")

class CaraMembuat(Base):
    __tablename__ = 'cara_membuat'
    id = Column(Integer, primary_key=True)
    id_resep_master = Column(Integer, ForeignKey('resep_master.id'))
    lama_waktu = Column(Integer)
    tips = Column(String(255))
    cara_membuat_detail = relationship("CaraMembuatDetail", back_populates="cara_membuat")
    resep_master = relationship("ResepMaster", back_populates="cara_membuat")

class CaraMembuatDetail(Base):
    __tablename__ = 'cara_membuat_detail'
    id = Column(Integer, primary_key=True)
    id_cara_membuat = Column(Integer, ForeignKey('cara_membuat.id'))
    cara = Column(String(255))
    cara_membuat = relationship("CaraMembuat", back_populates="cara_membuat_detail")

class TestiDiskusi(Base):
    __tablename__ = 'testi_diskusi'
    id = Column(Integer, primary_key=True)
    id_resep_master = Column(Integer, ForeignKey('resep_master.id'))
    user_id = Column(Integer, ForeignKey('user.id')) 
    foto = Column(String(255)) 
    testimonial = Column(String(255))
    reply_diskusi = relationship("ReplyDiskusi", back_populates="testi_diskusi")
    resep_master = relationship("ResepMaster", back_populates="testi_diskusi")

class ReplyDiskusi(Base):
    __tablename__ = 'reply_diskusi'
    id = Column(Integer, primary_key=True)
    id_testi_diskusi = Column(Integer, ForeignKey('testi_diskusi.id'))
    user_id = Column(Integer)
    testimonial = Column(String(255))
    testi_diskusi = relationship("TestiDiskusi", back_populates="reply_diskusi")

class Rating(Base):
    __tablename__ = 'rating'
    id = Column(Integer, primary_key=True)
    id_resep_master = Column(Integer, ForeignKey('resep_master.id'))
    rating = Column(Float)
    resep_master = relationship("ResepMaster", back_populates="rating")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_pict = Column(OID)
    name = Column(String(255))
    email = Column(String(255))


username = 'admin'
password = 'admin'
host = 'localhost'
port = '5432'

connection_string = f"postgresql://{username}:{password}@{host}:{port}/Resep"

engine = create_engine(connection_string)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ResepMasterSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class BahanMasterSchema(BaseModel):
    id: int
    id_resep_master: int
    porsi: int

    class Config:
        orm_mode = True

class BahanDetailSchema(BaseModel):
    id: int
    id_bahan_master: int
    name: str

    class Config:
        orm_mode = True

class CaraMembuatSchema(BaseModel):
    id: int
    id_resep_master: int
    lama_waktu: int
    tips: str

    class Config:
        orm_mode = True

class CaraMembuatDetailSchema(BaseModel):
    id: int
    id_cara_membuat: int
    cara: str

    class Config:
        orm_mode = True

class TestiDiskusiSchema(BaseModel):
    id: int
    id_resep_master: int
    user_id: int
    foto: str
    testimonial: str

    class Config:
        orm_mode = True

class ReplyDiskusiSchema(BaseModel):
    id: int
    id_testi_diskusi: int
    user_id: int
    testimonial: str

    class Config:
        orm_mode = True

class RatingSchema(BaseModel):
    id: int
    id_resep_master: int
    rating: float

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    email: str
    user_pict: Optional[bytes]

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    user_pict: Optional[bytes]

class UserDisplay(BaseModel):
    id: int
    name: str
    email: str
    user_pict: Optional[str]

    class Config:
        orm_mode = True


router = APIRouter(tags=["Resep Master"],prefix="/api")

@app.post("/resep_master/", status_code=status.HTTP_201_CREATED)
def create_resep_master(name: str, db: Session = Depends(get_db)):
    new_resep_master = ResepMaster(name=name)
    db.add(new_resep_master)
    db.commit()
    db.refresh(new_resep_master)
    return new_resep_master

@app.get("/resep_master/{resep_master_id}", response_model=ResepMasterSchema)
def read_resep_master(resep_master_id: int, db: Session = Depends(get_db)):
    resep_master = db.query(ResepMaster).filter(ResepMaster.id == resep_master_id).first()
    if resep_master is None:
        raise HTTPException(status_code=404, detail="ResepMaster not found")
    return resep_master

@app.put("/resep_master/{resep_master_id}", response_model=ResepMasterSchema)
def update_resep_master(resep_master_id: int, resep_master: ResepMasterSchema, db: Session = Depends(get_db)):
    db_item = db.query(ResepMaster).filter(ResepMaster.id == resep_master_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="ResepMaster not found")
    for var, value in vars(resep_master).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/resep_master/{resep_master_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resep_master(resep_master_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ResepMaster).filter(ResepMaster.id == resep_master_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="ResepMaster not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@app.get("/resep_master/", response_model=List[ResepMasterSchema])
def read_all_resep_master(db: Session = Depends(get_db)):
    return db.query(ResepMaster).all()

router = APIRouter(tags=["Bahan"],prefix="/api")

@app.post("/bahan_master/", status_code=status.HTTP_201_CREATED)
def create_bahan_master(resep_master_id: int, porsi: int, db: Session = Depends(get_db)):
    new_bahan_master = BahanMaster(id_resep_master=resep_master_id, porsi=porsi)
    db.add(new_bahan_master)
    db.commit()
    db.refresh(new_bahan_master)
    return new_bahan_master

@app.post("/bahan_detail/", status_code=status.HTTP_201_CREATED)
def create_bahan_detail(bahan_master_id: int, name: str, db: Session = Depends(get_db)):
    new_bahan_detail = BahanDetail(id_bahan_master=bahan_master_id, name=name)
    db.add(new_bahan_detail)
    db.commit()
    db.refresh(new_bahan_detail)
    return new_bahan_detail

@app.get("/bahan_master/{bahan_master_id}", response_model=BahanMasterSchema)
def read_bahan_master(bahan_master_id: int, db: Session = Depends(get_db)):
    bahan_master = db.query(BahanMaster).filter(BahanMaster.id == bahan_master_id).first()
    if bahan_master is None:
        raise HTTPException(status_code=404, detail="BahanMaster not found")
    return bahan_master

@app.get("/bahan_detail/{bahan_detail_id}", response_model=BahanDetailSchema)
def read_bahan_detail(bahan_detail_id: int, db: Session = Depends(get_db)):
    bahan_detail = db.query(BahanDetail).filter(BahanDetail.id == bahan_detail_id).first()
    if bahan_detail is None:
        raise HTTPException(status_code=404, detail="BahanDetail not found")
    return bahan_detail

@app.put("/bahan_master/{bahan_master_id}", response_model=BahanMasterSchema)
def update_bahan_master(bahan_master_id: int, bahan_master: BahanMasterSchema, db: Session = Depends(get_db)):
    db_item = db.query(BahanMaster).filter(BahanMaster.id == bahan_master_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BahanMaster not found")
    for var, value in vars(bahan_master).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/bahan_detail/{bahan_detail_id}", response_model=BahanDetailSchema)
def update_bahan_detail(bahan_detail_id: int, bahan_detail: BahanDetailSchema, db: Session = Depends(get_db)):
    db_item = db.query(BahanDetail).filter(BahanDetail.id == bahan_detail_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BahanDetail not found")
    for var, value in vars(bahan_detail).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/bahan_master/{bahan_master_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bahan_master(bahan_master_id: int, db: Session = Depends(get_db)):
    db_item = db.query(BahanMaster).filter(BahanMaster.id == bahan_master_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BahanMaster not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@app.delete("/bahan_detail/{bahan_detail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bahan_detail(bahan_detail_id: int, db: Session = Depends(get_db)):
    db_item = db.query(BahanDetail).filter(BahanDetail.id == bahan_detail_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BahanDetail not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@app.get("/bahan_master/", response_model=List[BahanMasterSchema])
def read_all_bahan_master(db: Session = Depends(get_db)):
    return db.query(BahanMaster).all()

@app.get("/bahan_detail/", response_model=List[BahanDetailSchema])
def read_all_bahan_detail(db: Session = Depends(get_db)):
    return db.query(BahanDetail).all()

router = APIRouter(tags=["Cara Membuat"],prefix="/api")

@app.post("/cara_membuat/", status_code=status.HTTP_201_CREATED)
def create_cara_membuat(resep_master_id: int, lama_waktu: int, tips: str, db: Session = Depends(get_db)):
    new_cara_membuat = CaraMembuat(id_resep_master=resep_master_id, lama_waktu=lama_waktu, tips=tips)
    db.add(new_cara_membuat)
    db.commit()
    db.refresh(new_cara_membuat)
    return new_cara_membuat

@app.post("/cara_membuat_detail/", status_code=status.HTTP_201_CREATED)
def create_cara_membuat_detail(cara_membuat_id: int, cara: str, db: Session = Depends(get_db)):
    new_cara_membuat_detail = CaraMembuatDetail(id_cara_membuat=cara_membuat_id, cara=cara)
    db.add(new_cara_membuat_detail)
    db.commit()
    db.refresh(new_cara_membuat_detail)
    return new_cara_membuat_detail

@app.get("/cara_membuat/{cara_membuat_id}", response_model=CaraMembuatSchema)
def read_cara_membuat(cara_membuat_id: int, db: Session = Depends(get_db)):
    cara_membuat = db.query(CaraMembuat).filter(CaraMembuat.id == cara_membuat_id).first()
    if cara_membuat is None:
        raise HTTPException(status_code=404, detail="CaraMembuat not found")
    return cara_membuat

@app.get("/cara_membuat_detail/{cara_membuat_detail_id}", response_model=CaraMembuatDetailSchema)
def read_cara_membuat_detail(cara_membuat_detail_id: int, db: Session = Depends(get_db)):
    cara_membuat_detail = db.query(CaraMembuatDetail).filter(CaraMembuatDetail.id == cara_membuat_detail_id).first()
    if cara_membuat_detail is None:
        raise HTTPException(status_code=404, detail="CaraMembuatDetail not found")
    return cara_membuat_detail

@app.get("/cara_membuat/", response_model=List[CaraMembuatSchema])
def read_all_cara_membuat(db: Session = Depends(get_db)):
    return db.query(CaraMembuat).all()

@app.get("/cara_membuat_detail/", response_model=List[CaraMembuatDetailSchema])
def read_all_cara_membuat_detail(db: Session = Depends(get_db)):
    return db.query(CaraMembuatDetail).all()

@app.put("/cara_membuat/{cara_membuat_id}", response_model=CaraMembuatSchema)
def update_cara_membuat(cara_membuat_id: int, cara_membuat: CaraMembuatSchema, db: Session = Depends(get_db)):
    db_item = db.query(CaraMembuat).filter(CaraMembuat.id == cara_membuat_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="CaraMembuat not found")
    for var, value in vars(cara_membuat).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/cara_membuat_detail/{cara_membuat_detail_id}", response_model=CaraMembuatDetailSchema)
def update_cara_membuat_detail(cara_membuat_detail_id: int, cara_membuat_detail: CaraMembuatDetailSchema, db: Session = Depends(get_db)):
    db_item = db.query(CaraMembuatDetail).filter(CaraMembuatDetail.id == cara_membuat_detail_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="CaraMembuatDetail not found")
    for var, value in vars(cara_membuat_detail).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/cara_membuat/{cara_membuat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cara_membuat(cara_membuat_id: int, db: Session = Depends(get_db)):
    db_item = db.query(CaraMembuat).filter(CaraMembuat.id == cara_membuat_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="CaraMembuat not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@app.delete("/cara_membuat_detail/{cara_membuat_detail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cara_membuat_detail(cara_membuat_detail_id: int, db: Session = Depends(get_db)):
    db_item = db.query(CaraMembuatDetail).filter(CaraMembuatDetail.id == cara_membuat_detail_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="CaraMembuatDetail not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

router = APIRouter(tags=["Testi Diskusi"],prefix="/api")

@app.post("/testi_diskusi/", status_code=status.HTTP_201_CREATED)
def create_testi_diskusi(resep_master_id: int, user_id: int, foto: str, testimonial: str, db: Session = Depends(get_db)):
    new_testi_diskusi = TestiDiskusi(id_resep_master=resep_master_id, user_id=user_id, foto=foto, testimonial=testimonial)
    db.add(new_testi_diskusi)
    db.commit()
    db.refresh(new_testi_diskusi)
    return new_testi_diskusi

@app.post("/reply_diskusi/", status_code=status.HTTP_201_CREATED)
def create_reply_diskusi(testi_diskusi_id: int, user_id: int, testimonial: str, db: Session = Depends(get_db)):
    new_reply_diskusi = ReplyDiskusi(id_testi_diskusi=testi_diskusi_id, user_id=user_id, testimonial=testimonial)
    db.add(new_reply_diskusi)
    db.commit()
    db.refresh(new_reply_diskusi)
    return new_reply_diskusi

@app.get("/testi_diskusi/{testi_diskusi_id}", response_model=TestiDiskusiSchema)
def read_testi_diskusi(testi_diskusi_id: int, db: Session = Depends(get_db)):
    testi_diskusi = db.query(TestiDiskusi).filter(TestiDiskusi.id == testi_diskusi_id).first()
    if testi_diskusi is None:
        raise HTTPException(status_code=404, detail="TestiDiskusi not found")
    return testi_diskusi

@app.get("/reply_diskusi/{reply_diskusi_id}", response_model=ReplyDiskusiSchema)
def read_reply_diskusi(reply_diskusi_id: int, db: Session = Depends(get_db)):
    reply_diskusi = db.query(ReplyDiskusi).filter(ReplyDiskusi.id == reply_diskusi_id).first()
    if reply_diskusi is None:
        raise HTTPException(status_code=404, detail="ReplyDiskusi not found")
    return reply_diskusi

@app.get("/testi_diskusi/", response_model=List[TestiDiskusiSchema])
def read_all_testi_diskusi(db: Session = Depends(get_db)):
    return db.query(TestiDiskusi).all()

@app.get("/reply_diskusi/", response_model=List[ReplyDiskusiSchema])
def read_all_reply_diskusi(db: Session = Depends(get_db)):
    return db.query(ReplyDiskusi).all()

@app.put("/testi_diskusi/{testi_diskusi_id}", response_model=TestiDiskusiSchema)
def update_testi_diskusi(testi_diskusi_id: int, testi_diskusi: TestiDiskusiSchema, db: Session = Depends(get_db)):
    db_item = db.query(TestiDiskusi).filter(TestiDiskusi.id == testi_diskusi_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="TestiDiskusi not found")
    for var, value in vars(testi_diskusi).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/reply_diskusi/{reply_diskusi_id}", response_model=ReplyDiskusiSchema)
def update_reply_diskusi(reply_diskusi_id: int, reply_diskusi: ReplyDiskusiSchema, db: Session = Depends(get_db)):
    db_item = db.query(ReplyDiskusi).filter(ReplyDiskusi.id == reply_diskusi_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="ReplyDiskusi not found")
    for var, value in vars(reply_diskusi).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/testi_diskusi/{testi_diskusi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testi_diskusi(testi_diskusi_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TestiDiskusi).filter(TestiDiskusi.id == testi_diskusi_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="TestiDiskusi not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@app.delete("/reply_diskusi/{reply_diskusi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reply_diskusi(reply_diskusi_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ReplyDiskusi).filter(ReplyDiskusi.id == reply_diskusi_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="ReplyDiskusi not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

router = APIRouter(tags=["Rating"],prefix="/api")

@app.post("/rating/", status_code=status.HTTP_201_CREATED)
def create_rating(resep_master_id: int, rating_value: float, db: Session = Depends(get_db)):
    new_rating = Rating(id_resep_master=resep_master_id, rating=rating_value)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@app.get("/rating/{rating_id}", response_model=RatingSchema)
def read_rating(rating_id: int, db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@app.get("/rating/", response_model=List[RatingSchema])
def read_all_rating(db: Session = Depends(get_db)):
    return db.query(Rating).all()

@app.put("/rating/{rating_id}", response_model=RatingSchema)
def update_rating(rating_id: int, rating: RatingSchema, db: Session = Depends(get_db)):
    db_item = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Rating not found")
    for var, value in vars(rating).items():
        setattr(db_item, var, value) if value else None
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/rating/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

router = APIRouter(tags=["User"],prefix="/api")

@app.post("/users/", response_model=UserDisplay, status_code=status.HTTP_201_CREATED)
async def create_user(name: str, email: str, user_pict: UploadFile = File(None), db: Session = Depends(get_db)):
    image_data = None
    if user_pict:
        contents = await user_pict.read()
        image_data = base64.b64encode(contents).decode('utf-8')
    new_user = User(name=name, email=email, user_pict=image_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserDisplay)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[UserDisplay])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.put("/users/{user_id}", response_model=UserDisplay)
async def update_user(user_id: int, name: Optional[str] = None, email: Optional[str] = None, user_pict: UploadFile = File(None), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if name:
        db_user.name = name
    if email:
        db_user.email = email
    if user_pict:
        contents = await user_pict.read()
        db_user.user_pict = base64.b64encode(contents).decode('utf-8')
    db.commit()
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"ok": True}