import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from data.data_dicts import mohs_surgeons

# Create tabs
tab1, tab2, tab3 = st.tabs(["Problem Overview", "3D Visualization", "Automated Medical Transcriptions"])

# Tab 1: Problem Overview
with tab1:
    st.title("Noma")
    st.write("Authors: Abhishek Pillai, Shrey Gupta, Siddhant Agarwal")
    
    st.header("Problem Context")
    st.write("""
    During our research into the healthcare industry for this hackathon, we uncovered a significant disparity in the availability of physicians across different states in the U.S. This gap becomes even more pronounced when we look at specific specialties.
    """)
    st.image("images/Picture1.png", caption="Physician availability across different states", width=500, use_column_width=True)
    st.write("""
    For example, dermatologists, who specialize in skin treatment, are far less accessible in rural areas compared to urban centers. This shortage of specialists highlights the healthcare inequality that many regions face, which can lead to delayed treatments and increased medical risks.
    
    This led us to the issues surrounding the treatment of Melanoma, a type of skin cancer which requires the dermatologists. The treatment of melanoma requires Mohs Micrographic Surgery (MMS). With the lack of dermatologists available in rural regions, there exists a clear lack of Mohs surgeons as well.
    """)

    df_mms = pd.DataFrame(mohs_surgeons)
    locations_dermatologists = df_mms['Location'][:3]
    percentages_dermatologists = df_mms['Percentage'][:3]
    locations_surgeons_absent = df_mms['Location'][3:]
    percentages_surgeons_absent = df_mms['Percentage of Absence'][3:]
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))

    ax[0].barh(locations_dermatologists, percentages_dermatologists, color='skyblue')
    ax[0].set_xlabel('Percentage (%)')
    ax[0].set_title('Percentage of Dermatologists Performing MMS')
    ax[0].invert_yaxis()

    ax[1].barh(locations_surgeons_absent, percentages_surgeons_absent, color='salmon')
    ax[1].set_xlabel('Percentage of Absence (%)')
    ax[1].set_title('Percentage of Counties without Mohs Surgeons')
    ax[1].invert_yaxis()

    fig.tight_layout()
    plt.savefig('dermatologists_mohs_surgeons_charts.png')
    st.image('dermatologists_mohs_surgeons_charts.png', caption='Distribution of Dermatologists and Mohs Surgeons in the USA')
    
    st.subheader("Telemedicine: The Key to Fighting Healthcare Inequality")
    st.write("""
    Research strongly supports telemedicine as an effective solution for reducing healthcare disparities, particularly in underserved areas. Telemedicine allows patients to access specialists, like dermatologists, regardless of geographic location, thereby addressing the shortage of healthcare professionals in rural areas.

    This is backed by several studies:
    - A comprehensive study published by the National Institutes of Health discusses how telemedicine has improved patient outcomes in rural settings and highlights its scalability for future healthcare needs. [Read more here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9392842/).
    - Another study emphasizes the role of virtual care in reducing barriers to treatment, particularly for patients with chronic illnesses in remote locations. [Explore the study here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8430850/).
    - Deloitte’s research further demonstrates how telemedicine enhances access to medical care in rural regions by offering critical healthcare services to those who may not have access to local physicians. [Check out Deloitte's insights](https://www2.deloitte.com/us/en/insights/industry/public-sector/virtual-health-telemedicine-rural-areas.html).
    """)

    st.subheader("The Need for Automated Medical Transcriptions")

    st.write("""
    Accurate and timely documentation is crucial in healthcare, but manual transcription during surgery is time-consuming and prone to errors.

    1. **Time Constraints:** Surgeons often don't have time for detailed documentation during procedures.
    2. **Error Identification:** Without precise records, it’s harder to spot medical or surgical errors.
    """)

    st.header("The Solution")

    st.write("""
    We have built a software that allows enhanced communication between surgeons and consultants during Moh's surgery for Melanoma. 
    Our project offers two key features:
    1. **Real-time 3D Visualization:** We provide a live 3D visualization of the patient's face during surgery, allowing consultants to make precise incisions and receive real-time updates throughout the procedure.

    2. **Automated Medical Transcriptions:** Our system generates highly accurate medical transcriptions from live surgical feeds, automating documentation and enabling detailed analysis of medical and surgical errors.
    """)

# Tab 2: 3D Visualization
with tab2:
    st.header("Generating 3D visualization of patient's face")

    st.write("""
    **Key Techniques in 3D Reconstruction:**
    
    1. **Gaussian Splatting**: A method that represents points in 2D images as Gaussian curves. These overlapping curves generate smooth 3D reconstructions, making it useful for visualizing surgical areas.
    2. **NeRF (Neural Radiance Fields)**: A deep learning technique used to generate 3D scenes by learning how light interacts with objects in the images.
    3. **Point Cloud Generation**: 3D points are generated from 2D image pixels, where pixel intensity (from RGB values) determines the depth, forming the z-axis of the 3D points.
    4. **Sampling Rate**: Used to control the granularity of the 3D point cloud, ensuring accurate reconstruction by selecting pixels at intervals.
    5. **Incision Simulation**: Incisions were achieved by detecting ray intersections between the mouse pointer and 3D model, creating dynamic lines based on user input.
    6. **Annotations**: 3D incisions are mapped to 2D annotations by projecting 3D points onto the 2D canvas, allowing users to see the surgical cuts in both 3D and 2D views.
    """)

    # Display the images
    st.image("images/3d_visualization.png", caption="3D Point Cloud Visualization of Surgical Area", use_column_width=True)
    st.image("images/incision_annotations.png", caption="Annotations of Incisions Mapped from 3D to 2D", use_column_width=True)

    # Data for the table
    data = {
        'Method': ['NeRF', 'Gaussian Splatting', 'Instant Splat'],
        'Inference Time (h)': [2.5, 1.75, 0.75],
        'Rendering Quality (1-10)': [7, 8, 8]
    }

    # Create a dataframe
    df = pd.DataFrame(data)

    # Display the table
    st.subheader("Comparison of 3D Reconstruction Methods")
    st.write("The table below highlights the key performance metrics of the methods we tested:")
    st.dataframe(df)

    st.header("Rendering the 3D visualizations")


# Tab 3: Automated Medical Transcriptions
with tab3:
    st.header("Automated Medical Transcriptions")
    
    st.subheader("Tools and Methods Used in the Pipeline")
    st.write("""
    We utilized several tools and methods to create real-time, accurate medical transcriptions:
    
    ### Tools:
    1. **LITA (Language-Image Transformer Agent):** Real-time, spatio-temporal transcription from video feeds.
    2. **AWS Transcribe:** For speaker diarization (identifying speakers) and transcription of the surgery's audio.
    3. **Neo4j with GraphRAG:** Knowledge graph construction and real-time updates.
    
    ### Method:
    1. **Time-Stamped Transcription:** We generate time-stamped descriptions from the video feed to document each action during the surgery.
    2. **Speaker Diarization:** AWS Transcribe detects and separates different speakers in the surgical audio.
    3. **Knowledge Graph Construction:** Neo4j constructs a knowledge graph that maps relationships between entities (surgeons, tools, patients).
    """)

    st.subheader("Pipeline Diagram")
    
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with labels
    G.add_node("Video Feed", label="Video Feed")
    G.add_node("LITA Transcription", label="LITA Transcription")
    G.add_node("AWS Transcribe", label="AWS Transcribe")
    G.add_node("Speaker Diarization", label="Speaker Diarization")
    G.add_node("Knowledge Graph (Neo4j)", label="Knowledge Graph (Neo4j)")
    G.add_node("GraphRAG Updates", label="GraphRAG Updates")

    # Add edges
    G.add_edges_from([
        ("Video Feed", "LITA Transcription"),
        ("Video Feed", "AWS Transcribe"),
        ("AWS Transcribe", "Speaker Diarization"),
        ("LITA Transcription", "Knowledge Graph (Neo4j)"),
        ("Speaker Diarization", "Knowledge Graph (Neo4j)"),
        ("Knowledge Graph (Neo4j)", "GraphRAG Updates"),
    ])

    # Set custom positions to flow top-down
    pos = {
        "Video Feed": (0.5, 1.0),
        "LITA Transcription": (0.3, 0.7),
        "AWS Transcribe": (0.7, 0.7),
        "Speaker Diarization": (0.7, 0.4),
        "Knowledge Graph (Neo4j)": (0.5, 0.4),
        "GraphRAG Updates": (0.5, 0.1)
    }

    # Plot the diagram with better aesthetics
    plt.figure(figsize=(10, 6))

    # Draw nodes with distinct colors and larger sizes
    nx.draw_networkx_nodes(G, pos, node_color=['#ff9999', '#66b3ff', '#66b3ff', '#99ff99', '#ffcc99', '#ffcc99'], 
                           node_size=4000, alpha=0.9, edgecolors='black')

    # Draw edges with arrowheads and line thickness
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray', width=2.5)

    # Draw node labels with font adjustments
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', font_color='black')

    # Set title for the diagram
    plt.title("Real-Time Surgical Transcription Pipeline", fontsize=16, fontweight='bold')

    # Show the plot in Streamlit
    st.pyplot(plt)

    # Load the HTML file
    with open("transcript_34.html", "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    # Display the HTML file
    st.components.v1.html(html_content, height=600)