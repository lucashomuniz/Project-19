
import warnings
import pandas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.metrics")

"""
==================================================================================================================================
 Q1: WHAT IS THE AVERAGE IMPACT GENERATED BY PROMOTION OVER THE TOTAL SALES? IS THAT IMPACT GENERAL FOR ALL BRANDS AND CUSTOMERS?
==================================================================================================================================
"""

# Load promotions and Sales Data
dataset1 = pandas.read_excel('Invoice.xlsx')
dataset2 = pandas.read_excel('Promo.xlsx')

# Convert date Columns to Datetime Format
dataset1['INVOICE_DT'] = pandas.to_datetime(dataset1['INVOICE_DT'])
dataset2['event_start_dt'] = pandas.to_datetime(dataset2['event_start_dt'])
dataset2['event_end_dt'] = pandas.to_datetime(dataset2['event_end_dt'])

# Identify if Invoice dates are Within the Promo Periods
promo_data = dataset2.sort_values('event_start_dt')
dataset1['in_promo'] = dataset1.apply(lambda row: ((promo_data['event_start_dt'] <= row['INVOICE_DT']) & (promo_data['event_end_dt'] >= row['INVOICE_DT'])).any(), axis=1)

# Replace True/False with 'IN'/'OUT' for Promo Status
dataset1['in_promo'] = dataset1['in_promo'].replace({True: 'IN', False: 'OUT'})

# Separate the Dates Inside and Outside Promo Periods
dates_in_promo = dataset1[dataset1['in_promo'] == 'IN']['INVOICE_DT']
dates_out_promo = dataset1[dataset1['in_promo'] == 'OUT']['INVOICE_DT']

# Calculate Percentages
total_dates = len(dataset1)
inside_promo_count = len(dates_in_promo)
outside_promo_count = len(dates_out_promo)

inside_promo_percentage = (inside_promo_count / total_dates) * 100
outside_promo_percentage = (outside_promo_count / total_dates) * 100

# Display the Results
print(f"\nDates within the Promotional Period: {len(dates_in_promo)} ({inside_promo_percentage:.2f}%)")
print(f"Dates outside the Promotional Period: {len(dates_out_promo)} ({outside_promo_percentage:.2f}%)")

# Merge promotions and Sales Data Based on 'basecode' and 'CUSTOMER_HIERARCHY_LVL2_CD'
merged_data = pandas.merge(dataset1, dataset2, left_on=['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD'], right_on=['basecode', 'customer_hierarchy_lvl2_cd'], how='left')

# Create a Column to Indicate Whether it has promo_cd
merged_data['has_promo'] = ~merged_data['promo_cd'].isna()

# Count the Distinct Amount of basecode and customer_hierarchy that Have and do Not Have promo_cd
promo_count = merged_data.groupby(['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD'])['has_promo'].agg(['sum', 'count']).reset_index()
promo_count.columns = ['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD', 'promo_yes', 'total']

# Quantity of Basecode and customer_hierarchy that have promo cd
promo_with_cd = promo_count['promo_yes'].sum()

# Quantity of basecode and customer_hierarchy that do not have promo_cd
promo_without_cd = promo_count['total'].sum() - promo_with_cd

# Total amount of basecode and customer_hierarchy
promo_total = promo_count['total'].sum()

# Calculate Percentage
promo_with_percent = (promo_with_cd / promo_total) * 100
promo_without_percent = (promo_without_cd / promo_total) * 100

# Analyze Promotions by Product and Customer
promo_summary = merged_data.groupby(["basecode", "CUSTOMER_HIERARCHY_LVL2_CD"]).agg({
    'promo_cd': 'count',  # Contar a quantidade de promoções
    'invoice_qty': 'sum'  # Somar o volume (invoice_qty) correspondente
}).reset_index()

# Display Summary Results With Number of Promotions and Volume
print(promo_summary)

# Display Quantity With and Without promo_cd
print(f"\nTotal Number of Promotions: {promo_total} (100%)")
print(f"Number of Combinations WITH Promotions: {promo_with_cd} ({promo_with_percent:.2f}%)")
print(f"Number of Combinations WITHOUT Promotions: {promo_without_cd} ({promo_without_percent:.2f}%)")

# Display the Total volume Quantity (invoice_qty) With and Without Promotions
promo_qty_with = merged_data[merged_data['has_promo'] == True]['invoice_qty'].sum()
promo_qty_without = merged_data[merged_data['has_promo'] == False]['invoice_qty'].sum()

# Total Amount of Volume
promo_qty_total = promo_qty_with + promo_qty_without

# Calculate Percentages for Volume
promo_qty_with_percent = (promo_qty_with / promo_qty_total) * 100
promo_qty_without_percent = (promo_qty_without / promo_qty_total) * 100

# Display Total Volume Amount and Percentages
print(f"\nTotal Volume Quantity: {promo_qty_total} (100%)")
print(f"Number of Combinations WITH Promotions: {promo_qty_with} ({promo_qty_with_percent:.2f}%)")
print(f"Number of Combinations WITHOUT Promotions: {promo_qty_without} ({promo_qty_without_percent:.2f}%)")

# Separating Data Into Two Groups: With Promotions and Without Promotions
promo_group = merged_data[merged_data['has_promo'] == True]
no_promo_group = merged_data[merged_data['has_promo'] == False]

# Calculation Based on Average Sales Per Period (With and Without Promotions)
mean_sales_with_promo = promo_group['invoice_qty'].mean()
mean_sales_without_promo = no_promo_group['invoice_qty'].mean()

# Percentage Impact Calculation
if mean_sales_without_promo > 0:
    impacto_percentual = ((mean_sales_with_promo - mean_sales_without_promo) / mean_sales_without_promo) * 100
else:
    impacto_percentual = 0

# Display Average Results
print(f"\nAverage Sales WITH promotions: {mean_sales_with_promo}")
print(f"Average Sales WITHOUT promotions: {mean_sales_without_promo}")
print(f"Percentage Impact of Promotions on Sales: {impacto_percentual:.2f}%")

"""
==================================================================================================================================
Q2: CONSIDERING THE APPROVED PROMOTIONS FOR THE LAST QUARTER OF 2018, HOW MANY TONS OF PRODUCTS ARE WE GOING TO SELL IN Q4 2018?
==================================================================================================================================
"""

# Set the Period to Q4 2018
q4_2018_start = pandas.to_datetime('2018-10-01')
q4_2018_end = pandas.to_datetime('2018-12-31')

# Filter Promotions Occurring in Q4 2018
promo_q4_2018 = dataset2[(dataset2['event_start_dt'] >= q4_2018_start) & (dataset2['event_end_dt'] <= q4_2018_end)]

# Display the Number of Promotions and the Combinations of basecode and customer_hierarchy
print(f"\nTotal Promotions Q4 2018: {len(promo_q4_2018)}")
promo_combinations_q4_2018 = promo_q4_2018[['basecode', 'customer_hierarchy_lvl2_cd']].drop_duplicates()
print(f"Total Combinations Q4 2018: {len(promo_combinations_q4_2018)}")

# Set the Period to Q4 2017
q4_2017_start = pandas.to_datetime('2017-10-01')
q4_2017_end = pandas.to_datetime('2017-12-31')

# Filter Sales that Occurred in Q4 2017
q4_sales_2017 = dataset1[(dataset1['INVOICE_DT'] >= q4_2017_start) & (dataset1['INVOICE_DT'] <= q4_2017_end)]

# Filter sales in Q4 2017 with basecode and customer_hierarchy combinations from Q4 2018
filtered_sales_q4_2017 = pandas.merge(q4_sales_2017, promo_combinations_q4_2018, how='inner',
                                      left_on=['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD'],
                                      right_on=['basecode', 'customer_hierarchy_lvl2_cd'])

# Sum the Total Volume for each Combination of basecode and customer_hierarchy
grouped_sales_q4_2017 = filtered_sales_q4_2017.groupby(['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD'])['invoice_qty'].sum().reset_index()

# Display the Volume Sum for Each Combination
print(f"Total Combinations Q4 2017: {len(grouped_sales_q4_2017)}")
print(f"Total Volume Q4 2017: {sum(grouped_sales_q4_2017['invoice_qty'])}")

# Train the Gradient Boosting Machines (GBM) model
X = grouped_sales_q4_2017[['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD']]  # Input variables
y = grouped_sales_q4_2017['invoice_qty']  # Output variables

# Use LabelEncoder to Encode Basecode and customer_hierarchy
le_basecode = LabelEncoder()
le_customer = LabelEncoder()

# Apply LabelEncoder to Input Columns Using `.loc[]`
X.loc[:, 'basecode'] = le_basecode.fit_transform(X['basecode'])
X.loc[:, 'CUSTOMER_HIERARCHY_LVL2_CD'] = le_customer.fit_transform(X['CUSTOMER_HIERARCHY_LVL2_CD'])

# Scale the Input Data
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split Data Into Training and Testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Gradient Boosting Machines Model
model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

# Make Predictions on The Test Set
y_pred = model.predict(X_test)

# Evaluate the Model with MAE and RMSE and R2
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)
print(f"\nMean Absolute Error (MAE): {mae:.2f} toneladas")
print(f"Root Mean Square Error (RMSE): {rmse:.2f} toneladas")
print(f"Coefficient of Determination (R²): {r2:.4f}")

# Forecast Sales for Q4 2018
X_pred_2018 = promo_combinations_q4_2018.copy()

# Adjust Column Names to Ensure Consistency
X_pred_2018.columns = ['basecode', 'CUSTOMER_HIERARCHY_LVL2_CD']

# Only Use Combinations Present in Q4 2017
X_pred_2018 = X_pred_2018[X_pred_2018['basecode'].isin(le_basecode.classes_) & X_pred_2018['CUSTOMER_HIERARCHY_LVL2_CD'].isin(le_customer.classes_)]

# Encode 2018 Data Using `.loc[]`
X_pred_2018.loc[:, 'basecode'] = le_basecode.transform(X_pred_2018['basecode'])
X_pred_2018.loc[:, 'CUSTOMER_HIERARCHY_LVL2_CD'] = le_customer.transform(X_pred_2018['CUSTOMER_HIERARCHY_LVL2_CD'])

# Scale The Input Data for Prediction
X_pred_2018 = scaler.transform(X_pred_2018)

# Make the Forecast for Q4 2018
y_pred_2018 = model.predict(X_pred_2018)

# Display the Total Forecast For Q4 2018
print(f"Sales Forecast for Q4 2018: {y_pred_2018.sum():.2f} toneladas")
