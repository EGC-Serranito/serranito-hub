from datetime import datetime, timezone
import os
import uuid
from app.modules.flamapy.services import FlamapyService
from flask import current_app, jsonify, make_response, request, send_from_directory
from flask_login import current_user
from app.modules.hubfile import hubfile_bp
from app.modules.hubfile.models import HubfileDownloadRecord, HubfileViewRecord
from app.modules.hubfile.services import HubfileDownloadRecordService, HubfileService
from flask_login import login_required

from app import db

flamapy_service = FlamapyService()


@hubfile_bp.route("/file/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path)

    # Get the cookie from the request or generate a new one if it does not exist
    user_cookie = request.cookies.get("file_download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())

    # Check if the download record already exists for this cookie
    existing_record = HubfileDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        file_id=file_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        HubfileDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            file_id=file_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    # Save the cookie to the user's browser
    resp = make_response(
        send_from_directory(directory=file_path, path=filename, as_attachment=True)
    )
    resp.set_cookie("file_download_cookie", user_cookie)

    return resp

@hubfile_bp.route("/hubfile/upload", methods=["POST"])
@login_required
def upload_file():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # Crear carpeta temporal si no existe
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    # Ruta temporal para el archivo
    temp_file_path = os.path.join(temp_folder, file.filename)

    # Guardar temporalmente el archivo
    try:
        file.save(temp_file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    # Llamar directamente a `check_uvl` pasando la ruta temporal del archivo
    validation_result, status_code = flamapy_service.check_uvl(temp_file_path)

    if status_code != 200:
        # Si no es válido, eliminar el archivo temporal y retornar error
        os.remove(temp_file_path)
        return jsonify(validation_result), status_code

    # Si el archivo es válido, guardarlo permanentemente
    new_filename = file.filename
    return jsonify(
        {
            "message": "UVL uploaded and validated successfully",
            "filename": new_filename,
        }
    ), 200


@hubfile_bp.route('/file/view/<int:file_id>', methods=['GET'])
def view_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path, filename)

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()

            user_cookie = request.cookies.get('view_cookie')
            if not user_cookie:
                user_cookie = str(uuid.uuid4())

            # Check if the view record already exists for this cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie
            ).first()

            if not existing_record:
                # Register file view
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie
                )
                db.session.add(new_view_record)
                db.session.commit()

            # Prepare response
            response = jsonify({'success': True, 'content': content})
            if not request.cookies.get('view_cookie'):
                response = make_response(response)
                response.set_cookie('view_cookie', user_cookie, max_age=60*60*24*365*2)

            return response
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
