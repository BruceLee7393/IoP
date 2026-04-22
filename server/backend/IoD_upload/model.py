from sqlalchemy import Column, DateTime, Integer, VARCHAR, JSON
from backend.extensions import db


class IoD_upload(db.Model):
    __tablename__ = "iod_upload"

    # id 不再自动生成，而是直接接收设备端的id
    id = Column(VARCHAR(100), primary_key=True, comment="设备生成的唯一消息ID")
    device_id = Column(VARCHAR(64), index=True, nullable=False, comment="设备唯一id")
    event_type = Column(Integer, nullable=False, comment="事件类型")
    event_record = Column(JSON, nullable=False, comment="事件详细说明")
    upload_status = Column(
        Integer, nullable=False, default=0, comment="上传状态，0--待上传，1--已上传"
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="上传重试次数")
    event_time = Column(DateTime, nullable=False, comment="事件发生时间")
    last_upload_time = Column(DateTime, comment="最近一次尝试上传时间")
    ack_time = Column(DateTime, comment="收到确认回执时间")

    def __repr__(self):
        return f"<IoD_Record {self.id} from {self.device_id}>"
