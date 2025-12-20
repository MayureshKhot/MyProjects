import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv(r"D:\NareshIT_PrakashSenapati\My Projects\Resume Projects\Predictive Marketing Campaign Optimizer\marketing_and_product_performance.csv")
print(data.info())
print(data.isna().sum())
print(data.duplicated().sum())

print(data['Subscription_Tier'].value_counts())
print(data.nunique())
print(data.describe())