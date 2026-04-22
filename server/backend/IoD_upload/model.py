import uuid
from sqlalchemy import Column, CHAR, DateTime, Integer, VARCHAR, JSON

# from sqlalchemy.orm import relationship
from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class IoD_upload(db.Model):
    __tablename__ = "iod_upload"

    id = Column(CHAR(36), primary_key=True, default=generate_uuid, comment="唯一标识符")
    device_id = Column(VARCHAR(64), index=True, nullable=False, comment="设备唯一id")
    event_type = Column(Integer, nullable=False, comment="事件类型")
    event_record = Column(JSON, nullable=False, comment="事件详细说明")
    upload_status = Column(
        Integer, nullable=False, default=0, comment="上传状态，0--待上传，1--已上传"
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="上传重试次数")
    # server_default 仅在插入（INSERT） 数据且该字段缺失时触发。设置初始状态、记录创建时间。
    # onupdate 仅在更新（UPDATE） 该行数据时触发。记录“最后修改时间”。
    event_time = Column(DateTime, nullable=False, comment="事件发生时间")
    last_upload_time = Column(DateTime, comment="最近一次尝试上传时间")
    ack_time = Column(DateTime, comment="收到确认回执时间")

    def __repr__(self):
        return f"<Device_id {self.device_id}>"
