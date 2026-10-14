from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignProfile:
    name: str
    source: str
    tracking_number: str
    share_of_calls: float
    missed_rate: float
    conversion_rate_when_answered: float

    def missed_threshold(self) -> float:
        return self.missed_rate

    def converted_threshold(self) -> float:
        return self.missed_rate + (1 - self.missed_rate) * self.conversion_rate_when_answered


@dataclass(frozen=True)
class DemoAccount:
    name: str
    timezone: str
    user_name: str
    user_email: str
    user_password: str
    api_key_setting: str
    campaigns: tuple[CampaignProfile, ...]


ACME = DemoAccount(
    name="Acme Home Services",
    timezone="America/Chicago",
    user_name="Dana Brooks",
    user_email="manager@acme.test",
    user_password="acme-demo",
    api_key_setting="demo_api_key_acme",
    campaigns=(
        CampaignProfile("Google Search - Emergency Plumbing", "Google Ads", "+15550100001", 0.30, 0.12, 0.38),
        CampaignProfile("Google Search - HVAC Repair", "Google Ads", "+15550100002", 0.20, 0.15, 0.31),
        CampaignProfile("Facebook - Spring Tune-Up", "Facebook Ads", "+15550100003", 0.15, 0.22, 0.14),
        CampaignProfile("Direct Mail - Fall Postcard", "Direct Mail", "+15550100004", 0.10, 0.18, 0.21),
        CampaignProfile("Organic - Website", "Organic Search", "+15550100005", 0.15, 0.10, 0.27),
        CampaignProfile("Local Radio - Morning Show", "Radio", "+15550100006", 0.10, 0.25, 0.09),
    ),
)

SUMMIT = DemoAccount(
    name="Summit Auto Group",
    timezone="America/New_York",
    user_name="Marcus Lee",
    user_email="manager@summit.test",
    user_password="summit-demo",
    api_key_setting="demo_api_key_summit",
    campaigns=(
        CampaignProfile("Google Search - New Inventory", "Google Ads", "+15550200001", 0.28, 0.14, 0.22),
        CampaignProfile("Google Search - Service Center", "Google Ads", "+15550200002", 0.22, 0.10, 0.41),
        CampaignProfile("Facebook - Trade-In Event", "Facebook Ads", "+15550200003", 0.15, 0.20, 0.12),
        CampaignProfile("TV - Weekend Sales Spot", "TV", "+15550200004", 0.12, 0.30, 0.08),
        CampaignProfile("Bing - Certified Pre-Owned", "Bing Ads", "+15550200005", 0.08, 0.12, 0.19),
        CampaignProfile("Organic - Website", "Organic Search", "+15550200006", 0.15, 0.09, 0.25),
    ),
)

DEMO_ACCOUNTS = (ACME, SUMMIT)
