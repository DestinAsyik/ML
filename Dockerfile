# Gunakan image Python sebagai base
FROM python:3.11.4-slim

# Atur direktori kerja di container
WORKDIR /app

# Salin file requirements.txt dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek ke dalam container
COPY . .

# Ekspos port aplikasi
EXPOSE 8080

# Jalankan aplikasi dengan Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]