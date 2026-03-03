try:
    num_brothers = int(input("Enter the total number of active brothers: "))
    
    if num_brothers <= 35: 
        hq_fees = 7950
        hq_fees += 10.34 * num_brothers
    
    if num_brothers >= 35:
        hq_fees = 10.34 * num_brothers
        hq_fees += 1300
        hq_fees += 190 * num_brothers
    
    local_budget = float(input("Budget: "))

    total_due = hq_fees + local_budget
    dues_per_brother = total_due / num_brothers
    
    print(f"\nTotal Capital Needed + SAJ: ${total_due:,.2f}")
    print(f"Minimum dues per brother per year + SAJ: ${dues_per_brother:,.2f}")
    print(f"Minimum dues per brother per semester + SAJ: ${dues_per_brother/2:,.2f}")

except ValueError:
    print("Error: Enter a valid number.")