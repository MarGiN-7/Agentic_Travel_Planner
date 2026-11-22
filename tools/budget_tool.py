from langchain.tools import tool

@tool
def budget_estimation(flight_cost: float, hotel_price_per_night: float, num_days: int, daily_expenses: float = 1500):
    """
    Estimate the total budget for a trip.
    Includes flight cost, hotel cost for the duration, and estimated daily local expenses (food, local travel).
    """
    try:
        hotel_total = hotel_price_per_night * (num_days - 1) # Assuming nights = days - 1
        local_total = daily_expenses * num_days
        total_cost = flight_cost + hotel_total + local_total
        
        breakdown = {
            "flight": flight_cost,
            "hotel": hotel_total,
            "local_expenses": local_total,
            "total": total_cost
        }
        
        result = (f"Budget Breakdown:\n"
                  f"- Flight: ₹{flight_cost}\n"
                  f"- Hotel ({num_days-1} nights): ₹{hotel_total}\n"
                  f"- Local Expenses ({num_days} days): ₹{local_total}\n"
                  f"-------------------------------------\n"
                  f"Total Estimated Cost: ₹{total_cost}")
        return result
    except Exception as e:
        return f"Error calculating budget: {str(e)}"
