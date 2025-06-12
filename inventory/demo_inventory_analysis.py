import pandas as pd
import random
from datetime import date, timedelta

def generate_virtual_data_v2():
    """
    Generates virtual sales and inventory data with non-negative inventory
    and a new absolute value replenishment logic.
    """
    # 1. Initialization
    start_date = date(2025, 1, 1)
    end_date = date(2025, 3, 30)
    
    distributor = "WuHan_Chuangjie"
    hub = "武汉创洁工贸淡化股份有限公司-武汉东西湖"
    brand = "H&S"
    
    channels = [
        'B Store', 'CB', 'CVS', 'DCP', 'DKS', 'DMW', 'DP.com', 
        'EB', 'Grocery & Others', 'HSM', 'ICP', 'MM', 'WS'
    ]
    
    sales_ranges = {
        'B Store': (100, 200), 'CB': (150, 450), 'CVS': (350, 850),
        'DCP': (300, 450), 'DKS': (0, 250), 'DMW': (0, 350),
        'DP.com': (150, 250), 'EB': (0, 50), 'Grocery & Others': (400, 1500),
        'HSM': (12000, 20000), 'MM': (800, 1200)
    }
    
    # Core logic variables
    all_data = []
    # Start with a reasonable inventory
    current_inv_eod = 80000.0 
    # NEW: Replenishment counter set to 5-7 days
    replenish_counter = random.randint(5, 7)
    icp_ws_counter = random.randint(2, 3)
    
    current_date = start_date
    
    # 2. Main Loop through each date
    while current_date <= end_date:
        # Inventory at the start of the day is the end-of-day inventory from yesterday
        inv_today_start = current_inv_eod
        
        # NEW: Check for replenishment (every 5-7 days)
        replenish_counter -= 1
        if replenish_counter == 0:
            # NEW: Add a random absolute amount, not a percentage
            replenishment_amount = random.uniform(10000, 20000)
            inv_today_start += replenishment_amount
            # NEW: Reset counter to 5-7 days
            replenish_counter = random.randint(5, 7)
            
        # Generate planned sales for the current day
        daily_sales_data = []
        total_daily_sales_planned = 0
        
        icp_ws_counter -= 1
        show_icp_ws = (icp_ws_counter == 0)

        for channel in channels:
            giv = 0
            if channel in ['ICP', 'WS']:
                if show_icp_ws:
                    giv = random.uniform(2000, 4000)
            else:
                low, high = sales_ranges[channel]
                giv = random.uniform(low, high)
            
            daily_sales_data.append({'channel': channel, 'giv': giv})
            total_daily_sales_planned += giv

        if show_icp_ws:
            icp_ws_counter = random.randint(2, 3)

        # NEW: Check if inventory is sufficient. If not, scale down sales.
        actual_total_sales = 0
        if total_daily_sales_planned > inv_today_start:
            # This simulates an out-of-stock situation
            scaling_factor = inv_today_start / total_daily_sales_planned
            for record in daily_sales_data:
                record['giv'] *= scaling_factor
            actual_total_sales = inv_today_start
        else:
            actual_total_sales = total_daily_sales_planned

        # Create rows for the current day
        date_str = current_date.strftime('%Y-%m-%d')
        for record in daily_sales_data:
            all_data.append({
                'Date': date_str,
                'Distributor': distributor,
                'Hub': hub,
                'Inv.Value(RMB)': round(inv_today_start, 2),
                'Product Hierarchy - Brand': brand,
                'Store Group Channel': record['channel'],
                'IDS GIV': round(record['giv'], 2)
            })
            
        # Update inventory for the end of the day
        current_inv_eod = inv_today_start - actual_total_sales
        
        current_date += timedelta(days=1)
        
    # 3. Create DataFrame and save to CSV
    df = pd.DataFrame(all_data)
    output_filename = "virtual_data_new_logic.csv"
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"Successfully generated data with new logic!")
    print(f"File saved as: {output_filename}")
    print("\n--- Data Head ---")
    print(df.head())
    print("\n--- Data Tail ---")
    print(df.tail())

# Run the function
generate_virtual_data_v2()