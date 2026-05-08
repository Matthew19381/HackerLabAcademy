from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class WriteupTemplate(Base):
    __tablename__ = "writeup_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "DVWA SQLi Report"
    category = Column(String, nullable=False)  # "lab", "ctf", "general"
    template_md = Column(Text, nullable=False)  # Markdown template with {{variables}}
    variables_json = Column(Text, nullable=True)  # JSON schema: [{"name": "vuln", "type": "string", "label": "Vulnerability"}]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Writeup(Base):
    __tablename__ = "writeups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("writeup_templates.id"), nullable=True)
    title = Column(String, nullable=False)
    content_md = Column(Text, nullable=False)  # Filled markdown
    rendered_pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    template = relationship("WriteupTemplate", backref="writeups")
