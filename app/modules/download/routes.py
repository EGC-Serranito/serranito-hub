from flask import render_template, request, jsonify
from app.modules.download import download_bp
from app.modules.download.services import DownloadService
from flask import send_file, abort
from datetime import datetime
import logging

download_service = DownloadService()


@download_bp.route("/download", methods=["GET"])
def index():
    return render_template("download/index.html")


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


@download_bp.route("/download/by-date", methods=["POST"])
def download_datasets_by_date():
    try:
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        if not start_date_str or not end_date_str:
            return jsonify({"error": "Both start_date and end_date are required."}), 400

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        if start_date > end_date:
            return jsonify({"error": "Start date must be before end date."}), 400

        master_zip_buffer = download_service.zip_datasets_by_date(start_date, end_date)

        if master_zip_buffer is None:
            return jsonify({"error": "No datasets found in the specified date range."}), 404

        localtime = datetime.now().strftime("%Y%m%d")
        download_filename = f"serranitohub_datasets_{localtime}.zip"

        return send_file(
            master_zip_buffer,
            as_attachment=True,
            mimetype="application/zip",
            download_name=download_filename,
        )

    except Exception as e:
        logging.error(f"Error while downloading in date range datasets: {e}")
        abort(500, description="An error occurred while downloading the datasets")
