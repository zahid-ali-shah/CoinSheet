from core.models import TypeOfPaymentModes


def get_expense_icon(payment_type):
    if payment_type == TypeOfPaymentModes.BANK:
        return "fa-solid fa-building-columns"
    elif payment_type == TypeOfPaymentModes.CASH:
        return "fa-solid fa-sack-dollar"
    elif payment_type == TypeOfPaymentModes.CREDIT:
        return "fa-solid fa-credit-card"
    else:
        return ""


def get_pre_month(month, year):
    if month == 1:
        previous_month = 12
        year = year - 1
    else:
        previous_month = month - 1
        year = year
    return previous_month, year
