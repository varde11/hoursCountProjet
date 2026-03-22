from schema import ContractOutput

def get_planned_hours(contract: ContractOutput) -> float:
    if contract.daily_hours is not None and contract.mission_days is not None:
        mission_estimated = contract.daily_hours * contract.mission_days

        # mission très courte : on privilégie l'horaire réel
        if contract.mission_days <= 3:
            return mission_estimated

    if (
        contract.base_hours is not None
        and contract.base_hours.type == "hebdomadaire"
        and contract.base_hours.valeur is not None
    ):
        return float(contract.base_hours.valeur)

    if contract.daily_hours is not None and contract.mission_days is not None:
        return contract.daily_hours * contract.mission_days

    if contract.base_hours is not None and contract.base_hours.valeur is not None:
        return float(contract.base_hours.valeur)

    return 0.0

def split_overtime_hours(actual_hours: float):
    normal = min(actual_hours, 35.0)

    overtime_25 = 0.0
    overtime_50 = 0.0

    if actual_hours > 35:
        overtime_25 = min(actual_hours, 43.0) - 35.0

    if actual_hours > 43:
        overtime_50 = actual_hours - 43.0

    return normal, overtime_25, overtime_50


def get_special_rule(contract: ContractOutput, label: str):
    for rule in contract.special_rate_rules:
        if rule.label == label:
            return rule
    return None



from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)