from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Define new documents to add
# Your list of individual strings
new_texts = [
    """| **Log Message**  | **Field Name(s)**                                   | **Potential Anomalies**                                                    |
| ---------------- | --------------------------------------------------- | -------------------------------------------------------------------------- |
| `ATT` (Attitude) | `Roll`, `Pitch`, `Yaw`                              | Unusual or sudden changes in orientation, oscillations, instability        |
| `GPS`            | `Lat`, `Lng`, `Alt`, `HDop`, `NSats`, `Vel`         | GPS drift, low satellite count, poor HDOP, sudden velocity jumps           |
| `IMU`            | `GyrX`, `GyrY`, `GyrZ`, `AccX`, `AccY`, `AccZ`      | Spikes or drift in acceleration/gyros suggesting vibration or sensor fault |
| `BARO`           | `Alt`, `Press`, `Temp`                              | Sudden pressure drops, inconsistent altitude compared to GPS               |
| `CTUN`           | `Alt`, `ThrOut`, `NavRoll`, `NavPitch`, `NavYaw`    | Unexpected throttle outputs, altitude errors, poor navigation response     |
| `NTUN`           | `DesVelX`, `VelX`, `DesVelY`, `VelY`, `DAlt`, `Alt` | Large error between desired and actual velocities/altitude                 |
| `MODE`           | `Mode`                                              | Rapid or unexpected mode changes (e.g., Auto to RTL), manual overrides     |
| `EV` (Events)    | `Id`, `TimeUS`                                      | Warnings/errors like EKF fails, failsafes, fence breaches                  |
| `EKF` / `NKF`    | `PosErr`, `VelErr`, `HorizPos`, `VertPos`           | High estimation errors, indicating EKF divergence or GPS faults            |
| `ERR`            | `Subsys`, `ECode`                                   | Logged internal errors like compass, GPS, baro, or failsafe triggers       |
| `POWR`           | `Vcc`, `Curr`, `CurrTot`                            | Voltage drops, overcurrent, power brownouts                                |
| `RCIN`           | `C1` to `C8`                                        | Irregular or lost RC signal input                                          |
| `RCOU`           | `C1` to `C8`                                        | Abnormal output values to motors/servos                                    |
| `MAG`            | `MagX`, `MagY`, `MagZ`, `OfsX`, `OfsY`, `OfsZ`      | Magnetometer interference, high offsets                                    |
| `VIBE`           | `VibeX`, `VibeY`, `VibeZ`, `Clip0-2`                | Excessive vibration levels, IMU clipping                                   |
""",
]
new_docs = [Document(page_content=txt) for txt in new_texts]

# Load existing store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    "rag_vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

# Add new documents
vectorstore.add_documents(new_docs)

# Save updated store
vectorstore.save_local("rag_vector_store")
print("✅ Appended new documents to vector store.")
