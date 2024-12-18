import logging
import os
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from flask import (
    current_app,
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm, DataSetUpdateForm
from app.modules.dataset.models import DSDownloadRecord
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService,
    DatasetRatingService,
)
from app.modules.flamapy.services import FlamapyService
from app.modules.hubfile.services import HubfileService
from app.modules.zenodo.services import ZenodoService

logger = logging.getLogger(__name__)

flamapy_service = FlamapyService()
dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()
dataset_rating_service = DatasetRatingService()
hubfile_service = HubfileService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(
                form=form, current_user=current_user
            )
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)

        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return (
                jsonify({"Exception while create dataset data in local: ": str(exc)}),
                400,
            )
        # send dataset as deposition to Zenodo
        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            zenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            # update dataset with deposition id in Zenodo
            dataset_service.update_dsmetadata(
                dataset.ds_meta_data_id, deposition_id=deposition_id
            )

            try:
                # iterate for each feature model (one feature model = one request to Zenodo)
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                # publish deposition
                zenodo_service.publish_deposition(deposition_id)

                # update DOI
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(
                    dataset.ds_meta_data_id, dataset_doi=deposition_doi
                )
            except Exception as e:
                msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/update/check", methods=["POST"])
@login_required
def check_upload_uvl():
    # Obtener la carpeta temporal del usuario actual
    temp_folder = current_user.temp_folder()

    # En caso de que exista la carpeta temporal, se borra y se crea de nuevo
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, "check_uvl.uvl")

    try:
        # Obtener el cuerpo de la solicitud y validar que tiene "content"
        body = request.get_json()
        content = body.get("content")
        if content is None:
            return jsonify({"error": "El contenido no fue proporcionado."}), 400

        # Escribir el contenido en el archivo
        with open(file_path, "w") as f:
            f.write(content)

        # Validar el archivo con el servicio flamapy
        validation_result, status_code = flamapy_service.check_uvl(file_path)

        # Eliminar el archivo después de la validación
        os.remove(file_path)

        # Verificar el código de estado y retornar la respuesta correspondiente
        if status_code != 200:
            return jsonify(validation_result), status_code

        return jsonify({"message": "UVL check successfully"}), 200

    except Exception as e:
        # Manejar errores inesperados
        return jsonify({"error": str(e)}), 500


@dataset_bp.route("/dataset/<int:dataset_id>/upload/files", methods=["POST"])
@login_required
def upload_update_files(dataset_id):
    temp_folder = current_user.temp_folder()
    files = dataset_service.get_or_404(dataset_id).files()
    # En caso de que exista la carpeta temporal, se borra y se crea de nuevo
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    diccionario = dict()
    for file in files:
        if not file or not file.name.endswith(".uvl"):
            return (jsonify({"message": "No valid file"}), 400)
        file_path = os.path.join(temp_folder, file.name)
        if os.path.exists(file_path):
            base_name, extension = os.path.splitext(file.name)
            i = 1
            while os.path.exists(
                os.path.join(temp_folder, f"{base_name} ({i}){extension}")
            ):
                i += 1
            new_filename = f"{base_name} ({i}){extension}"
            file_path = os.path.join(temp_folder, new_filename)
        else:
            new_filename = file.name
        try:
            directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{dataset_id}/"
            parent_directory_path = os.path.dirname(current_app.root_path)

            file_path_old = os.path.join(
                parent_directory_path, directory_path, file.name
            )
            body = request.get_json()

            # Se van copiando y subiendo todos los archivos antiguos
            # En el caso del editado, se sube la nueva información
            if os.path.exists(file_path_old):
                with open(file_path_old, "r") as f2:
                    content = f2.read()
                    with open(file_path, "w") as f:
                        if str(file.id) == body.get("file_id"):
                            diccionario[file.name] = body.get("content")
                            f.write(body.get("content"))
                        else:
                            diccionario[file.name] = content
                            f.write(content)
        except Exception as e:
            return (jsonify({"message": str(e)}), 500)
    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "files": diccionario,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/update/<int:dataset_id>", methods=["GET", "POST"])
@login_required
def update_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)
    last_dataset_id = dataset.last_version_id
    if last_dataset_id is None:
        last_dataset_id = dataset_id
    form = DataSetUpdateForm()
    if request.method == "POST":
        dataset = None
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.update_from_form(
                form=form, current_user=current_user, last_dataset_id=last_dataset_id
            )

            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return (
                jsonify({"Exception while create dataset data in local: ": str(exc)}),
                400,
            )

        # send dataset as deposition to Zenodo
        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            zenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            # update dataset with deposition id in Zenodo
            dataset_service.update_dsmetadata(
                dataset.ds_meta_data_id, deposition_id=deposition_id
            )

            try:
                # iterate for each feature model (one feature model = one request to Zenodo)
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                # publish deposition
                zenodo_service.publish_deposition(deposition_id)

                # update DOI
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(
                    dataset.ds_meta_data_id, dataset_doi=deposition_doi
                )
            except Exception as e:
                msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200
    else:
        form = DataSetForm(
            title=dataset.ds_meta_data.title,
            desc=dataset.ds_meta_data.description,
            publication_type=dataset.ds_meta_data.publication_type,
            publication_doi=dataset.ds_meta_data.publication_doi,
            dataset_doi=dataset.ds_meta_data.dataset_doi,
            tags=dataset.ds_meta_data.tags,
            authors=dataset.ds_meta_data.authors,
            feature_models=dataset.feature_models,
        )
        return render_template(
            "dataset/update_dataset.html", form=form, dataset_id=dataset_id
        )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    versions = dataset.get_versions()
    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(
        render_template("dataset/view_dataset.html", dataset=dataset, versions=versions)
    )
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    versions = dataset.get_versions()
    return render_template(
        "dataset/view_dataset.html", dataset=dataset, versions=versions
    )


@dataset_bp.route("/rate_dataset/<int:dataset_id>", methods=["POST"])
@login_required
def rate_dataset(dataset_id):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON data"}), 400

    user_id = current_user.id
    rate = int(data.get("rate"))

    if rate is None:
        return jsonify({"message": "Rate is required"}), 400
    elif rate < 1 or rate > 5:
        return jsonify({"message": "Invalid rate, rate must be between 1 and 5"}), 400

    same_rate = dataset_rating_service.find_rating_by_user_and_dataset(
        user_id=user_id, dataset_id=dataset_id
    )

    if same_rate is not None:
        dataset_rating_service.update_rate(same_rate, rate)
        return jsonify({"message": "Rating updated"})
    else:
        dataset_rating_service.create(dataset_id=dataset_id, user_id=user_id, rate=rate)
        return jsonify({"message": "Rating created"})
