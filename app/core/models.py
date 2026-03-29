# 导入所有表类以便 metadata 完整
from app.auth.model import User  # noqa: F401
from app.families.model import Family, FamilyInvite, FamilyMember  # noqa: F401
from app.foods.model import Food  # noqa: F401
from app.profiles.model import Profile  # noqa: F401
from app.nutrition.model import NutritionPreference  # noqa: F401
from app.reminders.model import Reminder  # noqa: F401
from app.weights.model import WeightRecord  # noqa: F401
