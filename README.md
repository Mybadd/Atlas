# AtlasDraw - STEP to 2D Illustration Generator

A web application that takes 3D STEP files and automatically generates stylized 2D illustrations (PNG/JPEG).

## Tech Stack
- **Backend:** Python 3.10+, Flask
- **3D Processing:** CadQuery (pythonOCC)
- **2D Rendering:** svglib, ReportLab
- **Image Processing:** Pillow (PIL)
- **Frontend:** HTML, CSS, JavaScript

## How to Run

1. **Install Conda** (required for CadQuery installation on Windows).
2. **Setup Environment:**
   ```bash
   conda create -n step2img python=3.10
   conda activate step2img
   conda install -c cadquery -c conda-forge cadquery
   pip install flask flask-cors Pillow svglib reportlab
   ```
3. **Run the App:**
   ```bash
   conda activate step2img
   python app.py
   ```
4. **Open in Browser:** 
   Navigate to [http://localhost:5000](http://localhost:5000)
