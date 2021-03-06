def calculate_calories(profile):
    goal_calories = 0

    # calculate BMR based on information given
    if profile["weight"] and profile["heightFeet"] and profile["heightInches"] and profile["age"]:
        # BMR = 10 * weight in kg + 6.25 * height in cm - 5 * age + (5 if male, -161 if female)
        goal_calories = 10 * 0.453592 * profile["weight"] + \
                        6.25 * (30.48 * profile["heightFeet"] + 0.393701 * profile["heightInches"]) - \
                        5 * profile["age"]
        if profile["gender"] == "male":
            goal_calories += 5
        else:
            goal_calories -= 161
    else:                                   # if no information given, assume average BMR
        if profile["gender"] == "male":     # Based on daily consumption of 2500 calories per day
            goal_calories = 2080
        else:                               # Based on daily consumption of 2000 calories per day
            goal_calories = 1666
    
    # Apply multiplier based on activity level.
    if profile["activityLevel"] == "Lightly Active":
        goal_calories *= 1.375
    elif profile["activityLevel"] == "Moderately Active":
        goal_calories *= 1.55
    elif profile["activityLevel"] == "Very Active":
        goal_calories *= 1.725
    else: # Default = Sedentary
        goal_calories *= 1.2

    # Apply personal goals
    if profile["weeklyTarget"] == "Lose 2.0 lb/week":
        goal_calories -= 1000
    elif profile["weeklyTarget"] == "Lose 1.5 lb/week":
        goal_calories -= 750
    elif profile["weeklyTarget"]== "Lose 1.0 lb/week":
        goal_calories -= 500
    elif profile["weeklyTarget"]== "Lose 0.5 lb/week":
        goal_calories -= 250
    elif profile["weeklyTarget"]== "Gain 0.5 lb/week":
        goal_calories += 250
    elif profile["weeklyTarget"]== "Gain 1.0 lb/week":
        goal_calories += 500
    elif profile["weeklyTarget"]== "Gain 1.5 lb/week":
        goal_calories += 750
    else: # Default = Maintain weight
        goal_calories = goal_calories

    return goal_calories