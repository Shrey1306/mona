import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

st.set_option('deprecation.showPyplotGlobalUse', False)

clean_environmental_dataset = '../data/cleaned_environmental_dataset_no_duplicates.csv'
# st.image("./seed_logo.png", width=100)
st.title("Seed: Returns Meet Responsibility")
st.write("Authors: Unnathi Kumar, Adhira Choudhury, Abhishek Pillai, Neil Goyal")
st.write("")

st.header("More About Our Dataset")
st.write("We used the [HBS Corporate Environmental Impact dataset](https://opennetzero.org/dataset/iwa-corporate-environmental-impact-data-supplement) and the [As You Sow Invest Your Values Company Screen dataset](https://www.asyousow.org/) in our study.")
st.write("The HBS dataset contains historical (2010-2019) sustainability data for 1665 companies globally. It reports the firm's industry, performance on several environmental factors (working capacity, fish production capacity, crop production capacity, meat production capacity, biodiversity, abiotic resources, water production capacity, wood production capacity), and performance on 17 environment-focused UN Sustainable Development Goals (SDG) targets. The dataset also reports “% imputed”, quantifying a company's environmental impact.")
st.write("The As You Sow dataset reports on screening criteria focused on environmental, social, and governance (ESG) aspects, including involvement in fossil fuels, coal mining, controversial weapons, and tobacco, among others, for 6557 companies globally. It provides “Yes” or “No” (binary) answers to questions like whether the company was identified in a coal screen, a controversial weapons screen, a gun retailers screen, a gender equality screen, etc. The dataset also provides corresponding tickers with the company name to facilitate identification on the stock exchange.")

# Data Preprocessing
st.header("Data Preprocessing")
st.write("To ensure that this dataset fit our needs, we went through several stages of preprocessing. First, since our project focuses on the US Stock Market, we omitted all companies outside of the US from the dataset. This resulted in 245 companies present in the US in the dataset. Then, since our project does not have a focus on historical performance, we only retained dataset entries from 2019 and removed the “Year” column. We also removed columns that were irrelevant to the task of evaluating environmental impact, which included the production capacities and individual environmental intensities. Then, we normalised the dataset so that all relevant factors in the dataset would be represented as comparable indices. Since some dataset entires were negative, we normalised the dataset by adding the absolute value of the minimum value entry to all entries in the column and dividing by the maximum value entry in the column. Further, since the company names in the HBS dataset did not have corresponding tickers, we performed fuzzy matching of the company names against companies in the NASDAQ dataset to account for minor differences in names and abbreviations. Fuzzy matching leveraged Levenshtein distance, which involved calculating similarity scores between names and selecting the closest matches based on a 0.85 threshold. To be able to run a clustering algorithm on the data, we performed multi-hot encoding on the company name and industries.")
st.write("The As Your Sow dataset was pruned to 1,678 US entries from an initial 6,377 by ommiting all entries with Non United States stock data to remain consistent with the U.S. stock market. The financial metrics of beta and market cap were appended to each entry through Yahoo Finance API calls. Fuzzy matching, using Levenshtein distance, resolved discrepancies in the Tickers column which provided a list of tickers rather than the one used in the US market by matching company names from the dataset and NASDAQ dataset to get the correct ticker for each entry. Additionally, the dataset contains 32 attributes which provide insights into the ESG status of the stock's company. For instance, attributes include details like identifying companies use of fossil fuels, support of deforestation, production of certain products, and support of certain laws and policies.")
st.write("Combining these datasets entailed matching entities by ticker values, appending entries absent in one dataset with zero values for missing metrics, and applying hot encoding to both industry and company names, facilitating subsequent analytical endeavors. This process underscored the datasets' readiness for environmental impact analysis within the US stock market context, leveraging pandas for data manipulation and CSV files for intermediate storage.  Incorporating the provided details into the analytical framework, the preprocessing and integration of the HBS Corporate Environmental Impact and As Your Sow datasets resulted in a comprehensive dataset with 1,824 entries, representing companies, and 62 attributes, covering a wide range of ESG indicators and financial metrics. ")

# SDG Analysis
st.header("Analysis on SDG (Sustainable Development Goals) Performance")
st.write("First, we conducted an analysis on the relationships between the different SDG metrics from the HBS dataset.")
data = pd.read_csv(clean_environmental_dataset)

sdg_columns = [col for col in data.columns if col.startswith('SDG')]
sdg_data = data[sdg_columns]
correlation_matrix = sdg_data.corr()
fig = plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation between Different SDG Metrics')
st.pyplot(fig)
st.write('The heatmap above provides some interesting insights. We find that there are a variety of relations within SDG performance, ranging from strongly positively correlated to strongly negatively correlated. For example, SDG 1.5 has a very high correlation with SDG 2.1, 2.2, 2.3, and 2.4 (all 0.99), which means that companies focusing on building resilience to disasters (SDG 1.5) also have a strong focus on eliminating hunger (since SDG 2 is “zero hunger”).')
st.write('On the contrary, we also find that SDG 14.1 has a strong negative correlation with SDG 3.4 (-0.96) and SDG 3.3 (-0.96), which means that companies focusing on reducing marine pollution (SDG 14.1), generally, do not fight diseases and promote mental health (SDGs 3.3 and 3.4). While this correlation seems unexpected, it is an observed tradeoff that companies should be mindful of and work towards mitigating. SDG 15.1 and SDG 15.2 are perfectly negatively correlated with SDG 14.1 and SDG 14.c, which suggests a tradeoff between conserving life on land versus life on water for companies.')
st.write('Some moderate correlations are also present in the heatmap. For example, SDG 3.4 shows very little to no linear correlation with SDG 6 (-0.09). so companies focusing on reducing mortality from non-communicable diseases are not necessarily focused on clean water and sanitation.')

# Industry Analysis
st.header("Industry Analysis")
st.write("We plotted the environmental index in the most common industries (corresponding to more than 5 companies in our dataset) to find trends in environmental indices and assess distribution across sectors.")
data['Industry (Exiobase)'] = data['Industry (Exiobase)'].str.replace('\(\d+\)', '', regex=True) \
                                                                 .str.replace('\d+', '', regex=True) \
                                                                 .str.strip()  # Remove leading/trailing spaces

industry_counts = data['Industry (Exiobase)'].value_counts()

industries_more_than_10 = industry_counts[industry_counts > 5].index
data_filtered = data[data['Industry (Exiobase)'].isin(industries_more_than_10)]
data_filtered_reset_index = data_filtered.reset_index()

sns.set(style="whitegrid")

fig2 = plt.figure(figsize=(10, 8))
s2 = sns.scatterplot(x='Industry (Exiobase)', y='Environmental Index', data=data_filtered_reset_index, hue="Industry (Exiobase)", legend=False)

s2.set(xticklabels=[])
plt.title('Environmental Index across Different Industries')
plt.xlabel('Industry')
plt.ylabel('Environmental Index')
plt.tight_layout() 

st.pyplot(fig2)
# st.image('./company_legend.png')
st.write("With respect to the environmental performance of different industries, we found that generally, companies in the air transport, construction, extraction of crude petroleum, and retail trade spaces have low environmental indices, whereas companies in the research and development and computer spaces have high environmental indices. On the other hand, there is considerable variance in environmental indices in fields like financial intermediation and chemicals. With that, this highlights the need for companies in certain spaces to identify gaps in their methodologies and employ sustainable remedies.")

# Environmental Index vs. Environmental Factors
st.header("Environmental Index vs. Environmental Factors")
st.markdown("#### Biodiversity")

fig3 = plt.figure(figsize=(14, 10))
sns.scatterplot(x='Biodiversity', y='Environmental Index', data=data_filtered, alpha = 0.7, s=100)
plt.title('Environmental Index as a Function of Biodiversity', fontsize=16)
plt.xlabel('Biodiversity', fontsize=14)
plt.ylabel('Environmental Index', fontsize=14)
plt.tight_layout()
st.pyplot(fig3)

st.markdown("#### Abiotic Resources")
fig4 = plt.figure(figsize=(14, 10))

data_filtered2 = data_filtered[data_filtered['Abiotic Resources'] >= 0.98]
sns.scatterplot(x='Abiotic Resources', y='Environmental Index', data=data_filtered2, alpha = 0.7, s=100)
plt.title('Environmental Index as a Function of Abiotic Resources', fontsize=16)
plt.xlabel('Abiotic Resources', fontsize=14)
plt.ylabel('Environmental Index', fontsize=14)
plt.tight_layout()
st.pyplot(fig4)

#New data visualization for company breakdown into causes:

file_path_market_cap = '../data/cleaned_market_cap_values.csv'
data_market_cap = pd.read_csv(file_path_market_cap)

def plot1(data_market_cap):
    labels = ['Weapons Free Funds: Nuclear weapons screen',
              'Weapons Free Funds: Military contractors screen',
              'Gun Free Funds: Gun manufacturers screen',
              'Gun Free Funds: Gun retailers screen']
    label_counts = data_market_cap[labels].astype(bool).sum(axis=0)
    counts = label_counts.values
    bar_labels = ['Nuclear weapons screen', 'Military contractors screen', 'Gun manufacturers screen', 'Gun retailers screen']
    bar_colors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange']

    fig, ax = plt.subplots()
    ax.bar(bar_labels, counts, color=bar_colors)
    ax.set_ylabel('Number of Companies')
    ax.set_title('Companies Providing Weapons & Military Support')
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')
    return fig

# Plot 2
def plot2(data_market_cap):
    labels = ['Fossil Free Funds: Coal screen',
              'Fossil Free Funds: Oil / gas screen',
              'Fossil Free Funds: Fossil-fired utility screen']
    label_counts = data_market_cap[labels].astype(bool).sum(axis=0)
    counts = label_counts.values
    bar_labels = ['Coal screen', 'Oil / gas screen', 'Fossil-fired utility screen']
    bar_colors = ['tab:red', 'tab:blue', 'tab:green']

    fig, ax = plt.subplots()
    ax.bar(bar_labels, counts, color=bar_colors)
    ax.set_ylabel('Number of Companies')
    ax.set_title('Companies with Dependencies on Non-Renewable Energy')
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')
    return fig

# Plot 3
def plot3(data_market_cap):
    labels = [
        'Deforestation Free Funds: Producer screen',
        'Deforestation Free Funds: Financier screen',
        'Deforestation Free Funds: Consumer brand screen'
    ]
    label_counts = data_market_cap[labels].astype(bool).sum(axis=0)
    counts = label_counts.values
    bar_labels = ['Producer screen', 'Banks and lenders screen', 'Major consumer brands screen']
    bar_colors = ['tab:red', 'tab:blue', 'tab:green']

    fig, ax = plt.subplots()
    ax.bar(bar_labels, counts, color=bar_colors)
    ax.set_ylabel('Number of Companies')
    ax.set_title('Companies with Deforestation Supporting Operations')
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')
    return fig

# Plot 4
def plot4(data_market_cap):
    labels = ['Deforestation Free Funds: Palm oil producer screen',
              'Deforestation Free Funds: Palm oil consumer brand screen',
              'Deforestation Free Funds: Paper / pulp producer screen',
              'Deforestation Free Funds: Paper / pulp consumer brand screen',
              'Deforestation Free Funds: Rubber producer screen',
              'Deforestation Free Funds: Rubber consumer brand screen',
              'Deforestation Free Funds: Timber producer screen',
              'Deforestation Free Funds: Timber consumer brand screen',
              'Deforestation Free Funds: Cattle producer screen',
              'Deforestation Free Funds: Cattle consumer brand screen',
              'Deforestation Free Funds: Soy producer screen',
              'Deforestation Free Funds: Soy consumer brand screen']
    label_counts = data_market_cap[labels].astype(bool).sum(axis=0)
    counts = label_counts.values
    bar_labels = ['Palm oil producer screen', 'Palm oil consumer brand screen', 'Paper / pulp producer screen', 
                  'Paper / pulp consumer brand screen', 'Rubber producer screen', 'Rubber consumer brand screen', 
                  'Timber producer screen', 'Timber consumer brand screen', 'Cattle producer screen', 
                  'Cattle consumer brand screen', 'Soy producer screen', 'Soy consumer brand screen']

    fig, ax = plt.subplots()
    ax.bar(bar_labels, counts)
    ax.set_ylabel('Number of Companies')
    ax.set_title('Retailers of Consumer Goods Related to Deforestation')
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')
    return fig

# Load data
clean_market_dataset = '../data/cleaned_market_cap_values.csv'
data_market_cap = pd.read_csv(clean_market_dataset)

# Display the plots in Streamlit
st.header("Analysis of Companies with Ethical Concerns")

st.subheader("Companies Providing Weapons & Military Support")
fig1 = plot1(data_market_cap)
st.pyplot(fig1)

st.subheader("Companies with Dependencies on Non-Renewable Energy")
fig2 = plot2(data_market_cap)
st.pyplot(fig2)

st.subheader("Companies with Deforestation Supporting Operations")
fig3 = plot3(data_market_cap)
st.pyplot(fig3)

st.subheader("Retailers of Consumer Goods Related to Deforestation")
fig4 = plot4(data_market_cap)
st.pyplot(fig4)

# Function to generate 2D PCA plot
def plot_2d_pca(features_for_pca, cluster_labels):
    pca_2d = PCA(n_components=2)
    X_pca_2d = pca_2d.fit_transform(features_for_pca)

    plt.figure(figsize=(10, 8))
    plt.scatter(X_pca_2d[:, 0], X_pca_2d[:, 1], c=cluster_labels, cmap='viridis', marker='o', alpha=0.7, edgecolor='k')
    plt.title('Clusters Visualized in PCA-Reduced 2D Space')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.colorbar(label='Cluster Label')
    st.pyplot()

# Function to generate 3D PCA plot
def plot_3d_pca(features_for_pca, cluster_labels):
    pca_3d = PCA(n_components=3)
    X_pca_3d = pca_3d.fit_transform(features_for_pca)

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2], 
                         c=cluster_labels, cmap='viridis', marker='o', alpha=0.7, edgecolor='k')

    ax.set_title('Clusters Visualized in PCA-Reduced 3D Space')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.set_zlabel('Principal Component 3')

    cbar = plt.colorbar(scatter, ax=ax, pad=0.1)
    cbar.set_label('Cluster Label')

    st.pyplot()

st.title('Clustering Analysis with PCA Visualization')

# Read data
clean_df = pd.read_csv('../Clustering-Hierarcal/clusters_added_clean_data_revised.csv')
features_for_pca = clean_df.drop(columns=['Cluster_Labels', 'Company_Name', 'Ticker', 'Company_Name_Encoded', 'Industry_Encoded'])
cluster_labels = clean_df['Cluster_Labels']

st.header('2D PCA Visualization')
plot_2d_pca(features_for_pca, cluster_labels)
st.header('3D PCA Visualization')
plot_3d_pca(features_for_pca, cluster_labels)