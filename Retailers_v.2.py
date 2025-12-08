# %% [markdown]
# # Analysis of Meat Distribution in the RN Retail Network
# 
# This notebook contains the statistical analysis to evaluate hypotheses related to the origin and quality of meat sold in the retail network of Rio Grande do Norte (RN).
# 
# The objective is to understand the relationships between retailer size and the distance of meat origin, sanitary quality, and product processing level.
# 
# ## Hypotheses
# 
# 1. **Larger retailers sell meat sourced from greater distances.**
#    - Independent Variable (IV): Retailer size (`porte_loja`)
#    - Dependent Variable (DV): Distance from origin (`distancia_km`)
#    - Covariate: Census tract income (`renda_setor`)
# 
# 2. **Larger retailers sell more ultra-processed foods.**
#    - IV: Retailer size (`porte_loja`)
#    - DV: Processing level (`processamento`)
#    - Covariate: Census tract income (`renda_setor`)
# 
# 3. **Larger retailers display higher sanitary quality.**
#    - IV: Retailer size (`porte_loja`)
#    - DV: Sanitary performance (`desc_desempenho_sanitario`)
#    - Covariate: Census tract income (`renda_setor`)

# %%
# Import required libraries
import pandas as pd

pd.set_option(
    "display.max_columns", None
)  # Configure pandas to display all DataFrame columns

# %%
# Load the dataset
df = pd.read_csv("entrada/20240615_carnestotais_att.csv")
df  # Display the first few rows of the DataFrame

# %%
# Convert string-formatted numerical columns to floats
float_cols = [
    "lng_loja",
    "lat_loja",
    "lng_frigo",
    "lat_frigo",
    "distancia_km",
    "renda_setor",
]
for col in float_cols:
    df[col] = (
        df[col].str.replace(",", ".").astype(float)
    )  # Replace commas with dots and convert to float

# %%
# Clean and standardize text columns
df.columns = [
    i.strip() for i in df.columns
]  # Strip extra whitespace from column names

for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[
            col
        ].str.strip()  # Strip extra whitespace from text entries

# %%
# Save the cleaned DataFrame to a CSV file, excluding the index
df.to_csv("saida/20240615_carnestotais_att_nonans.csv", index=False)

# %% [markdown]
# #Descriptive Analysis
# #Where does the meat distributed in the RN retail network come from?

# %%
# Display frequency counts of slaughterhouse states
df.uf_frigo.value_counts()

# %%
## Frequency of Meat Originating from Outside the Northeast Region

northeast_states = ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE']
meat_outside_ne = df[~df['uf_frigo'].isin(northeast_states)]
total_obs = len(df)
count_outside = len(meat_outside_ne)
percentage_outside = (count_outside / total_obs) * 100

# Display the results
print(f"Percentage from outside the Northeast: {percentage_outside:.2f}%")

# %%
import geopandas as gpd
import matplotlib.pyplot as plt

# Path to the GeoJSON file
geojson_url = "entrada/brazil-states.geojson"

# Load data
estados = gpd.read_file(geojson_url)
estado_frequencia = df["uf_frigo"].value_counts()
estados["freq"] = estados["sigla"].map(estado_frequencia).fillna(0)

# 1. Increase Figure Size (Standard A4 width is approx 8 inches, so 20 is very large/high quality)
fig, ax = plt.subplots(1, 1, figsize=(20, 20))

# 2. Plot with improved aesthetics
estados.plot(
    column="freq",
    ax=ax,
    legend=True,
    edgecolor="#606060",  # Darker grey for better contrast
    linewidth=0.8,        # Slightly thicker lines
    cmap="Greens",
    legend_kwds={
        "label": "Frequency of slaughterhouses for all types of meat",
        "orientation": "horizontal",
        "shrink": 0.6,    # Make the legend bar shorter
        "pad": 0.02,      # Move legend closer to the map
        "aspect": 30      # Make the legend bar thinner
    },
)

# 3. Improve Labels (Font size, Bold text, Only show non-zero values)
for x, y, label in zip(
    estados.centroid.x, estados.centroid.y, (estados["freq"].astype(int))
):
    # Only label states that actually have data (optional, remove 'if' to show all)
    if label > 0:
        ax.text(
            x, y, 
            label, 
            color="black", 
            fontsize=14,       # Larger text
            fontweight="bold", # Bold text
            ha="center", 
            va="center"
        )

# Remove axis
plt.axis("off")

# 4. Save with High Resolution and Tight Bounding Box
plt.savefig(
    "saida/carne_total_high_res.png", 
    dpi=600,               # High resolution for print
    bbox_inches='tight',   # Removes extra white space
    pad_inches=0.1         # Small padding around the image
)

plt.show()

# %%
df.carne.value_counts().index

# %%
# 1. Filter data for Beef only ("Carne bovina")
df_beef = df[df.carne == "Carne bovina"]

# 2. Calculate frequency of each state for Beef
beef_frequency = df_beef["uf_frigo"].value_counts()

# 3. Map the frequency back to the GeoDataFrame
# Fill missing values with 0 so the map plots correctly
estados["freq"] = estados["sigla"].map(beef_frequency).fillna(0)

# 4. Initialize the plot with high-quality dimensions
fig, ax = plt.subplots(1, 1, figsize=(20, 20))

# 5. Create the choropleth map
estados.plot(
    column="freq",
    ax=ax,
    legend=True,
    cmap="PuBu",          # Purple-Blue colormap specific for Beef
    edgecolor="#606060",  # Darker grey for better definition
    linewidth=0.8,        # Slightly thicker lines
    legend_kwds={
        "label": "Frequency of slaughterhouses for beef",
        "orientation": "horizontal",
        "shrink": 0.6,    # Compact legend
        "pad": 0.02,      # Closer to map
        "aspect": 30      # Thinner bar
    },
)

# 6. Annotate the map (Smart Labeling)
for x, y, label in zip(
    estados.centroid.x, estados.centroid.y, (estados["freq"].astype(int))
):
    # Only label states that have data (avoid cluttering with '0')
    if label > 0:
        ax.text(
            x, y, 
            label, 
            color="black", 
            fontsize=14,       # Larger text for readability
            fontweight="bold", # Bold text
            ha="center", 
            va="center"
        )

# 7. Final adjustments and saving
plt.axis("off")
plt.savefig(
    "saida/bovina_high_res.png", 
    dpi=600,              # High resolution for print
    bbox_inches='tight',  # Remove extra white space
    pad_inches=0.1
)

plt.show()

# %%
import geopandas as gpd
import matplotlib.pyplot as plt

#Filter data for Poultry only ("Frango")
df_poultry = df[df.carne == "Frango"]

#Calculate frequency of each state for Poultry
poultry_frequency = df_poultry["uf_frigo"].value_counts()

#Map the frequency back to the GeoDataFrame
# Fill missing values with 0 so the map plots correctly
estados["freq"] = estados["sigla"].map(poultry_frequency).fillna(0)

#Initialize the plot with high-quality dimensions
fig, ax = plt.subplots(1, 1, figsize=(20, 20))

#Create the choropleth map
estados.plot(
    column="freq",
    ax=ax,
    legend=True,
    edgecolor="#606060",  
    linewidth=0.8,        
    cmap="Reds",         
    legend_kwds={
        "label": "Frequency of slaughterhouses for poultry",
        "orientation": "horizontal",
        "shrink": 0.6,  
        "pad": 0.02,     
        "aspect": 30      
    },
)

#Annotate the map (Smart Labeling)
for x, y, label in zip(
    estados.centroid.x, estados.centroid.y, (estados["freq"].astype(int))
):
    # Only label states that have data (avoid cluttering with '0')
    if label > 0:
        ax.text(
            x, y, 
            label, 
            color="black", 
            fontsize=14,       
            fontweight="bold", 
            ha="center", 
            va="center"
        )

#Final adjustments and saving
plt.axis("off")
plt.savefig(
    "saida/frango_high_res.png", 
    dpi=600,              
    bbox_inches='tight',  
    pad_inches=0.1
)

plt.show()

# %%
import geopandas as gpd
import matplotlib.pyplot as plt

# Filter data for Pork only ("suina")
df_pork = df[df.carne == "suina"]

# Calculate frequency of each state for Pork
pork_frequency = df_pork["uf_frigo"].value_counts()

# Map the frequency back to the GeoDataFrame
# Fill missing values with 0 so the map plots correctly
estados["freq"] = estados["sigla"].map(pork_frequency).fillna(0)

#Initialize the plot with high-quality dimensions
fig, ax = plt.subplots(1, 1, figsize=(20, 20))

#Create the choropleth map
estados.plot(
    column="freq",
    ax=ax,
    legend=True,
    edgecolor="#606060",  
    linewidth=0.8,        
    cmap="Purples",       
    legend_kwds={
        "label": "Frequency of slaughterhouses for swine", # 
        "orientation": "horizontal",
        "shrink": 0.6,    
        "pad": 0.02,      
        "aspect": 30     
    },
)

#Annotate the map (Smart Labeling)
for x, y, label in zip(
    estados.centroid.x, estados.centroid.y, (estados["freq"].astype(int))
):
    # Only label states that have data (avoid cluttering with '0')
    if label > 0:
        ax.text(
            x, y, 
            label, 
            color="black", 
            fontsize=14,       
            fontweight="bold", 
            ha="center", 
            va="center"
        )

#Final adjustments and saving
plt.axis("off")
plt.savefig(
    "saida/suina_high_res.png", 
    dpi=600,              
    bbox_inches='tight',  
    pad_inches=0.1
)

plt.show()

# %% [markdown]
# # Hypotheses and Variables
# 
# ## Hypothesis 1 - Larger retailers sell meat sourced from greater distances
# 
# * **Independent Variable (IV):** Retailer size (`porte_loja`)
# * **Dependent Variable (DV):** Distance from origin (`distancia_km`) - All meat types
# * **Covariate:** Census tract income (`renda_setor`)

# %%
# Reset the index of the DataFrame to ensure it is continuous
df.reset_index(drop=True, inplace=True)

# Check for any missing values (NaN) in the columns
print(df.isnull().any())

# %%
# Remove rows where census tract income data ('renda_setor') is missing
df.dropna(subset=["renda_setor"], inplace=True)

# %%
# Convert retailer size ('porte_loja') to a categorical data type
df["porte_loja"] = df["porte_loja"].astype("category")

# %%
import plotly.express as px

#Dictionary to translate Retailer Size categories to English
mapping_dict = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets"
}

df["porte_loja"] = df["porte_loja"].replace(mapping_dict)

#Create the Box Plot with High-Quality Settings
fig = px.box(
    df,
    x="porte_loja",
    y="distancia_km",
    title="Meat Sourcing Distance by Retailer Type",
    labels={
        "porte_loja": "",
        "distancia_km": "Distance from Origin (km)",
    },
    color="porte_loja",       
    template="plotly_white",  
)

# 3. Refine Layout for Publication Quality
fig.update_layout(
    title_x=0.5,           
    font=dict(
        family="Arial",    
        size=14,           
        color="black"
    ),
    showlegend=False,      
    yaxis=dict(
        showgrid=True,             
        gridcolor='lightgrey',     
        zeroline=False,             
    ),
    xaxis=dict(
        showgrid=False,            
        linecolor='white'          
    ),
    # Optional: Set specific figure dimensions for consistent export quality
    # width=1000,
    # height=600,
)

# 4. Save and Display
fig.write_html("saida/hipotese1_translated.html")
fig.show()

# %%
import plotly.express as px
#Ensure Retailer Types are in English if not already applied

mapping_dict = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets"
}
# Only apply if the values are still in Portuguese
if df["porte_loja"].isin(["Acougue", "Supermercado"]).any():
    df["porte_loja"] = df["porte_loja"].replace(mapping_dict)

#Create the Scatter Plot
# Visualizing the relationship between Neighborhood Income and Sourcing Distance
# 'trendline="ols"' adds an Ordinary Least Squares regression line to check for correlations
fig = px.scatter(
    df,
    x="renda_setor",
    y="distancia_km",
    color="porte_loja",
    title="Census Tract Income vs. Meat Sourcing Distance",
    labels={
        "renda_setor": "Census Tract Income (BRL)", # BRL or R$
        "distancia_km": "Distance from Origin (km)",
        "porte_loja": "Retailer Type",
    },
    trendline="ols",         
    template="plotly_white",  
)

#Refine Layout
fig.update_layout(
    title_x=0.5,              
    font=dict(size=14),       
    legend=dict(
        title="Retailer Type",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.02                
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgrey'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgrey'
    )
)

#Save and Display
fig.write_html("saida/hipotese1_acessorio_renda_translated.html")
fig.show()

# %%
df.groupby("porte_loja")["distancia_km"].describe()

# %%
# ANCOVA Assumption Check: Independence of the Covariate and Independent Variable
# We need to verify if the covariate (Census Tract Income) shares a relationship with the Independent Variable (Retailer Size).

import statsmodels.api as sm
from statsmodels.formula.api import ols

modelo_pressuposto1 = ols("renda_setor ~ C(porte_loja)", data=df).fit()

# Display the summary of the regression
# INTERPRETATION GUIDE:
# Look at the 'Prob (F-statistic)'.
# - If p < 0.05: The assumption is VIOLATED (Income varies significantly by Store Size).
#   -> Conclusion: You cannot use ANCOVA. You should use a GLM or another approach.
print(modelo_pressuposto1.summary())

# %%
#Then, change to GLM approach 

import statsmodels.api as sm
import pandas as pd

#One-Hot Encoding for Categorical Variables
# Convert 'porte_loja' (Retailer Size) into dummy variables (0/1).
df = pd.get_dummies(df, columns=["porte_loja"], drop_first=True)

# Identify the newly created dummy columns
dummy_columns = [col for col in df.columns if "porte_loja_" in col]

# Define the Independent Variables (Predictors)
# Combining the Retailer Size dummies with the Covariate 'renda_setor' (Census Income)
independent_vars = dummy_columns + ["renda_setor"]

# Prepare the Design Matrices
X = df[independent_vars]  # Predictors
y = df["distancia_km"]    # Dependent Variable (Response)

#Check data types to ensure compatibility
print("Predictor types:\n", X.dtypes)
print("Response type:", y.dtype)

# Ensure all inputs are strictly numerical (Float)
X = X.astype(float)

# Add the Intercept (Constant)
X = sm.add_constant(X)

# Fit the Generalized Linear Model (GLM)
# Family: Gaussian (Normal) is chosen because the response variable 'distancia_km' is continuous.
# Link Function: The default link for Gaussian is 'Identity' (meaning no transformation is applied yet).
modelo_glm = sm.GLM(y, X, family=sm.families.Gaussian()).fit()

# Display the statistical summary
print(modelo_glm.summary())


# %%
###Assessing the validity of the Gaussian distribution assumption for the initial GLM.
#Formal Test: Shapiro-Wilk test.
#Visual Inspection: Q-Q plots and Histograms with Kernel Density Estimation (KDE)

import numpy as np
import statsmodels.api as sm
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Get the residuals from the fitted GLM model
# (Assuming 'modelo_glm' is your fitted model object)
residuals = modelo_glm.resid_response

# 2. Shapiro-Wilk Test for Normality
statistic, p_value = stats.shapiro(residuals)

print(f"Shapiro-Wilk Test Statistic: {statistic:.4f}")
print(f"P-value: {p_value:.4e}")  # Scientific notation for very small numbers

# 3. Decision Logic (Gaussian vs. Log Justification)
print("-" * 50)
print("CONCLUSION:")
if p_value > 0.05:
    print("The residuals appear to be normally distributed (Fail to reject H0).")
    print(">> The standard Gaussian model is adequate.")
else:
    print("The residuals do NOT appear to be normally distributed (Reject H0).")
    print(">> The standard Gaussian assumption is violated.")
    print(">> RECOMMENDATION: Apply a Logarithmic Transformation (Log-Linear Model).")
print("-" * 50)

# 4. Visualization: Q-Q Plot
plt.figure(figsize=(8, 5))
stats.probplot(residuals, dist="norm", plot=plt)
plt.title("Q-Q Plot of Residuals", fontsize=14)
plt.xlabel("Theoretical Quantiles", fontsize=12)
plt.ylabel("Ordered Values (Residuals)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig("saida/residuals_qqplot.png", dpi=300, bbox_inches="tight")
plt.show()

# 5. Visualization: Histogram with KDE
plt.figure(figsize=(8, 5))
sns.histplot(residuals, kde=True, bins=30, stat="density", color="skyblue", edgecolor="black")
plt.title("Histogram of Residuals with KDE Curve", fontsize=14)
plt.xlabel("Residuals", fontsize=12)
plt.ylabel("Density", fontsize=12)
plt.grid(True, axis='y', linestyle="--", alpha=0.6)
plt.savefig("saida/residuals_histogram.png", dpi=300, bbox_inches="tight")
plt.show()


# %%
### GLM Model (Log-Linear)
#Fit a Generalized Linear Model (GLM) using a Gaussian family with a log-transformed dependent variable to correct for non-normal residuals observed in the previous step.

import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

#Transform the dependent variable (Log-Transformation)
y_transformed = np.log(y)

#Fit the GLM Model (Log-Linear)
modelo_glm_transformado = sm.GLM(y_transformed, X, family=sm.families.Gaussian()).fit()

# Print the statistical summary to the console 
print(modelo_glm_transformado.summary())

#Save the Summary as an Image
summary_str = modelo_glm_transformado.summary().as_text()

# Create a figure to render the text
plt.figure(figsize=(10, 6))
plt.text(
    0.01, 0.05,
    summary_str,
    {"fontsize": 10},
    fontname="Monospace"  # Monospace font ensures proper table alignment
)

# Remove axes
plt.axis("off")
plt.tight_layout()

# Save the file
plt.savefig("saida/modelo_glm_transformado_summary.png", dpi=300, bbox_inches="tight")

# Close the plot to prevent it from showing up a second time in the notebook
plt.close()

# %% [markdown]
# ## Conclusion
# 
# Hypothesis 1 was not supported by the data. Contrary to the expectation that larger retailers would source products from further away, the analysis revealed that Supercenters obtain meat from significantly shorter distances than Wholesale clubs and Supermarkets.

# %% [markdown]
# ### Hypothesis 2: Larger retailers sell more ultra-processed foods
# 
# #Independent Variable (IV): Retailer size (`porte_loja`)
# #Dependent Variable (DV): Level of processing (`processamento`) - *Categories: Minimally processed, Processed, Ultra-processed*
# #Covariate: Census tract income (`renda_setor`)
# #Statistical Method: Multinomial Logistic Regression

# %%
import pandas as pd
import numpy as np # Needed for np.nan conversion

#Load the raw dataset
df = pd.read_csv("entrada/20240615_carnestotais_att.csv")

#Define critical variables required for the statistical model
critical_columns = ["porte_loja", "renda_setor", "processamento"]

#Replace explicit empty spaces (" ") in 'processamento' with NaN.
#Drop any row that is NaN in any of the critical columns.
df_processamento = (
    df.replace({"processamento": {" ": np.nan}})
    .dropna(subset=critical_columns)
    .copy()
)

#Display the prepared DataFrame and its new size
print(f"DataFrame dimensions after cleaning: {df_processamento.shape}")
df_processamento.head()

# %%
import pandas as pd
import plotly.express as px

#Setup Data 
retailer_map = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets",
}

processing_map = {
    "minimamente processado ": "Minimally processed foods",
    "processado": "Processed foods",
    "ultraprocessado": "Ultra-processed foods",
}

df_processamento["porte_loja"] = df_processamento["porte_loja"].replace(retailer_map)
df_processamento["processamento"] = df_processamento["processamento"].replace(processing_map)

# Calculate Frequencies
processing_distribution = (
    df_processamento.groupby("porte_loja")["processamento"]
    .value_counts(normalize=True)
    .unstack()
    .fillna(0)
    .stack()
    .reset_index(name="relative_frequency")
)

#Visualization Setup
custom_colors = ["#ADD8E6", "#87CEEB", "#4682B4"] # Blue Palette

fig = px.bar(
    processing_distribution,
    x="porte_loja",
    y="relative_frequency",
    color="processamento",
    barmode="group",
    title="Distribution of Processing Levels by Retailer Size (Relative Count)",
    category_orders={
        "processamento": ["Minimally processed foods", "Processed foods", "Ultra-processed foods"]
    },
    color_discrete_sequence=custom_colors,
    template="plotly_white",
    height=700,
    width=1000
)

# Refine Layout
fig.update_layout(
    font=dict(family="Arial", size=14, color="black"),
    title=dict(x=0.5),
    
    # Gap Settings
    bargap=0.3,      
    bargroupgap=0.1, 
    
    xaxis=dict(
        title="",
        showgrid=False,
        linecolor="black"
    ),
    yaxis=dict(
        title="Frequency",
        tickformat=".0%",
        showgrid=True,
        gridcolor="#E5E5E5"
    ),
    
    legend=dict(
        title="Food Processing Level",
        orientation="h",       
        yanchor="bottom",      
        y=1.02,                
        xanchor="center",      
        x=0.5,                 
        bgcolor="rgba(255, 255, 255, 0.9)",
        borderwidth=0
    ),
    
    margin=dict(t=100)
)

# Add Vertical Dividers between Retailers
retailers = processing_distribution["porte_loja"].unique()
for i in range(len(retailers) - 1):
    fig.add_shape(
        type="line",
        x0=i + 0.5, y0=0,
        x1=i + 0.5, y1=1,
        xref="x", yref="paper",
        line=dict(color="lightgrey", width=1, dash="dot")
    )

fig.show()

# %%
import pandas as pd
import plotly.express as px

# 1. Load and Clean Data
df = pd.read_csv("entrada/20240615_carnestotais_att.csv")

# Create a dedicated copy to avoid SettingWithCopyWarning
df_processamento = df.dropna(subset=["processamento", "porte_loja"]).copy()

# SAFETY FIX: Strip whitespace to ensure 'minimamente processado' matches correctly
df_processamento["processamento"] = df_processamento["processamento"].str.strip()

# 2. Translations
retailer_map = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets",
}

processing_map = {
    "minimamente processado": "Minimally processed foods", # Removed extra space key
    "processado": "Processed foods",
    "ultraprocessado": "Ultra-processed foods",
}

# Apply translations
df_processamento["porte_loja"] = df_processamento["porte_loja"].replace(retailer_map)
df_processamento["processamento"] = df_processamento["processamento"].replace(processing_map)

# 3. Calculate Absolute Counts
processing_counts = (
    df_processamento.groupby("porte_loja")["processamento"]
    .value_counts(normalize=False) 
    .unstack()
    .fillna(0)
    .stack()
    .reset_index(name="count")
)

# 4. Visualization Setup
custom_colors = ["#ADD8E6", "#87CEEB", "#4682B4"]

# Explicitly define Retailer Order (Alphabetical) to ensure lines align
retailer_order = sorted(processing_counts["porte_loja"].unique())

fig = px.bar(
    processing_counts,
    x="porte_loja",
    y="count",
    color="processamento",
    barmode="group",
    title="Distribution of Processing Levels by Retailer Size (Absolute Count)",
    # Enforce order for BOTH X-axis and Legend
    category_orders={
        "processamento": ["Minimally processed foods", "Processed foods", "Ultra-processed foods"],
        "porte_loja": retailer_order
    },
    color_discrete_sequence=custom_colors,
    template="plotly_white",
    height=700,
    width=1000
)

# 5. Refine Layout
fig.update_layout(
    font=dict(family="Arial", size=14, color="black"),
    title=dict(x=0.5),
    
    bargap=0.3,
    bargroupgap=0.1,
    
    xaxis=dict(
        title="",
        showgrid=False,
        linecolor="black"
    ),
    yaxis=dict(
        title="Count",
        tickformat="d", # 'd' ensures integers (0, 10, 20) instead of floats
        showgrid=True,
        gridcolor="#E5E5E5"
    ),
    
    # Legend
    legend=dict(
        title="Food Processing Level",
        orientation="h",       
        yanchor="bottom",      
        y=1.02,                
        xanchor="center",      
        x=0.5,                 
        bgcolor="rgba(255, 255, 255, 0.9)",
        borderwidth=0
    ),
    
    margin=dict(t=100)
)

# 6. Add Hover Template (Showing Raw Counts)
fig.update_traces(
    hovertemplate="<b>Retailer</b>: %{x}<br>" +
                  "<b>Type</b>: %{data.name}<br>" +
                  "<b>Count</b>: %{y}<extra></extra>"
)

# 7. Add Vertical Dividers
# Since we enforced 'category_orders', the loop logic is now safe
for i in range(len(retailer_order) - 1):
    fig.add_shape(
        type="line",
        x0=i + 0.5, y0=0,
        x1=i + 0.5, y1=1,
        xref="x", yref="paper",
        line=dict(color="lightgrey", width=1, dash="dot")
    )

fig.show()

# %%
# Apply Translation Mappings
df_processamento["porte_loja"] = df_processamento["porte_loja"].replace(mapping_dict)
df_processamento["processamento"] = df_processamento["processamento"].replace(mappping_processamento)

# Generate Contingency Table
# Create a cross-tabulation to observe the frequency of each processing level across retailer types
contingency_table = pd.crosstab(
    df_processamento["porte_loja"], 
    df_processamento["processamento"]
)

contingency_table.index.name = "Retailer Size"
contingency_table.columns.name = "Processing Level"

# Display the table
contingency_table

# %%
import statsmodels.api as sm
import pandas as pd

#Adjust the Covariate 'Census Tract Income' (renda_setor)
#Handle Brazilian number formatting (comma decimal) before conversion
df_processamento["renda_setor"] = df_processamento["renda_setor"].astype("str")
df_processamento["renda_setor"] = (
    df_processamento["renda_setor"]
    .str.replace(",", ".")
    .astype(float) # Final conversion to float
)

#Define the Predictor Matrix (X)
# Identify pre-existing dummy columns (from previous pd.get_dummies step)
dummy_columns = [col for col in df_processamento.columns if "porte_loja_" in col]

#Define Independent Variables: Retailer Size Dummies + Income Covariate
independent_vars = dummy_columns + ["renda_setor"]
X = df_processamento[independent_vars].astype(float) 

#Add Intercept (Constant)
X = sm.add_constant(X)

#Define the Target Variable (y)
y = df_processamento["processamento"]

# 4. Final Target Preparation
# Ensure the target variable is explicitly defined as a Pandas Categorical type.
df_processamento["processamento"] = pd.Categorical(df_processamento["processamento"])

# Update y with the categorical type
y = df_processamento["processamento"]

# Display unique categories to confirm successful definition
unique_values = y.unique()
print("Final Processing Categories:", unique_values)

# Display the prepared Design Matrix (X)
df_processamento.head()

# %%
import numpy as np
import pandas as pd
import statsmodels.api as sm

#Encode and Synchronize Variables (Final Data Prep)
#Ensure Y is numerically encoded (0, 1, 2, etc.)
if y.dtype == 'object':
    # Convert string labels to numerical codes (required for MNLogit)
    y_encoded = y.astype('category').cat.codes
else:
    # If already encoded, use the existing series
    y_encoded = y 
    
#Combine X and the encoded Y into a single temporary DataFrame
data_model = pd.concat([y_encoded.rename('y_encoded'), X], axis=1)

#Remove NaNs and Infinities in a synchronized manner (Prevents MissingDataError)
data_clean = data_model.replace([np.inf, -np.inf], np.nan).dropna(axis=0)

#Separate the FINAL clean, synchronized data matrices
y_final = data_clean['y_encoded']
X_final = data_clean.drop(columns=['y_encoded'])

#Fit the Multinomial Logit Model
try:
    print("Fitting MNLogit Model...")
    # Fit the model using the clean, synchronized data
    modelo = sm.MNLogit(y_final, X_final).fit()
    
    print(modelo.summary())

except Exception as e:
    print(f"Error fitting the model: {e}")

# %%
#CONTEXTUAL INFORMATION & INTERPRETATION 
print("\n" + "="*80)
print("             CONTEXT FOR INTERPRETING MNLOGIT SUMMARY")
print("="*80)

print("\n[Y] DEPENDENT VARIABLE (PROCESSING LEVEL):")
print("---------------------------------------")
print(" Y=0 (OMITTED/REFERENCE): Minimally processed foods (Fresh Meat)")
print(" Y=1 (PANEL 1): Processed foods (Compared to Baseline 0)")
print(" Y=2 (PANEL 2): Ultra-processed foods (Compared to Baseline 0)")

print("\n[X] INDEPENDENT VARIABLE (RETAILER SIZE):")
print("---------------------------------------")
print(" * The omitted retailer category (Reference) is: **Butcher shops**.")
print(" * All store coefficients measure the odds relative to the Butcher shops baseline.")
print("="*80)

#Print the statistical summary (the original model text output)
print(modelo.summary())

# %%
import pandas as pd
import numpy as np

# Prepare Predictor Matrix (X_VIF)
X_vif_input = df_processamento[['porte_loja', 'renda_setor']].copy()

#Generate dummy variables for retailer size, dropping the first category (reference)
X_vif = pd.get_dummies(X_vif_input, columns=['porte_loja'], drop_first=True)

#Ensure all variables are float (required for linear algebra)
X_vif = X_vif.astype(float)

# Calculate VIF Manually via Inverse Correlation Matrix
#The VIF for each predictor is the diagonal element of the inverse of the correlation matrix (R^-1).
try:
    # Calculate the correlation matrix (R)
    corr_matrix = X_vif.corr()
    
    # Invert the correlation matrix (R^-1)
    inv_corr_matrix = np.linalg.inv(corr_matrix.values)
    
    # Create the results DataFrame: VIF_i = diagonal element (i,i) of R^-1
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X_vif.columns
    vif_data["VIF"] = np.diag(inv_corr_matrix)
    
    print("--- VIF Results (Manual Calculation) ---")
    print(vif_data.sort_values(by="VIF", ascending=False))

except Exception as e:
    print(f"Calculation failed. Error: {e}")

# %% [markdown]
# ## Conclusion
# 
# The initial hypothesis that larger retailers sell more ultra-processed foods was REJECTED. Low Explanatory Power: The Pseudo R^2 of 0.009033 confirms that the variables included in the model (Retailer Size and Income) account for less than 1% of the overall variance in processing level.

# %% [markdown]
# ## Hypothesis 3 - Larger retailers display higher sanitary quality
# 
# #Independent Variable (IV): Retailer size (`porte_loja`)
# #Dependent Variable (DV): Sanitary performance (`desc_desempenho_sanitario`) - *Beef only*
# #Covariate: Census tract income (`renda_setor`)

# %%
import pandas as pd

# Load the dataset
df = pd.read_csv("entrada/20240615_carnestotais_att.csv")

# Filter the dataset to include only Beef ("Carne bovina")
carne_bovina_data = df[df["carne"] == "Carne bovina"]

# Display the filtered DataFrame
carne_bovina_data

# %%
#Standardize the Covariate 'renda_setor' (Census Income)
#Convert to string first to safely handle replace operations
carne_bovina_data["renda_setor"] = carne_bovina_data["renda_setor"].astype(str)

#Replace Brazilian comma decimal separator with dot and convert to float
carne_bovina_data["renda_setor"] = (
    carne_bovina_data["renda_setor"]
    .str.replace(",", ".")
    .astype(float)
)

#Verify data types after conversion
print("Data Types:\n", carne_bovina_data.dtypes)

#Handle Missing Data
#Define critical columns for this specific hypothesis
columns_to_check = ["est_desempenho_sanitario", "porte_loja", "renda_setor"]

#Drop rows where any of these critical variables are missing (NaN)
carne_bovina_data_clean = carne_bovina_data.dropna(subset=columns_to_check)

#Ensure Dependent Variable is Numeric
# Convert 'est_desempenho_sanitario' to numeric, coercing errors to NaN
# This ensures that the Sanitary Score (1-5) is treated as a number for the GLM
carne_bovina_data_clean["est_desempenho_sanitario"] = pd.to_numeric(
    carne_bovina_data_clean["est_desempenho_sanitario"], errors="coerce"
)

#Display the cleaned DataFrame
carne_bovina_data_clean

# %%
import matplotlib.pyplot as plt

# Translate Retailer Types to English for Reporting
# Define the mapping dictionary (if not already defined globally)
mapping_dict = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets"
}

#Apply translation to a copy of the dataframe to avoid SettingWithCopy warnings
carne_bovina_data_clean = carne_bovina_data_clean.copy()
carne_bovina_data_clean["porte_loja"] = carne_bovina_data_clean["porte_loja"].replace(mapping_dict)

#Calculate Descriptive Statistics
# Group by Retailer Size and describe the Sanitary Performance Score
result = carne_bovina_data_clean.groupby("porte_loja")["est_desempenho_sanitario"].describe()

# Display the result in the notebook
print("Descriptive Statistics for Sanitary Performance (Beef Only):")
print(result)

#Save the Descriptive Table as an Image (Publication Ready)
fig, ax = plt.subplots(figsize=(14, 5)) 
ax.axis("tight")
ax.axis("off")

#Create the table
table = ax.table(
    cellText=result.round(2).values,  
    colLabels=result.columns.str.capitalize(), #
    rowLabels=result.index,
    loc="center",
    cellLoc="center"
)

# Style the table
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 1.8)  

# Save and Show
plt.savefig("saida/descricao_est_desempenho_sanitario_translated.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#Visualizing Sanitary Performance by Retailer Size (Beef Only)

import plotly.express as px

#Translate Retailer Sizes
mapping_dict = {
    "Acougue": "Butcher shops",
    "Atacarejo/Clubes": "Wholesale clubs",
    "Conveniência": "Convenience store",
    "Hiper/Supercenter": "Supercenters",
    "Sortimento limitado": "Limited-assortment",
    "Supermercado": "Supermarkets"
}

#Apply translation to a copy to avoid warnings
carne_bovina_data_clean = carne_bovina_data_clean.copy()
carne_bovina_data_clean["porte_loja"] = carne_bovina_data_clean["porte_loja"].replace(mapping_dict)

#Prepare Data (Crosstab)
ct = pd.crosstab(
    carne_bovina_data_clean["porte_loja"],
    carne_bovina_data_clean["est_desempenho_sanitario"],
    normalize="index"
)

#Rename columns (Sanitary Scores)
sanitary_performance_labels = {
    2.0: "Poor",
    3.0: "Could be better",
    4.0: "Good",
    5.0: "Very good"
}
ct_renamed = ct.rename(columns=sanitary_performance_labels)

#Create Chart with High-Quality Base Settings
custom_colors = [
    "#ADD8E6",  # Light blue (Poor)
    "#87CEEB",  # Sky blue (Could be better)
    "#4682B4",  # Steel blue (Good)
    "#00008B"   # Dark blue (Very good)
]

fig = px.bar(
    ct_renamed,
    barmode="relative", # Stacked
    color_discrete_sequence=custom_colors,
    height=700,
    width=1000,
    template="plotly_white" # Clean white background base
)

#Enhance Visuals & Definition
fig.update_layout(
    # Typography
    font=dict(family="Arial", size=14, color="black"),

    # Titles and Labels
    xaxis_title="",
    yaxis_title="Frequency",
    legend_title="Sanitary Performance Scale",

    # Axis Formatting
    xaxis=dict(
        tickangle=45,
        tickfont=dict(size=14),
        showgrid=False,
        linecolor="black", # Solid axis line
        linewidth=1
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E0E0E0", # Very soft grey grid
        gridwidth=1,
        tickformat=".0%",    # Percentage format
        linecolor="black",   # Solid axis line
        linewidth=1,
        zeroline=False
    ),

    # Legend Styling
    legend=dict(
        x=1.02,
        y=1,
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#CCCCCC",
        borderwidth=1,
        font=dict(size=12)
    ),

    # Layout Spacing
    margin=dict(l=80, r=150, t=50, b=100), # Increased right margin for legend
    bargap=0.2, # Space between bars
)

#Add Borders to Bars (Crucial for "Crisp" look)
fig.update_traces(
    marker_line_color='white',
    marker_line_width=1.5,
    hovertemplate=(
        "<b>Store Size</b>: %{x}<br>"
        "<b>Rating</b>: %{data.name}<br>"
        "<b>Frequency</b>: %{y:.1%}<extra></extra>"
    )
)  

#Save in High Definition
# Option A: High-Res PNG (Scale 3 = 300 DPI approx)
try:
    fig.write_image("saida/descritiva_hip2_high_res.png", scale=3)
except Exception as e:
    print(f"Could not save image (check kaleido installation): {e}")

# Option B: Vector Format (Infinite resolution, best for PDF papers)
try:
    fig.write_image("saida/descritiva_hip2.svg")
except Exception as e:
    print(f"Could not save SVG: {e}")

fig.show()

# %%
import statsmodels.api as sm
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel 
import numpy as np

#Handle Dummies 
if 'porte_loja' in carne_bovina_data_clean.columns:
    carne_bovina_data_clean = pd.get_dummies(
        carne_bovina_data_clean, 
        columns=["porte_loja"], 
        drop_first=True # Keeps one category as the reference (Butcher shops)
    )
    print("Dummies created/regenerated.")
else:
    print("Dummies already exist (Skipping pd.get_dummies).")

#Prepare the predictor (X) and response (Y) variables
dummy_columns = [col for col in carne_bovina_data_clean.columns if "porte_loja_" in col]
independent_vars = dummy_columns + ["renda_setor"]

#Define X (Predictors)
X_olr = carne_bovina_data_clean[independent_vars].copy() 

#Define Y (Response): Must be integer for OLR (1, 2, 3, 4, 5)
y_olr = carne_bovina_data_clean["est_desempenho_sanitario"].astype(int)

#Ensure X is FLOAT
X_olr = X_olr.astype(float) # Ensure all predictors are float (preserves income precision)

#Fit the Ordinal Logistic Regression Model (OLR)
print("Fitting Ordinal Logistic Regression (OLR)...")
try:
    # Use distr='logit' for the Proportional Odds Model (standard OLR)
    modelo_olr = OrderedModel(y_olr, X_olr, distr='logit').fit(method='bfgs')
    
    # Display the statistical summary
    print(modelo_olr.summary())

except Exception as e:
    print(f"Error fitting OLR model: {e}")

# %%
#Preparing null model
model_null = OrderedModel(carne_bovina_data_clean['est_desempenho_sanitario'], exog=None, # No independent variables
                          distr='logit')
results_null = model_null.fit()
print(results_null.summary())

# %%
import numpy as np
import pandas as pd
import scipy.stats as stats # Required for the Chi-squared test

# Assuming 'modelo_olr' is your fitted full OLR model (Ordinal Logistic Regression)
# and 'results_null' is your fitted null OLR model from the previous step.

#Obtain Log-Likelihood values
LL = modelo_olr.llf       # Log-Likelihood of the Full Model
LL_null = results_null.llf # Log-Likelihood of the Null Model

#Calculate McFadden's Pseudo R-Squared
pseudo_r2 = 1 - (LL / LL_null)

#Calculate the Likelihood Ratio (LR) Test Statistic
# LR Test Statistic: LR = -2 * (LL_null - LL)
LR_statistic = -2 * (LL_null - LL)

#Determine Degrees of Freedom (df) for the test
df_lr = modelo_olr.df_model # Provides the correct df (number of predictors)

#Calculate the p-value using the Chi-squared distribution
# sf is the survival function (1 - CDF), giving the upper-tail probability (the p-value)
lr_p_value = stats.chi2.sf(LR_statistic, df=df_lr)

print("--- Overall Model Quality & Likelihood Ratio Test ---")
print(f"1. Log-Likelihood (LL) of Full Model: {LL:.4f}")
print(f"2. Log-Likelihood of Null Model (LL_null): {LL_null:.4f}")
print("-" * 50)
print(f"McFadden's Pseudo R-Squared: {pseudo_r2:.6f}")
print(f"LR Test Statistic (Chi²): {LR_statistic:.4f}")
print(f"Degrees of Freedom (df): {df_lr}")
print(f"LR Test P-value: {lr_p_value:.6f}") # Output from the second block

# --- Interpretation Note ---
if lr_p_value < 0.05:
    print("\nCONCLUSION: The Full Model is statistically better than the Null Model.")
else:
     print("\nCONCLUSION: The Full Model is NOT statistically better than the Null Model (LLR p > 0.05).")

if pseudo_r2 < 0.20:
    print(
        "NOTE on R²: The Pseudo R-Squared is low (<0.20), indicating limited "
        "explanatory power, even if the model is technically significant."
    )

# %% [markdown]
# ## Conclusion 
# 
# In conclusion, the hypothesis that sanitary quality uniformly improves with increasing establishment size was not broadly confirmed. Instead, the data points to a general high baseline of sanitary performance across most retailer types, with only the Supercenter category demonstrating a distinct and statistically significant advantage. The very limited explanatory power of the model (low Pseudo R2) further suggests that other, uninvestigated factors likely exert a far more dominant influence on the determination of sanitary quality within these establishments.
<<<<<<< HEAD
=======


>>>>>>> ba380f1eb7bc16a1bf35b1f5c293f3046562ffd6
