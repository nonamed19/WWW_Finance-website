from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "accounts_user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(128), default="")
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    email: Mapped[str] = mapped_column(String(254), default="")
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    money: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    salary: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    desire_amount_deposit: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    deposit_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    desire_amount_saving: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    saving_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    profile_image: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ApiToken(Base):
    __tablename__ = "api_tokens"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[User] = relationship()


class ProductBase:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dcls_month: Mapped[str] = mapped_column(String(6))
    fin_co_no: Mapped[str] = mapped_column(String(20))
    fin_prdt_cd: Mapped[str] = mapped_column(String(20))
    kor_co_nm: Mapped[str] = mapped_column(String(100))
    fin_prdt_nm: Mapped[str] = mapped_column(String(100))
    join_way: Mapped[str] = mapped_column(Text)
    mtrt_int: Mapped[str] = mapped_column(Text)
    spcl_cnd: Mapped[str] = mapped_column(Text)
    join_deny: Mapped[int] = mapped_column(Integer)
    join_member: Mapped[str] = mapped_column(Text)
    etc_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dcls_strt_day: Mapped[str] = mapped_column(String(8))
    dcls_end_day: Mapped[str | None] = mapped_column(String(8), nullable=True)
    fin_co_subm_day: Mapped[str] = mapped_column(String(14))


class DepositBase(ProductBase, Base):
    __tablename__ = "bankings_depositbaselist"
    options: Mapped[list["DepositOption"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class SavingBase(ProductBase, Base):
    __tablename__ = "bankings_savingbaselist"
    options: Mapped[list["SavingOption"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductOption:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    save_trm: Mapped[str] = mapped_column(String(10))
    intr_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    intr_rate2: Mapped[float | None] = mapped_column(Float, nullable=True)
    intr_rate_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    intr_rate_type_nm: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dcls_month: Mapped[str] = mapped_column(String(6))


class DepositOption(ProductOption, Base):
    __tablename__ = "bankings_depositoptionlist"
    product_id: Mapped[int] = mapped_column("product_id", ForeignKey("bankings_depositbaselist.id", ondelete="CASCADE"))
    product: Mapped[DepositBase] = relationship(back_populates="options")


class SavingOption(ProductOption, Base):
    __tablename__ = "bankings_savingoptionlist"
    product_id: Mapped[int] = mapped_column("product_id", ForeignKey("bankings_savingbaselist.id", ondelete="CASCADE"))
    product: Mapped[SavingBase] = relationship(back_populates="options")


review_likes = Table("bankings_productreview_likes", Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("productreview_id", ForeignKey("bankings_productreview.id", ondelete="CASCADE")),
    Column("user_id", ForeignKey("accounts_user.id", ondelete="CASCADE")),
)


class ProductReview(Base):
    __tablename__ = "bankings_productreview"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE"))
    product_type: Mapped[str] = mapped_column(String(10))
    product_name: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped[User] = relationship()
    likes: Mapped[list[User]] = relationship(secondary=review_likes)
    comments: Mapped[list["ReviewComment"]] = relationship(back_populates="review", cascade="all, delete-orphan")


class ReviewComment(Base):
    __tablename__ = "bankings_reviewcomment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("bankings_productreview.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    review: Mapped[ProductReview] = relationship(back_populates="comments")
    user: Mapped[User] = relationship()


class Exchange(Base):
    __tablename__ = "currencies_exchangelist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cur_unit: Mapped[str] = mapped_column(String(100), unique=True)
    ttb: Mapped[str] = mapped_column(String(100)); tts: Mapped[str] = mapped_column(String(100)); deal_bas_r: Mapped[str] = mapped_column(String(100))
    bkpr: Mapped[str] = mapped_column(String(100)); yy_efee_r: Mapped[str] = mapped_column(String(100)); ten_dd_efee_r: Mapped[str] = mapped_column(String(100))
    kftc_bkpr: Mapped[str] = mapped_column(String(100)); kftc_deal_bas_r: Mapped[str] = mapped_column(String(100)); cur_nm: Mapped[str] = mapped_column(String(100))


class Stock(Base):
    __tablename__ = "stocks_stocklist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bas_dt: Mapped[str] = mapped_column(String(10)); idx_nm: Mapped[str] = mapped_column(String(100)); idx_csf: Mapped[str | None] = mapped_column(String(100), nullable=True)
    epy_itms_cnt: Mapped[int] = mapped_column(Integer, default=0); clpr: Mapped[float] = mapped_column(Float, default=0); vs: Mapped[float] = mapped_column(Float, default=0); flt_rt: Mapped[float] = mapped_column(Float, default=0); mkp: Mapped[float] = mapped_column(Float, default=0); hipr: Mapped[float] = mapped_column(Float, default=0); lopr: Mapped[float] = mapped_column(Float, default=0)
    trqu: Mapped[int] = mapped_column(Integer, default=0); tr_prc: Mapped[int] = mapped_column(Integer, default=0); lstg_mrkt_tot_amt: Mapped[int] = mapped_column(Integer, default=0)


class News(Base):
    __tablename__ = "economics_newslist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True); originallink: Mapped[str] = mapped_column(String(500)); link: Mapped[str] = mapped_column(String(500)); description: Mapped[str] = mapped_column(Text); pub_date: Mapped[str] = mapped_column(String(100))


class UserSurvey(Base):
    __tablename__ = "surveys_usersurvey"
    id: Mapped[int] = mapped_column(Integer, primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE"))
    age_group: Mapped[str] = mapped_column(String(20)); income_source: Mapped[str] = mapped_column(String(20)); asset_size: Mapped[str] = mapped_column(String(20)); financial_purpose: Mapped[str] = mapped_column(String(20)); important_factor: Mapped[str] = mapped_column(String(20)); expected_return: Mapped[str] = mapped_column(String(20), default=""); investment_period: Mapped[str] = mapped_column(String(20), default=""); financial_products: Mapped[str] = mapped_column(String(100)); preferred_bank: Mapped[str] = mapped_column(String(20)); banking_channel: Mapped[str] = mapped_column(String(20), default=""); recent_investment: Mapped[bool | None] = mapped_column(Boolean, nullable=True); risk_tolerance: Mapped[str] = mapped_column(String(20), default=""); preferred_product: Mapped[str] = mapped_column(String(20), default=""); preferred_method: Mapped[str] = mapped_column(String(20), default=""); monthly_investment: Mapped[str] = mapped_column(String(20), default=""); preferred_benefit: Mapped[str] = mapped_column(String(20), default=""); service_priority: Mapped[str] = mapped_column(String(20), default=""); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions_subscribedproduct"
    id: Mapped[int] = mapped_column(Integer, primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE")); product_id: Mapped[str] = mapped_column(String(255)); product_name: Mapped[str] = mapped_column(String(255)); subscribed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "chats_conversation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("accounts_user.id", ondelete="CASCADE")); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "chats_message"
    id: Mapped[int] = mapped_column(Integer, primary_key=True); conversation_id: Mapped[int] = mapped_column(ForeignKey("chats_conversation.id", ondelete="CASCADE")); role: Mapped[str] = mapped_column(String(10)); content: Mapped[str] = mapped_column(Text); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")
