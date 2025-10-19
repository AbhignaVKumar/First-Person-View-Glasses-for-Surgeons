# First_Person_View_Glasses_for_Surgeons
Lightweight Smart FPV Glasses powered by Edge ML on Arduino Nicla Vision. Implements a TinyML speech recognition model and real-time Wi-Fi video streaming for hands-free surgical assistance and remote visualization

---

## 🩺 Motivation

In February 2024, **Dr. Senthilvelan**, an arthroscopic surgeon specializing in shoulder, elbow, and wrist procedures, sought a solution to **record and stream live video** from the surgery room for **training and reference**.  
Existing solutions were **bulky and expensive**, limiting accessibility in clinical setups.

This inspired the development of a **lightweight, affordable, and intelligent pair of FPV (First Person View) glasses** that allow surgeons to stream and record live video from their own perspective, without interrupting their workflow.

---

## 🧠 Concept Overview

The **FPV glasses system** is built into a regular spectacle frame form factor and is powered by **Arduino Nicla Vision**, an embedded board featuring:

- **STM32H747AII6 Dual ARM® Cortex® M7/M4**
- **2 MP camera sensor**
- **Microphone**
- **On-board Wi-Fi connectivity**
- **Compact form factor (23 mm × 23 mm)** - fits seamlessly on the nose bridge

This setup enables **real-time wireless video streaming** and **speech-controlled operation**, making it an effective hands-free solution for surgical environments.

---

## 🖼️ Preliminary Design

<p align="center">
  <img src="images/fpv_glasses_front.jpg" alt="FPV Smart Glasses Front View" width="500"/>
  <br/>
  <em>Figure 1: Early design prototype using Nicla Vision mounted on the nose bridge.</em>
</p>

<p align="center">
  <img src="images/fpv_glasses_side.jpg" alt="FPV Smart Glasses Side View" width="500"/>
  <br/>
  <em>Figure 2: Side view showing compact integration of electronics and cable routing.</em>
</p>

<p align="center">
  🎥 <b>Watch the video stream captured from the device:</b>  
  <a href="videos/fpv_stream_demo.mp4">FPV Stream Demo Video</a>
</p>

---

## ⚙️ Hardware Architecture

| Component | Description |
|------------|-------------|
| **Main Processor** | ARM Cortex-M7 + M4 (Dual Core) |
| **Camera** | 2 MP OV7675 integrated with Nicla Vision |
| **Wireless Interface** | Wi-Fi 2.4 GHz |
| **Power Source** | Rechargeable Li-Po or Power Bank |
| **Battery Capacity Tested** | 500 mAh (3 hrs), 5000 mAh (10+ hrs) |
| **Frame Material** | Lightweight spectacle frame with 3D printed battery mount |
| **Controls** | Integrated slide switch for stream ON/OFF (Before speech control) |

---

## 💻 Software Design and Implementation

- Developed firmware to **stream live video over Wi-Fi** using multiple protocols like **UDP**, **HTTP**, and **RTSP**
- Integrated **TinyML speech recognition model (71 KB)** on the **Cortex-M7** to identify `"resume"` and `"pause"` commands  
- Commands are sent via **Remote Procedure Call (RPC)** to the **Cortex-M4**, which controls the camera stream accordingly
- Achieved **37 ms inference time** for command recognition
- Supported **sub-200 ms latency** for video streaming across multiple clients via **WebRTC**

---

## 🔋 Battery Integration and Enhancements

In this design, the battery is seamlessly integrated into the spectacle frame and rests comfortably at the back of the head using a 3D-printed holder. A 5000 mAh power bank provides ample energy, is easily rechargeable via USB, and enables the FPV glasses to stream continuously for over 10 hours. An integrated slide switch allows users to turn the video streaming on and off(initial design, later with speech recognition), while a spring-loaded screw lets them adjust the camera angle for optimal comfort and viewing.

<p align="center">
  <img src="images/fpv_battery_mount.jpg" alt="Battery Mount Integration" width="500"/>
  <br/>
  <em>Figure 3: Battery integrated into the frame using a 3D-printed holder.</em>
</p>

<p align="center">
  <img src="images/fpv_final_design.jpg" alt="Final FPV Smart Glasses Design" width="500"/>
  <br/>
  <em>Figure 4: Final design prototype — fully integrated FPV smart glasses with Edge ML control.</em>
</p>

---

## 🧩 System Flow

```text
+---------------------+        +------------------+        +----------------------+
|  Cortex-M7 (AI Core)| -----> | RPC Communication| -----> |  Cortex-M4 (Stream)  |
| Speech Recognition  |        |  Inter-core Msgs |        |  Video Control Logic |
+---------------------+        +------------------+        +----------------------+
                                                                       |
                                                                       v
                                                              +----------------+
                                                              |  Wi-Fi Module  |
                                                              |  (UDP/RTSP)    |
                                                              +----------------+
                                                                       |
                                                                       v
                                                            +-------------------+
                                                            |   Web Client(s)   |
                                                            |  Live Stream View |
                                                            +-------------------+


