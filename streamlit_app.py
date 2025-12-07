import json
import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

from modules.ml import (
    train_iris_model, get_iris_data, predict_iris, 
    perform_clustering, perform_dimensionality_reduction, 
    hyperparameter_tuning, get_wine_data, generate_synthetic_data
)
from modules.cv import preprocess_image, canny_edges
from modules.robotics import generate_grid, a_star, visualize_grid_path
from modules.security import (
    hash_password,
    verify_password,
    generate_jwt,
    decode_jwt,
    generate_fernet_key,
    encrypt_text,
    decrypt_text,
)
from modules.automation import SmartFactory, IIoTSimulator, create_production_dashboard
from modules.data_science import DataGenerator, DataAnalyzer, BigDataProcessor, create_visualization_data
from modules.advanced_robotics import create_robotics_demo, SwarmRobotics, Environment

st.set_page_config(page_title="CS & Automation Portfolio", page_icon="🤖", layout="wide")


def page_ml():
    st.header("Advanced AI/ML: Research-Oriented Machine Learning")
    
    # Dataset selection
    col1, col2, col3 = st.columns(3)
    with col1:
        dataset = st.selectbox("Dataset", ["iris", "wine", "synthetic"])
    with col2:
        model_name = st.selectbox("Model", ["Logistic Regression", "Random Forest", "Gradient Boosting", "AdaBoost", "SVM", "Neural Network"])
    with col3:
        test_size = st.slider("Test size", 0.1, 0.5, 0.2, 0.05)
    
    random_state = st.number_input("Random seed", min_value=0, max_value=9999, value=42, step=1)

    if st.button("Train model"):
        model, metrics = train_iris_model(model_name, test_size, int(random_state), dataset)
        st.session_state["ml_model"] = model
        st.session_state["ml_metrics"] = metrics
        st.success(f"Trained {model_name} on {dataset} dataset")

    if "ml_metrics" in st.session_state:
        metrics = st.session_state["ml_metrics"]
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Test accuracy", f"{metrics['accuracy']:.3f}")
        with col2:
            st.metric("CV Mean", f"{metrics['cv_mean']:.3f}")
        with col3:
            st.metric("CV Std", f"{metrics['cv_std']:.3f}")
        with col4:
            st.metric("OEE", f"{metrics['accuracy'] * 0.9:.3f}")  # Simulated OEE
        
        # Classification report
        with st.expander("Classification Report"):
            st.text(metrics["classification_report"])
        
        # Feature importance
        if metrics["feature_importance"] is not None:
            with st.expander("Feature Importance"):
                importance_df = pd.DataFrame({
                    'feature': metrics["feature_names"],
                    'importance': metrics["feature_importance"]
                }).sort_values('importance', ascending=False)
                st.bar_chart(importance_df.set_index('feature'))
        
        # Prediction interface
        X, y, feature_names, target_names = get_iris_data() if dataset == "iris" else get_wine_data() if dataset == "wine" else generate_synthetic_data()
        defaults = X.mean(axis=0)
        
        with st.form("ml_predict"):
            st.subheader("Make Prediction")
            cols = st.columns(len(feature_names))
            inputs = []
            for i, (name, default) in enumerate(zip(feature_names, defaults)):
                if i < len(cols):
                    val = cols[i].number_input(name, value=float(default), step=0.1, format="%.2f")
                    inputs.append(val)
            
            submitted = st.form_submit_button("Predict")
            if submitted:
                model = st.session_state.get("ml_model")
                if model is None:
                    st.warning("Train a model first.")
                else:
                    idx, prob_map = predict_iris(model, np.array(inputs))
                    label = target_names[idx]
                    st.success(f"Prediction: {label}")
                    ordered = [prob_map.get(i, 0.0) for i in range(len(target_names))]
                    st.bar_chart({name: ordered[i] for i, name in enumerate(target_names)})
    
    # Advanced ML features
    st.subheader("Advanced ML Features")
    tab1, tab2, tab3 = st.tabs(["Clustering", "Dimensionality Reduction", "Hyperparameter Tuning"])
    
    with tab1:
        clustering_dataset = st.selectbox("Clustering Dataset", ["iris", "wine", "synthetic"])
        n_clusters = st.slider("Number of clusters", 2, 8, 3)
        
        if st.button("Run Clustering"):
            if clustering_dataset == "iris":
                X, _, _, _ = get_iris_data()
            elif clustering_dataset == "wine":
                X, _, _, _ = get_wine_data()
            else:
                X, _, _, _ = generate_synthetic_data()
            
            labels, clusterer = perform_clustering(X, "kmeans", n_clusters)
            
            # Visualize clusters
            if X.shape[1] >= 2:
                fig, ax = plt.subplots()
                scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis')
                ax.set_xlabel('Feature 1')
                ax.set_ylabel('Feature 2')
                ax.set_title('K-means Clustering')
                plt.colorbar(scatter)
                st.pyplot(fig)
    
    with tab2:
        reduction_dataset = st.selectbox("Reduction Dataset", ["iris", "wine", "synthetic"])
        method = st.selectbox("Method", ["pca", "tsne"])
        
        if st.button("Run Dimensionality Reduction"):
            if reduction_dataset == "iris":
                X, y, feature_names, target_names = get_iris_data()
            elif reduction_dataset == "wine":
                X, y, feature_names, target_names = get_wine_data()
            else:
                X, y, feature_names, target_names = generate_synthetic_data()
            
            X_reduced, reducer = perform_dimensionality_reduction(X, method, 2)
            
            # Visualize reduced data
            fig, ax = plt.subplots()
            scatter = ax.scatter(X_reduced[:, 0], X_reduced[:, 1], c=y, cmap='viridis')
            ax.set_xlabel(f'{method.upper()} Component 1')
            ax.set_ylabel(f'{method.upper()} Component 2')
            ax.set_title(f'{method.upper()} Visualization')
            plt.colorbar(scatter)
            st.pyplot(fig)
    
    with tab3:
        tuning_model = st.selectbox("Model for Tuning", ["Random Forest", "SVM", "Neural Network"])
        
        if st.button("Run Hyperparameter Tuning"):
            if dataset == "iris":
                X, y, _, _ = get_iris_data()
            elif dataset == "wine":
                X, y, _, _ = get_wine_data()
            else:
                X, y, _, _ = generate_synthetic_data()
            
            best_model, best_params = hyperparameter_tuning(tuning_model, X, y)
            
            st.json(best_params)
            st.success(f"Best parameters found for {tuning_model}")


def page_cv():
    st.header("Computer Vision: Image Processing and Edges")
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        width = st.slider("Width", 64, 1024, 256, 16)
    with col2:
        height = st.slider("Height", 64, 1024, 256, 16)
    with col3:
        blur = st.select_slider("Blur (kernel)", options=[1, 3, 5, 7], value=3)
    with col4:
        low = st.slider("Canny low", 0, 255, 100, 5)
    high = st.slider("Canny high", 0, 255, 200, 5)

    if uploaded is not None:
        img = Image.open(uploaded)
        proc = preprocess_image(img, width=width, height=height, blur_ksize=blur, grayscale=False)
        edges = canny_edges(
            img, width=width, height=height, blur_ksize=blur, low_threshold=low, high_threshold=high
        )
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Preprocessed")
            st.image(proc, caption=f"{width}x{height}, blur={blur}")
        with c2:
            st.subheader("Edges")
            st.image(edges, clamp=True)


def page_robotics():
    st.header("Robotics: A* Path Planning on a Grid")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        rows = st.slider("Rows", 10, 100, 25, 1)
    with c2:
        cols = st.slider("Cols", 10, 100, 25, 1)
    with c3:
        obstacle_prob = st.slider("Obstacle density", 0.0, 0.6, 0.2, 0.01)
    with c4:
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=42, step=1)

    grid = generate_grid(rows, cols, obstacle_prob=float(obstacle_prob), seed=int(seed))
    st.caption("White=free, Black=obstacle")
    st.image(255 - (grid * 255), clamp=True, width=300)

    c5, c6 = st.columns(2)
    with c5:
        start_r = st.number_input("Start row", 0, rows - 1, 0, 1)
        start_c = st.number_input("Start col", 0, cols - 1, 0, 1)
    with c6:
        goal_r = st.number_input("Goal row", 0, rows - 1, rows - 1, 1)
        goal_c = st.number_input("Goal col", 0, cols - 1, cols - 1, 1)

    start = (int(start_r), int(start_c))
    goal = (int(goal_r), int(goal_c))
    path = a_star(grid, start, goal)
    fig = visualize_grid_path(grid, path, start, goal)
    st.pyplot(fig, use_container_width=True)

    if path:
        st.success(f"Path length: {len(path) - 1} steps")
    else:
        st.error("No path found. Try a lower obstacle density or different start/goal.")


def page_security():
    st.header("Cybersecurity: Hashing, JWT, and Symmetric Encryption")
    tab1, tab2, tab3 = st.tabs(["Password Hashing", "JWT", "Fernet"])

    with tab1:
        pwd = st.text_input("Password to hash", type="password")
        if st.button("Hash password"):
            if not pwd:
                st.warning("Enter a password")
            else:
                st.session_state["hashed_pwd"] = hash_password(pwd)
        hashed_val = st.session_state.get("hashed_pwd", "")
        st.text_area("Hashed (bcrypt)", hashed_val, height=80)
        verify = st.text_input("Verify against hash", type="password", key="verify_pwd")
        if st.button("Check password"):
            if not hashed_val:
                st.warning("Hash a password first.")
            else:
                ok = verify_password(verify, hashed_val)
                st.write("Match" if ok else "No match")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            payload_str = st.text_area("Payload JSON", value='{"user":"alice","role":"researcher"}', height=120)
            secret = st.text_input("Secret key", value="change_me")
            exp = st.slider("Expires (minutes)", 1, 120, 15, 1)
            if st.button("Generate JWT"):
                try:
                    payload = json.loads(payload_str)
                    token = generate_jwt(payload, secret, exp)
                    st.text_area("JWT", token, height=120)
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            token_in = st.text_area("JWT to decode", height=120, key="jwt_in")
            secret_in = st.text_input("Secret for decoding", value="change_me", key="jwt_secret_in")
            if st.button("Decode JWT"):
                try:
                    data = decode_jwt(token_in, secret_in)
                    st.json(data)
                except Exception as e:
                    st.error(f"Decode error: {e}")

    with tab3:
        key = st.text_input("Fernet key (base64, 32-byte)", value=st.session_state.get("fernet_key", ""))
        if st.button("Generate new key"):
            new_key = generate_fernet_key()
            st.session_state["fernet_key"] = new_key
            st.success("Generated new key")
            st.text_input("Fernet key (base64, 32-byte)", value=new_key, key="fernet_key_display")

        plaintext = st.text_area("Plaintext", "Hello TU Ilmenau!")
        if st.button("Encrypt"):
            try:
                if not key:
                    st.warning("Provide a key")
                else:
                    token = encrypt_text(plaintext, key)
                    st.text_area("Ciphertext (token)", token, height=120)
            except Exception as e:
                st.error(f"Encrypt error: {e}")

        token_in = st.text_area("Ciphertext to decrypt", height=120, key="fernet_token_in")
        if st.button("Decrypt"):
            try:
                if not key:
                    st.warning("Provide a key")
                else:
                    text = decrypt_text(token_in, key)
                    st.text_area("Decrypted text", text, height=120)
            except Exception as e:
                st.error(f"Decrypt error: {e}")


def page_automation():
    st.header("Industry 4.0: Smart Factory & Automation")
    
    # Smart Factory Simulation
    st.subheader("Smart Factory Simulation")
    col1, col2, col3 = st.columns(3)
    with col1:
        n_processes = st.slider("Number of Processes", 5, 20, 10)
    with col2:
        simulation_hours = st.slider("Simulation Hours", 1, 72, 24)
    with col3:
        quality_threshold = st.slider("Quality Threshold", 0.8, 0.99, 0.95)
    
    if st.button("Run Smart Factory Simulation"):
        factory = SmartFactory(n_processes)
        factory.quality_threshold = quality_threshold
        processes = factory.generate_process_data(simulation_hours)
        
        # Calculate metrics
        oee = factory.calculate_oee()
        anomalies = factory.detect_anomalies()
        maintenance_scores = factory.predictive_maintenance()
        dashboard = create_production_dashboard(factory)
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall OEE", f"{oee:.3f}")
        with col2:
            st.metric("Anomalies Detected", len(anomalies))
        with col3:
            st.metric("Avg Energy Cost", f"€{dashboard['summary']['total_energy_consumption'] * 0.15:.2f}")
        with col4:
            st.metric("Quality Yield", f"{dashboard['quality_metrics']['first_pass_yield']:.3f}")
        
        # Production dashboard
        with st.expander("Production Dashboard"):
            st.json(dashboard)
        
        # Maintenance priorities
        if maintenance_scores:
            st.subheader("Predictive Maintenance Priorities")
            maintenance_df = pd.DataFrame(
                list(maintenance_scores.items()),
                columns=['Process', 'Risk Score']
            ).sort_values('Risk Score', ascending=False)
            st.bar_chart(maintenance_df.set_index('Process'))
    
    # IIoT Simulation
    st.subheader("IIoT Sensor Network")
    col1, col2, col3 = st.columns(3)
    with col1:
        n_sensors = st.slider("Number of Sensors", 10, 100, 20)
    with col2:
        duration = st.slider("Duration (minutes)", 30, 240, 60)
    with col3:
        sensor_types = st.multiselect("Sensor Types", ["temperature", "vibration", "pressure", "flow_rate"], default=["temperature", "vibration"])
    
    if st.button("Run IIoT Simulation"):
        iiot_sim = IIoTSimulator()
        
        # Add sensors
        for i in range(n_sensors):
            sensor_type = random.choice(sensor_types)
            location = f"Zone_{i % 5 + 1}"
            iiot_sim.add_sensor(f"Sensor_{i:03d}", sensor_type, location)
        
        # Generate data
        sensor_data = iiot_sim.generate_sensor_data(duration)
        analysis = iiot_sim.analyze_sensor_patterns()
        
        # Display results
        st.success(f"Generated {len(sensor_data)} sensor readings")
        
        # Sensor analysis
        with st.expander("Sensor Pattern Analysis"):
            for sensor_id, metrics in analysis.items():
                st.write(f"**{sensor_id}**: Mean={metrics['mean']:.2f}, Std={metrics['std']:.2f}, Anomalies={metrics['anomalies']}")
        
        # Time series visualization
        if sensor_data:
            df = pd.DataFrame(sensor_data)
            if not df.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                for sensor_type in sensor_types:
                    type_data = df[df['sensor_type'] == sensor_type]
                    if not type_data.empty:
                        ax.plot(type_data['timestamp'], type_data['value'], label=sensor_type, alpha=0.7)
                ax.set_xlabel('Time')
                ax.set_ylabel('Sensor Value')
                ax.set_title('IIoT Sensor Readings Over Time')
                ax.legend()
                plt.xticks(rotation=45)
                st.pyplot(fig)


def page_data_science():
    st.header("Data Science & Big Data Analytics")
    
    # Data generation
    st.subheader("Data Generation & Processing")
    data_type = st.selectbox("Data Type", ["IoT Sensor Data", "Manufacturing Data"])
    n_samples = st.slider("Number of Records", 1000, 50000, 10000)
    
    if st.button("Generate & Analyze Data"):
        if data_type == "IoT Sensor Data":
            data = DataGenerator.generate_iot_data(n_samples)
        else:
            data = DataGenerator.generate_manufacturing_data(n_samples)
        
        st.success(f"Generated {len(data)} records")
        
        # Data analysis
        analyzer = DataAnalyzer(data)
        stats = analyzer.basic_statistics()
        
        # Display basic statistics
        with st.expander("Basic Statistics"):
            st.json(stats)
        
        # Correlation analysis
        corr_analysis = analyzer.correlation_analysis()
        if "correlation_matrix" in corr_analysis:
            with st.expander("Correlation Analysis"):
                corr_df = pd.DataFrame(corr_analysis["correlation_matrix"])
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, ax=ax)
                ax.set_title('Correlation Matrix')
                st.pyplot(fig)
        
        # Clustering analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            with st.expander("Clustering Analysis"):
                features = st.multiselect("Select Features for Clustering", numeric_cols, default=numeric_cols[:3])
                n_clusters = st.slider("Number of Clusters", 2, 8, 3)
                
                if st.button("Run Clustering"):
                    if len(features) >= 2:
                        cluster_results = analyzer.clustering_analysis(features, n_clusters)
                        if "silhouette_score" in cluster_results:
                            st.metric("Silhouette Score", f"{cluster_results['silhouette_score']:.3f}")
                            st.json(cluster_results["cluster_analysis"])
        
        # Anomaly detection
        if len(numeric_cols) >= 2:
            with st.expander("Anomaly Detection"):
                anomaly_features = st.multiselect("Select Features for Anomaly Detection", numeric_cols, default=numeric_cols[:2])
                contamination = st.slider("Contamination Rate", 0.01, 0.2, 0.1)
                
                if st.button("Detect Anomalies"):
                    if len(anomaly_features) >= 2:
                        anomaly_results = analyzer.anomaly_detection(anomaly_features, contamination)
                        if "anomalies_detected" in anomaly_results:
                            st.metric("Anomalies Detected", anomaly_results["anomalies_detected"])
                            st.metric("Anomaly Rate", f"{anomaly_results['anomaly_rate']:.3f}")
        
        # Big data processing simulation
        st.subheader("Big Data Processing Simulation")
        processor = BigDataProcessor()
        
        # Stream processing
        with st.expander("Stream Processing"):
            stream_data = DataGenerator.generate_iot_data(1000)
            stream_results = processor.process_streaming_data(stream_data.to_dict('records'))
            st.json(stream_results)
        
        # Data quality assessment
        quality_report = processor.data_quality_assessment(data)
        with st.expander("Data Quality Report"):
            st.metric("Overall Quality Score", f"{quality_report['overall_quality_score']:.2f}%")
            st.json(quality_report["completeness"])


def page_advanced_robotics():
    st.header("Advanced Robotics & Cognitive Computing")
    
    # Robotics demo
    st.subheader("Cognitive Robotics Simulation")
    col1, col2, col3 = st.columns(3)
    with col1:
        n_robots = st.slider("Number of Robots", 2, 10, 5)
    with col2:
        n_obstacles = st.slider("Number of Obstacles", 5, 20, 8)
    with col3:
        simulation_steps = st.slider("Simulation Steps", 50, 200, 100)
    
    if st.button("Run Robotics Simulation"):
        # Create robotics demo
        demo = create_robotics_demo()
        
        # Extract key metrics
        final_metrics = demo["final_metrics"]
        
        # Display swarm metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Swarm Size", final_metrics["swarm_size"])
        with col2:
            st.metric("Cohesion", f"{final_metrics['cohesion']:.3f}")
        with col3:
            st.metric("Dispersion", f"{final_metrics['dispersion']:.2f}")
        with col4:
            st.metric("Coverage", f"{final_metrics['coverage']:.3f}")
        
        # Environment visualization
        with st.expander("Environment Setup"):
            env_data = demo["environment"]
            st.write(f"Environment: {env_data['width']}x{env_data['height']} meters")
            st.write(f"Objects: {len(env_data['objects'])}")
            
            # Simple visualization
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Plot obstacles
            for obj in env_data['objects']:
                if obj['type'] == 'obstacle':
                    rect = plt.Rectangle((obj['x']-obj['width']/2, obj['y']-obj['height']/2), 
                                       obj['width'], obj['height'], color='red', alpha=0.5)
                    ax.add_patch(rect)
                elif obj['type'] == 'target':
                    circle = plt.Circle((obj['x'], obj['y']), 0.3, color='green', alpha=0.7)
                    ax.add_patch(circle)
                elif obj['type'] == 'hazard':
                    circle = plt.Circle((obj['x'], obj['y']), 0.5, color='orange', alpha=0.7)
                    ax.add_patch(circle)
            
            # Plot robot trajectories
            colors = plt.cm.tab10(np.linspace(0, 1, len(demo['robot_trajectories'])))
            for i, trajectory in enumerate(demo['robot_trajectories']):
                if trajectory:
                    x_coords = [pos[0] for pos in trajectory]
                    y_coords = [pos[1] for pos in trajectory]
                    ax.plot(x_coords, y_coords, color=colors[i], alpha=0.7, label=f'Robot {i+1}')
                    # Mark final position
                    ax.plot(x_coords[-1], y_coords[-1], 'o', color=colors[i], markersize=8)
            
            ax.set_xlim(0, env_data['width'])
            ax.set_ylim(0, env_data['height'])
            ax.set_xlabel('X Position (m)')
            ax.set_ylabel('Y Position (m)')
            ax.set_title('Robot Swarm Trajectories')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            st.pyplot(fig)
        
        # Cognitive architecture explanation
        st.subheader("Cognitive Architecture Components")
        st.write("""
        The robots use a three-layer cognitive architecture:
        - **Perception Layer**: Processes sensor data to detect obstacles, targets, and hazards
        - **Decision Layer**: Applies rule-based decision making with priority handling
        - **Action Layer**: Executes motor commands based on decisions
        - **Memory System**: Stores spatial maps and recent experiences
        """)
        
        # Simulation timeline
        if demo["simulation_results"]:
            with st.expander("Simulation Timeline"):
                timeline_data = demo["simulation_results"][-10:]  # Last 10 steps
                for step in timeline_data:
                    st.write(f"Step {step['step']}: Time={step['time']:.1f}s, "
                           f"Centroid=({step['swarm_metrics']['centroid'][0]:.1f}, "
                           f"{step['swarm_metrics']['centroid'][1]:.1f})")


def main():
    st.title("Computer Science and Automation — Portfolio Demo")
    st.caption("Ilmenau University of Technology themed demo: AI/ML, CV, Robotics, Cybersecurity")
    choice = st.sidebar.radio("Module", [
        "AI/ML", "Computer Vision", "Robotics", "Cybersecurity", 
        "Automation 4.0", "Data Science", "Advanced Robotics"
    ])
    if choice == "AI/ML":
        page_ml()
    elif choice == "Computer Vision":
        page_cv()
    elif choice == "Robotics":
        page_robotics()
    elif choice == "Cybersecurity":
        page_security()
    elif choice == "Automation 4.0":
        page_automation()
    elif choice == "Data Science":
        page_data_science()
    elif choice == "Advanced Robotics":
        page_advanced_robotics()


if __name__ == "__main__":
    main()
