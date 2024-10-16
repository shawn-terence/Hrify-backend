# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port your app runs on
EXPOSE 8080

# Command to run your app
# Command to run your app using uvicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]


