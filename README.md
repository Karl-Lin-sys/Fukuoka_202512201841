# TU Ilmenau CS & Automation — Portfolio Demo

A self-contained Streamlit app showcasing modules aligned with TU Ilmenau's Computer Science and Automation programme:
- AI/ML: Iris classification (Logistic Regression / Random Forest)
- Computer Vision: Preprocessing and Canny edge detection
- Robotics: A* path planning in a grid world
- Cybersecurity: Password hashing (bcrypt), JWT, and symmetric encryption (Fernet)

## Quick start (Windows)
1. Open PowerShell in the project folder.
2. Run:
   
   ```powershell
   .\run_app.ps1
   ```

This will create a virtual environment, install dependencies, and launch the app in your browser.

## Structure
- `streamlit_app.py` — Unified UI
- `modules/ml.py` — ML model training + inference on Iris
- `modules/cv.py` — Image preprocessing and edge detection
- `modules/robotics.py` — Grid generation and A* path planning
- `modules/security.py` — Hashing, JWT, and Fernet crypto

## Notes
- No external services required.
- Packages are pinned for reproducibility.
- Applying to the 104 job [AI工程師 (job no. 8vdl8)](docs/job_application_8vdl8.md?plain=1) and need a quick brief? See `docs/job_application_8vdl8.md` for a Japanese summary that maps this portfolio to the posting’s requirements.

---

## 日本語: 概要と使い方
TU Ilmenau の「Computer Science and Automation」に対応する統合デモです（Streamlit製）。以下のモジュールをまとめて体験できます。
- AI/ML（Iris分類）
- コンピュータビジョン（前処理・Cannyエッジ）
- ロボティクス（グリッド/A*経路計画）
- セキュリティ（bcrypt/JWT/Fernet）

### 実行方法（Windows）
PowerShell でプロジェクト直下を開き、次を実行してください。

```powershell
.\run_app.ps1
```

ブラウザでアプリが起動します。

応募先（AI工程師 / 104 Job No. 8vdl8）との対応付け資料は [`docs/job_application_8vdl8.md`](docs/job_application_8vdl8.md?plain=1) を参照してください。
