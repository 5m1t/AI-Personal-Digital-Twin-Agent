from ..database import DatabaseRepository
import datetime

db = DatabaseRepository()

def log_transaction(amount: float, type: str, category: str, description: str = "") -> str:
    """Logs a financial transaction (income or expense) for budgeting.
    
    Args:
        amount: Transaction value (e.g. 45.50).
        type: Transaction type ('income' or 'expense').
        category: Expense/Income category (e.g. 'food', 'rent', 'learning', 'subscriptions', 'salary').
        description: Note about the transaction (e.g., 'Groceries at Whole Foods').
    """
    try:
        if type not in ('income', 'expense'):
            return "Error: type must be 'income' or 'expense'."
        today_str = datetime.date.today().isoformat()
        log_id = db.add_finance_log(today_str, category, amount, type, description)
        return f"Successfully logged {type} of ${amount:.2f} under '{category}'. Log ID: {log_id}."
    except Exception as e:
        return f"Error logging transaction: {str(e)}"

def get_financial_report() -> str:
    """Retrieves transaction logs and calculates net balance, total income, expenses, and suggestions."""
    try:
        logs = db.list_finance_logs()
        if not logs:
            return "No financial logs found."
            
        total_income = 0
        total_expense = 0
        categories = {}
        
        output = []
        output.append("### Recent Transactions:")
        # Show last 10 transactions
        for l in logs[:10]:
            output.append(f"- {l['date']} | {l['type'].upper()} | ${l['amount']:.2f} | Category: {l['category']} | {l['description']}")
            
        for l in logs:
            if l['type'] == 'income':
                total_income += l['amount']
            else:
                total_expense += l['amount']
                categories[l['category']] = categories.get(l['category'], 0) + l['amount']
                
        net_savings = total_income - total_expense
        output.append(f"\n### Financial Summary:")
        output.append(f"Total Income: ${total_income:.2f}")
        output.append(f"Total Expenses: ${total_expense:.2f}")
        output.append(f"Net Savings: ${net_savings:.2f}")
        
        if categories:
            output.append("\n### Expense by Category:")
            for cat, amt in categories.items():
                pct = (amt / total_expense) * 100 if total_expense > 0 else 0
                output.append(f"- {cat.capitalize()}: ${amt:.2f} ({pct:.1f}%)")
                
        # Simple advice
        if total_expense > 0 and (categories.get('subscriptions', 0) / total_expense) > 0.15:
            output.append("\n💡 Recommendation: Subscriptions make up more than 15% of your total expenses. Consider reviewing unused services.")
        if net_savings < 0:
            output.append("\n💡 Recommendation: You are running a deficit this month. Try to set a strict weekly dining-out budget.")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error generating financial report: {str(e)}"
