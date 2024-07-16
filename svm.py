import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump, load

# Function to extract MFCC features from audio file
def extract_features(file_path, mfcc_dim=13):
    try:
        # Load audio file
        audio_data, _ = librosa.load(file_path, sr=None)
        
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=len(audio_data), n_mfcc=mfcc_dim)
        
        # Flatten the data
        mfccs_flat = np.ravel(mfccs)
        
        return mfccs_flat
    
    except Exception as e:
        print(f"Error encountered while parsing {file_path}: {e}")
        return None

# Function to load data and extract features from all audio files in a directory
def load_data(directory):
    X = []
    y = []
    
    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            file_path = os.path.join(directory, filename)
            class_label = filename.split('_')[0]  # Assuming file format is "class_label_filename.wav"
            
            # Extract features
            features = extract_features(file_path)
            if features is not None:
                X.append(features)
                y.append(class_label)
    
    return np.array(X), np.array(y)

# Main function
if __name__ == "__main__":
    # Directory containing WAV files (each file should be named as "class_label_filename.wav")
    data_directory = ".."
    
    # Load data and extract features
    X, y = load_data(data_directory)
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=5)
    
    # Initialize SVM classifier
    svm_classifier = SVC(kernel='linear', random_state=5)
    
    # Train SVM classifier
    svm_classifier.fit(X_train, y_train)
    
    # Predict on test data
    y_pred = svm_classifier.predict(X_test)
    
    # Evaluate performance
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    
    # Print classification report
    print(classification_report(y_test, y_pred))

    # Save SVM model to file
    model_filename = "svm_model.joblib"
    dump(svm_classifier, model_filename)
    
    print(f"SVM model saved to {model_filename}.")