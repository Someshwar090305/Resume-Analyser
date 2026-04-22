# Resume Analyzer & Job Matcher

![Resume Analyzer](https://img.shields.io/badge/Streamlit-App-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![Groq](https://img.shields.io/badge/Groq-API-orange)

An AI-powered resume analysis tool that matches your resume against job descriptions using advanced language models. Get instant feedback on your resume's compatibility with job requirements, including skill matching, scoring, and improvement suggestions.

## ✨ Features

- **📄 Resume Upload**: Support for PDF and TXT file uploads
- **🤖 AI Analysis**: Powered by Groq's Llama 3.3 model for accurate analysis
- **🎯 Smart Matching**: Detailed skill matching and scoring (0-100)
- **💡 Improvement Suggestions**: Personalized recommendations to improve your resume
- **🎨 Modern UI**: Beautiful gradient design with dark theme
- **⚡ Fast Results**: Get analysis results in seconds

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/resume-analyzer.git
   cd resume-analyzer
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## 📖 Usage

1. **Upload Resume**: Upload a PDF or TXT file, or paste your resume text directly
2. **Enter Job Description**: Paste the job description you want to match against
3. **Analyze**: Click "🔍 Analyse Resume" to get your match score and feedback
4. **Review Results**: See your match percentage, matched/missing skills, and improvement suggestions

## 🛠️ Dependencies

- **streamlit** (>=1.30.0) - Web app framework
- **groq** (>=0.9.0) - Groq API client
- **pymupdf** (>=1.23.0) - PDF processing
- **python-dotenv** (>=1.0.0) - Environment variable management
- **requests** (>=2.28.0) - HTTP requests

## 🏗️ Project Structure

```
resume-analyzer/
├── app.py              # Main Streamlit application
├── analyzer.py         # AI analysis logic
├── pdf_reader.py       # PDF and text processing
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── .env               # Environment variables (create this)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com) and their Llama 3.3 model
- Built with [Streamlit](https://streamlit.io)
- PDF processing by [PyMuPDF](https://pymupdf.readthedocs.io/)

## 📞 Support

If you have any questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ for job seekers and recruiters**