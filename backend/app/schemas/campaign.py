from pydantic import BaseModel, ConfigDict


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source: str
    tracking_number: str
