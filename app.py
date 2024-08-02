from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
from datetime import timedelta
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['Get' , 'POST'])
def upload_form():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            output_file_path = process_file(file_path)
            return send_file(output_file_path, as_attachment=True)
    print("Get method called")
    return render_template('upload.html')

def process_file(file_path):
    encoding_used = 'latin1'
    data = pd.read_csv(file_path, encoding=encoding_used)

    data['OccurTime'] = pd.to_datetime(data['OccurTime'])

    threshold = timedelta(minutes=4)
    combined_data = []

    i = 0
    while i < len(data):
        current_row = data.iloc[i]
        j = i + 1
        combined = current_row.copy()

        while j < len(data):
            next_row = data.iloc[j]
            if next_row['OccurTime'] - current_row['OccurTime'] <= threshold and next_row['ErrNo'] == current_row['ErrNo']:
                combined['OccurTime'] = next_row['OccurTime']
                j += 1
            else:
                break

        combined_data.append(combined)
        i = j

    combined_df = pd.DataFrame(combined_data)
    output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'combined_errors.csv')
    combined_df.to_csv(output_file_path, index=False)
    return output_file_path

if __name__ == "__main__":
    app.run(debug=True)
