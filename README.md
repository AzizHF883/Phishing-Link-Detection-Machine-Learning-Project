# **URL Feature Extraction and Phishing Detection**  

This project focuses on extracting detailed features from URLs and utilizing machine learning models to classify them as either *phishing* or *general URLs*. It is designed to ensure robust feature extraction and accurate classification through pre-trained models.  

---

## **Project Purpose**  
Phishing attacks are a significant threat in cybersecurity, often targeting unsuspecting users through malicious URLs. This project aims to:  
1. **Extract URL Features**: Analyze various components of a given URL (e.g., length, subdomain structure, WHOIS data).  
2. **Predict Maliciousness**: Use machine learning models to classify whether the URL is phishing or benign.  

---

## **How It Works**  

### **Stage 1: Feature Extraction**  
The script extracts **48 features** from a given URL, including:  
- **Basic URL Attributes**: Length, number of special characters, presence of keywords.  
- **WHOIS Information**: Domain registration age, expiration date, and more.  
- **Domain and Path Analysis**: Subdomain structure, keywords in path, and brand names.  
- **External Favicon**: Checks if the favicon is hosted on an external domain.  

### **Stage 2: Model Predictions**  
1. Pre-trained machine learning models are loaded, including:  
   - Random Forest  
   - Gradient Boosting  
   - XGBoost  
   - AdaBoost  
   - Decision Tree  
2. The extracted features are passed into the models for prediction.  
3. The output indicates whether the URL is phishing or a general URL.  

---

## **Installation**  

### **Dependencies**  
Ensure the following libraries are installed in your Python environment:  
```bash
pip install requirements.txt
```

### **Files Required**  
1. `model_generator.py`: It Generates the model  trained based on the given dataset, also evaluates each of them. I have kept it for detailed information about them.
2. `brand.csv`: A CSV file containing brand names for keyword checks.
3. `app.py`: Main Python script for feature extraction and predictions.  
4. Pre-trained model files:  
   - `Random_Forest_model.pkl`  
   - `Gradient_Boosting_model.pkl`  
   - `XGBoost_model.pkl`  
   - `AdaBoost_model.pkl`  
   - `Decision_Tree_model.pkl`  

---

## **Usage**  

### **Running the Code**  
1. Open the script in your Python environment (e.g., local IDE or command-line execution).  
2. Provide a URL as input:  
   - For command-line execution: Use `app.py <url>` to pass the URL.  (this feature is commented out for easy testing, you can uncomment the indicated lines for desired features.
   - For local IDE: Enter the URL in the input prompt.  

3. The script will:  
   - Extract features from the URL.  
   - Use the models to classify the URL as phishing or benign.  

### **Output**  
- The extracted features are displayed as a dataframe.  
- Predictions from all five models are printed, indicating whether the URL is **Phishing** or a **General URL**.  

---

## **Purpose and Benefits**  
- **Proactive Security**: Quickly identify and flag potentially malicious URLs.  
- **Comprehensive Analysis**: Extract detailed URL attributes for deeper insights.  
- **Model Agnostic**: Can integrate additional models for better performance.  

---


---

Feel free to contribute or suggest improvements to make this tool even more effective!  

--- 

Let me know if you'd like additional customization or sections added!
