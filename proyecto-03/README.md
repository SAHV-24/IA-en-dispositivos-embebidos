# Fruit and Vegetable Classifier with AI on Raspberry Pi

Real-time fruit and vegetable classification system using TensorFlow Lite on Raspberry Pi 4. The project captures images via camera, performs deep learning inference, and controls servomotors and DC motors based on classification results.

## Authors

- **Sergio Herrera**
- **Natalia Moreno**
- **Valentina Bueno**

## Features

- 6-class classification: Beetroot, Cauliflower, Orange, Pear, Pineapple, Watermelon
- Real-time inference with TensorFlow Lite
- Hardware control (servomotors and DC motor)
- MobileNetV2 architecture (~95% validation accuracy)

## Hardware Requirements

- Raspberry Pi 4 (4GB+ recommended)
- Camera (Raspberry Pi or USB compatible)
- 2x Servo motors (0-270°)
- 1x DC motor
- Push button
- External power supply

### GPIO Connections

| Component | GPIO Pin |
|-----------|----------|
| Button | 27 |
| Servo 1 | 18 |
| Servo 2 | 23 |
| DC Motor | 17 |

## Quick Start

### 1. Clone repository

```bash
git clone https://github.com/SAHV-24/IA-en-dispositivos-embebidos.git
cd IA-en-dispositivos-embebidos/proyecto-03
```

### 2. Setup environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Enable camera (Raspberry Pi)

```bash
sudo raspi-config
# Interface Options -> Camera -> Enable
sudo reboot
```

### 4. Run classification system

```bash
python src/piloto.py
```

## Project Structure

```
proyecto-03/
├── data/                   # Training and validation data
├── models/                 # Trained TFLite models
├── notebooks/              # Jupyter notebooks for training
├── src/                    # Python source code
│   └── piloto.py          # Main inference script
├── outputs/                # Captured images and results
├── docs/                   # Additional documentation (papers)
└── requirements.txt        # Project dependencies
```

## Model Information

- **Architecture**: MobileNetV2 (Transfer Learning)
- **Input size**: 224x224x3
- **Output**: 6 classes
- **Framework**: TensorFlow Lite
- **Accuracy**: ~95% validation

## Workflow

1. User presses button
2. Image is captured and resized to 224x224
3. TensorFlow Lite performs inference
4. Servomotors move according to predicted class
5. DC motor activates for 5 seconds
6. Servomotors return to initial position

## Training

Open the training notebook:

```bash
jupyter notebook notebooks/training.ipynb
```

Follow the instructions to train with your own data.

## Troubleshooting

**Camera not working:**
```bash
vcgencmd get_camera
ls -l /dev/video*
```

**GPIO errors:**
```bash
sudo usermod -a -G gpio $USER
```

**Model not found:**
Ensure `project_model.tflite` is in `models/` directory.

## References

- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [MobileNetV2 Paper](https://arxiv.org/abs/1801.04381)
- Dataset: [Kaggle Fruits and Vegetables](https://www.kaggle.com/datasets/nataliamorenomontoya/fruits-and-vegetables-dataset-2)
