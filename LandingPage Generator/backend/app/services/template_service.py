from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class TemplateService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def initialize(self):
        await self._ensure_default_templates()

    async def _ensure_default_templates(self):
        count = await self.db.invoice_templates.count_documents({})
        if count == 0:
            default_templates = [
                {
                    "name": "Professional",
                    "description": "Clean and professional design",
                    "style": {
                        "primary_color": "#2C3E50",
                        "secondary_color": "#ECF0F1",
                        "font_family": "Helvetica",
                        "layout": "standard"
                    }
                },
                {
                    "name": "Modern",
                    "description": "Modern and minimalist design",
                    "style": {
                        "primary_color": "#3498DB",
                        "secondary_color": "#F8F9FA",
                        "font_family": "Arial",
                        "layout": "modern"
                    }
                }
            ]
            await self.db.invoice_templates.insert_many(default_templates)

    async def get_all_templates(self):
        templates = []
        cursor = self.db.invoice_templates.find()
        async for template in cursor:
            template["_id"] = str(template["_id"])
            templates.append(template)
        return templates

    async def get_template(self, template_id: str):
        template = await self.db.invoice_templates.find_one({"_id": ObjectId(template_id)})
        if template:
            template["_id"] = str(template["_id"])
        return template