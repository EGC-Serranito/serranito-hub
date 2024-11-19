from flask import render_template
from app.modules.download import download_bp
from app.modules.download.services import DownloadService
from flask import send_file, abort
from datetime import datetime
import logging

download_service = DownloadService()

@download_bp.route('/download', methods=['GET'])
def index():
    return render_template('download/index.html')

@download_bp.route("/download/all", methods=["GET"])
def download_all_datasets():

    try:
        # Create a zip buffer with all datasets
        master_zip_buffer = download_service.zip_all_datasets()

        # Generate a unique filename for the download
        localtime = datetime.now().strftime("%Y%m%d")
        download_filename = f"serranitohub_datasets_{localtime}.zip"

        # Return the zip buffer as a file download
        return send_file(
            master_zip_buffer,
            as_attachment=True,
            mimetype="application/zip",
            download_name=download_filename,
        )

    except Exception as e:
        logging.error(f"Error while downloading all datasets: {e}")
        abort(500, description="An error occurred while downloading the datasets")


