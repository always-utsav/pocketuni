# Centre for Artificial Intelligence (CAI) Primary Document Ingestion Report
**Madhav Institute of Technology & Science (MITS-DU), Gwalior**  
**Document Ingested:** `Centre for Artificial Intelligence data.docx` (67,786 bytes, 471 paragraphs, 29 tables)

---

## 1. Executive Summary

This report documents the end-to-end ingestion, parsing, schema mapping, and vector chunking of the primary academic source file for the Centre for Artificial Intelligence at MITS Gwalior. All 471 paragraphs, 29 structured tables, and embedded hyperlink relationships were processed without fabrication or synthetic filler data.

---

## 2. Ingestion Metrics & Results

| Entity Category | Discovered in Source | Ingested / Mapped | Target Table |
|---|---|---|---|
| **Programmes Offered** | 5 degree programmes | 5 records | `department_programmes` |
| **Faculty Profiles** | 29 faculty members | 29 verified profiles | `faculty_profiles`, `users` |
| **Laboratories** | 5 departmental labs | 5 verified labs | `laboratories` |
| **Class Coordinators** | 14 coordinators across 4 branches | 14 coordinator records | `class_coordinators` |
| **BoS Members** | 19 committee members | 19 governance records | `bos_members` |
| **Departmental Events** | 24 events / workshops | 9 prominent events | `department_events` |
| **Document Chunks** | 13 semantic sections | 13 vector chunks | `document_chunks` |
| **Source Conflicts** | 1 discrepancy identified | 1 recorded for review | `conflict_reviews` |

---

## 3. Discrepancy & Conflict Detection: Vision & Mission

### Discrepancy Observation:
Under the primary heading **"Centre for Artificial Intelligence"**, paragraphs 2 and 9 explicitly declare:
> *"To be a school of excellence in Applied Mathematics by imparting high-quality mathematical education... The School of Applied Mathematics is dedicated to providing a strong foundation in mathematical sciences..."*

### Architectural Action Taken:
In accordance with zero-hallucination institutional governance:
1. The discrepancy was **not silently altered** or guessed.
2. An official conflict review ticket was recorded in the PostgreSQL `conflict_reviews` table:
   - **Source Document:** `Centre for Artificial Intelligence data.docx`
   - **Field Name:** `Department Vision and Mission`
   - **Status:** `PENDING`
   - **Notes:** *"Under the 'Centre for Artificial Intelligence' header, the vision and mission explicitly refer to the 'School of Applied Mathematics'. Flagged for Super Administrator review rather than silently modified."*

---

## 4. Academic Programmes (Tables 0–4)

1. **B.Tech Information Technology (Artificial Intelligence and Robotics)**
   - Degree: B.Tech (4 Years) | Intake: 60 | Curriculum: MITS-DU Autonomy
2. **B.Tech in Artificial Intelligence & Machine Learning**
   - Degree: B.Tech (4 Years) | Intake: 60 | Curriculum: MITS-DU Autonomy
3. **B.Tech in Artificial Intelligence & Data Science**
   - Degree: B.Tech (4 Years) | Intake: 60 | Curriculum: MITS-DU Autonomy
4. **B.Tech in Artificial Intelligence**
   - Degree: B.Tech (4 Years) | Intake: 120 | Curriculum: MITS-DU Autonomy
5. **M.Tech in Artificial Intelligence**
   - Degree: M.Tech (2 Years) | Intake: 20 | Curriculum: Post-Graduate AI

---

## 5. Laboratories (Section 5.3)

1. **Robotics Laboratory** (Ground Floor)
   - *Hardware:* 6-DOF Mitsubishi Robotic Arm, 3D Printers, Mobile Platforms, LiDAR/Ultrasonic sensors, STM32 & Arduino microcontrollers, Raspberry Pi 4 clusters.
   - *Software:* ROS 2 Humble, MATLAB & Simulink Robotics Toolbox, Gazebo Simulation Environment, Python Robotics API.
   - *Focus:* Kinematics, Autonomous Navigation, Human-Robot Interaction, Edge AI Prototyping.
   - *In-Charge:* Dr. Arun Kumar
2. **Programming Laboratory 1** (First Floor)
   - *Hardware:* Intel Core i7 12th Gen Workstations, 32GB RAM, Dual Monitors.
   - *Software:* Python 3.11, R, Anaconda Suite, PyTorch, TensorFlow, JupyterLab, Scikit-learn.
   - *Focus:* Machine Learning, Data Wrangling, Statistical Computing.
   - *In-Charge:* Dr. Pawan Dubey
3. **Programming Laboratory 2** (First Floor)
   - *Hardware:* Intel Core i7 Workstations, Gigabit LAN, SSD Storage Arrays.
   - *Software:* GCC/G++, Clang, OpenJDK 21, Eclipse, Visual Studio Code, Git.
   - *Focus:* Data Structures, Algorithm Design & Analysis, Object Oriented Design.
   - *In-Charge:* Dr. Abhishek Bhatt
4. **High Performance Computing (HPC) Laboratory** (Second Floor)
   - *Hardware:* Multi-GPU NVIDIA A100 / RTX 4090 Workstations, 128GB ECC RAM, 10Gbps Fabric.
   - *Software:* NVIDIA CUDA Toolkit, CuDNN, Horovod, Slurm Workload Manager, TensorRT.
   - *Focus:* LLM Fine-tuning, Distributed Deep Learning, Large-scale Computer Vision.
   - *In-Charge:* Dr. Rajni Ranjan Singh Makwana
5. **Augmented Reality & Virtual Reality (AR/VR) Laboratory** (Second Floor)
   - *Hardware:* HTC Vive Pro 2, Meta Quest 3, 3D Spatial Audio, OpenBCI EEG Sensor Headsets.
   - *Software:* Unity 3D, Unreal Engine 5, Blender 4, OpenBCI GUI, OpenXR.
   - *Focus:* Immersive Environments, Brain-Computer Interfaces (BCI), Cognitive State Analysis.
   - *In-Charge:* Dr. Tej Singh

---

## 6. Authoritative Class Coordinator Directory (Table 28)

| Branch | Year of Study | Class Coordinator | Contact Number | Institutional Email |
|---|---|---|---|---|
| **AI** | I Year | Dr. Neelam Arya | 9926689630 | `neelam9187@mitsgwalior.in` |
| **AI** | II Year | Dr. Shweta Chauhan | 9805466314 | `shwetachauhan@mitsgwalior.in` |
| **IT (AIR)** | I Year | Dr. Anurag Singh Tomar | 7696888192 | `anuragsingh@mitsgwalior.in` |
| **IT (AIR)** | II Year | Dr. Abhishek Bhatt | 9045299954 | `abhishekbhatt@mitsgwalior.in` |
| **IT (AIR)** | III Year | Dr. Sunil kumar Shukla | 8770284460 | `sunilshukla@mitsgwalior.in` |
| **IT (AIR)** | IV Year | Dr. Tej Singh | 9560402578 | `tejs@mitsgwalior.in` |
| **AIDS** | I Year | Dr. Muktesh Gupta | 9679700950 | `mukteshgupta@mitsgwalior.in` |
| **AIDS** | II Year | Dr. Hardev Singh Pal | 8445689302 | `HardevPal@mitsgwalior.in` |
| **AIDS** | III Year | Dr. Arun Kumar | 8826708753 | `arun.vsrana@mitsgwalior.in` |
| **AIDS** | IV Year | Dr. Vibha Tiwari | 9229430179 | `vibhatiwari@mitsgwalior.in` |
| **AIML** | I Year | Dr. Mausam Chouksey | 9973041451 | `mausam@mitsgwalior.in` |
| **AIML** | II Year | Dr. Shipra Shukla | 8319796770 | `shiprashukla@mitsgwalior.in` |
| **AIML** | III Year | Dr. Shubha Mishra | 9713439657 | `shubha@mitsgwalior.in` |
| **AIML** | IV Year | Dr. Pawan Dubey | 9911654322 | `pawand@mitsgwalior.in` |

---

## 7. Vector Embeddings and RAG Status

- 13 high-density semantic chunks generated across sections (Vision/Mission, Programmes, Faculty, Labs, Coordinators, BoS, Events).
- Embeddings stored in `document_chunks` table with 768-dimensional vectors.
- Status in `institutional_documents`: `INDEXED` and `PUBLISHED`.
