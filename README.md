## Handson-L10-Spark-Streaming-MachineLearning-MLlib

## **Overview**

This repository contains a real-time analytics pipeline for a ride-sharing platform using Apache Spark Structured Streaming and MLlib. The pipeline performs:

Task 4: Real-Time Fare Prediction
Predicts the fare for each incoming ride based on its distance using a pre-trained Linear Regression model.
Detects anomalies by calculating deviation between actual fare and predicted fare.

Task 5: Time-Based Fare Trend Prediction
Aggregates streaming ride data into 5-minute windows.
Predicts the average fare for the upcoming window based on time features (hour and minute of day).

---

## **Repository Structure**
```
├── task4.py      # Task 4: Real-Time Fare Prediction
├── task5.py      # Task 5: Time-Based Fare Trend Prediction
├── data_generator.csv          # Static CSV used for model training
├── models/                       # Folder where trained models are saved
│   ├── fare_model/
│   └── fare_trend_model_v2/
└── README.md                     # Project documentation
```

---

## **Prerequisites**
Before starting the assignment, ensure you have the following software installed and properly configured on your machine:
1. **Python 3.x**:
   - [Download and Install Python](https://www.python.org/downloads/)
   - Verify installation:
     ```bash
     python3 --version
     ```

2. **PySpark**:
   - Install using `pip`:
     ```bash
     pip install pyspark
     ```

3. **Faker**:
   - Install using `pip`:
     ```bash
     pip install faker
     ```

---

### **Running the Analysis Tasks**

You can run the analysis tasks either locally.

1. **Execute Each Task **: The data_generator.py should be continuosly running on a terminal. open a new terminal to execute each of the tasks.
   ```bash
     python data_generator.py
   ```
   ```
     spark-submit task4.py
   ```
   ```
     spark-submit task5.py
   ```

---

### ** Approach**

## Task 4

Load training data from training-dataset.csv.
Cast numerical columns (distance_km, fare_amount) to DoubleType.
Use VectorAssembler to create features.
Train LinearRegression model to predict fare.
Save the model to models/fare_model.

Stream live rides from socket:
Transform streaming data into features.
Predict fare and calculate deviation.
Output results to console in append mode.

--- 

## Task 5

Load training data and cast timestamp.
Aggregate historical data into 5-minute windows to compute avg_fare.

Create time-based features:
hour_of_day
minute_of_hour

Train LinearRegression on these features.
Save the model to models/fare_trend_model_v2.
Stream live rides and aggregate into sliding 5-minute windows.
Transform into features and predict average fare for each window.
Output results to console in append mode.

--- 

## **Outputs**

**Task 4**
```
-------------------------------------------
Batch: 1
-------------------------------------------
+------------------------------------+---------+-----------+-----------+-----------------+-----------------+
|trip_id                             |driver_id|distance_km|fare_amount|predicted_fare   |deviation        |
+------------------------------------+---------+-----------+-----------+-----------------+-----------------+
|5ebe769b-fe3c-4837-ba9e-f8cbe46b0284|70       |44.75      |39.87      |87.14927414829461|47.27927414829461|
+------------------------------------+---------+-----------+-----------+-----------------+-----------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+------------------------------------+---------+-----------+-----------+-----------------+------------------+
|trip_id                             |driver_id|distance_km|fare_amount|predicted_fare   |deviation         |
+------------------------------------+---------+-----------+-----------+-----------------+------------------+
|b132606e-db07-4233-a265-9b0a669d9fa2|88       |15.09      |118.68     |94.44011900407794|24.239880995922064|
+------------------------------------+---------+-----------+-----------+-----------------+------------------+

```

**Task 5**

```
-------------------------------------------
Batch: 16
-------------------------------------------
+-------------------+-------------------+----------------+-----------------------+
|window_start       |window_end         |avg_fare        |predicted_next_avg_fare|
+-------------------+-------------------+----------------+-----------------------+
|2025-10-21 16:00:00|2025-10-21 16:05:00|76.3965306122449|92.39431034482759      |
+-------------------+-------------------+----------------+-----------------------+

-------------------------------------------
Batch: 24
-------------------------------------------
+-------------------+-------------------+-----------------+-----------------------+
|window_start       |window_end         |avg_fare         |predicted_next_avg_fare|
+-------------------+-------------------+-----------------+-----------------------+
|2025-10-21 16:01:00|2025-10-21 16:06:00|80.19385321100917|92.39431034482759      |
+-------------------+-------------------+-----------------+-----------------------+

```

---




