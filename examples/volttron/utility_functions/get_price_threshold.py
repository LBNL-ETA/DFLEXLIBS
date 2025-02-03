def get_price_threshold(price_schedule):
    
    price = price_schedule.copy()
    
    # Sort the prices in ascending order
    price.sort()

    # Calculate the index of the third quartile
    n = len(price)
    k = (3.0 * n - 1) / 4

    # Determine the price threshold as the third quartile
    if k == int(k):
        priceThreshold = price[int(k) - 1]
    else:
        priceThreshold = (price[int(k) - 1] + price[int(k)]) / 2

    return priceThreshold